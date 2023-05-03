import partitura as pt  
import mido
import numpy as np
import time
import threading
import multiprocessing
from collections import defaultdict
import partitura as pt


class MidiInputThread(threading.Thread):
    def __init__(
        self,
        port,
        queue,
        init_time=None,
        pipeline=None,
        return_midi_messages=False,
    ):
        threading.Thread.__init__(self)

        self.midi_in = port
        self.init_time = init_time
        self.listen = False
        self.queue = queue
        self.first_msg = False
        self.pipeline = pipeline
        self.return_midi_messages = return_midi_messages

    def run(self):
        self.start_listening()
        while self.listen:
            msg = self.midi_in.poll()
            if msg is not None:
                c_time = self.current_time
                output = self.pipeline(msg, c_time)
                if self.return_midi_messages:
                    self.queue.put(((msg, c_time), output))
                else:
                    self.queue.put(output)

    @property
    def current_time(self):
        """
        Get current time since starting to listen
        """
        return time.time() - self.init_time

    def start_listening(self):
        """
        Start listening to midi input (open input port and
        get starting time)
        """
        self.listen = True
        if self.init_time is None:
            self.init_time = time.time()

    def stop_listening(self):
        """
        Stop listening to MIDI input
        """
        # break while loop in self.run
        self.listen = False
        # reset init time
        self.init_time = None


def midi_msg_to_pt_note(msg):
    return msg

def pt_note_to_midi_msg(pt_note):
    return pt_note


class MidiRouter(object):
    """
    This is a class handling MIDI I/O.
    It takes (partial) strings for port names as inputs
    and searches for a fitting port.
    The reason this is set up in this way is that
    different OS tend to name/index MIDI ports differently.

    Use an instance if this class (and *only* this instance)
    to handle everything related to port opening, closing,
    finding, and panic. Expecially Windows is very finicky
    about MIDI ports and it'll likely break if ports are
    handled separately.

    This class can be used to:
    - create a midirouter = MidiRouter(**kwargs) with
    a number of (partial) port names or fluidsynths
    - poll a specific port: e.g.
    midirouter.input_port.poll()
    - send on a specific port: e.g.
    midirouter.output_port.send(msg)
    - open all set ports: midirouter.open_ports()
    - close all set ports: midirouter.close_ports()
    - panic reset all ports: midirouter.panic()
    - get the full name of the used midi ports: e.g.
    midirouter.input_port_name
    (DON'T use this name to open, close, etc with it,
    use the midirouter functions instead)

    Args:
        inport_name (string):
            a (partial) string for the input name.
        outport_name (string):
            a (partial) string for the output name.

    """

    def __init__(
        self,
        inport_name=None,
        outport_name=None
    ):
        self.available_input_ports = mido.get_input_names()
        print("Available inputs MIDI for mido", self.available_input_ports)
        self.available_output_ports = mido.get_output_names()
        print("Available outputs MIDI for mido", self.available_output_ports)

        self.input_port_names = {}
        self.output_port_names = {}
        self.open_ports_list = []

        # the MIDI port name the accompanion listens at (port name)
        self.input_port_name = self.proper_port_name(
            inport_name, True
        )
        # the MIDI port names / Instrument the accompanion is sent
        self.output_port_name = self.proper_port_name(
            outport_name, False
        )

        self.open_ports()

        self.input_port = self.assign_ports_by_name(
            self.input_port_name, input=True
        )
        self.output_port = self.assign_ports_by_name(
            self.output_port_name, input=False
        )

    def proper_port_name(self, try_name, input=True):
        if isinstance(try_name, str):
            if input:
                possible_names = [
                    (i, name)
                    for i, name in enumerate(self.available_input_ports)
                    if try_name in name
                ]
            else:
                possible_names = [
                    (i, name)
                    for i, name in enumerate(self.available_output_ports)
                    if try_name in name
                ]

            if len(possible_names) == 1:
                print(
                    "port name found for trial name: ",
                    try_name,
                    "the port is set to: ",
                    possible_names[0],
                )
                if input:
                    self.input_port_names[possible_names[0][1]] = None
                else:
                    self.output_port_names[possible_names[0][1]] = None
                return possible_names[0]

            elif len(possible_names) < 1:
                print("no port names found for trial name: ", try_name)
                return None
            elif len(possible_names) > 1:
                print(" many port names found for trial name: ", try_name)
                if input:
                    self.input_port_names[possible_names[0][1]] = None
                else:
                    self.output_port_names[possible_names[0][1]] = None
                return possible_names[0]
                # return None
        elif isinstance(try_name, int):
            if input:
                try:
                    possible_name = (try_name, self.available_input_ports[try_name])
                    self.input_port_names[possible_name[1]] = None
                    return possible_name
                except ValueError:
                    raise ValueError(f"no input port found for index: {try_name}")
            else:
                try:
                    possible_name = (try_name, self.available_output_ports[try_name])
                    self.output_port_names[possible_name[1]] = None
                    return possible_name
                except ValueError:
                    raise ValueError(f"no output port found for index: {try_name}")


        else:
            return None

    def open_ports_by_name(self, try_name, input=True):
        if try_name is not None:
            if input:
                port = mido.open_input(try_name)
            else:
                port = mido.open_output(try_name)
                # Adding eventual key release.
                port.reset()

            self.open_ports_list.append(port)
            return port

        else:
            return try_name

    def open_ports(self):
        for port_name in self.input_port_names.keys():
            if self.input_port_names[port_name] is None:
                port = self.open_ports_by_name(port_name, input=True)
                self.input_port_names[port_name] = port
        for port_name in self.output_port_names.keys():
            if self.output_port_names[port_name] is None:
                port = self.open_ports_by_name(port_name, input=False)
                self.output_port_names[port_name] = port

    def close_ports(self):
        for port in self.open_ports_list:
            port.close()
        self.open_ports_list = []

        for port_name in self.output_port_names.keys():
            self.output_port_names[port_name] = None
        for port_name in self.input_port_names.keys():
            self.input_port_names[port_name] = None

    def panic(self):
        for port in self.open_ports_list:
            port.panic()

    def assign_ports_by_name(self, try_name, input=True):
        if try_name is not None:
            if input:
                return self.input_port_names[try_name[1]]
            else:
                return self.output_port_names[try_name[1]]
        else:
            return None


def play_midi_from_score(score=None, 
                         midirouter=None, 
                         quarter_duration=1, 
                         default_velocity=60,
                         print_messages=False):
    
    """
    Play a score using a midirouter
    """
    if midirouter is None:
        print("No midirouter provided")
        return
    if score is None:
        print("No score provided")
        return
    note_array = score.note_array()
    onset_sec = note_array["onset_quarter"] * quarter_duration
    offset_sec = note_array["duration_quarter"] * quarter_duration + onset_sec
    noteon_messages = np.array([("note_on", p, onset_sec[i]) for i, p in enumerate(note_array["pitch"])], dtype=[("msg", "<U10"), ("pitch", int), ("time", float)])
    noteoff_messages = np.array([("note_off", p, offset_sec[i]) for i, p in enumerate(note_array["pitch"])], dtype=[("msg", "<U10"), ("pitch", int), ("time", float)])
    messages = np.concatenate([noteon_messages, noteoff_messages])
    messages = np.sort(messages, order="time")
    timediff = np.diff(messages["time"])
    output_port = midirouter.output_port

    for i, msg in enumerate(messages):
        if i == 0:
            pass
        else:
            time.sleep(timediff[i-1])
        m = mido.Message(msg["msg"], note=msg["pitch"], velocity=default_velocity)
        output_port.send(m)
        if print_messages:
            print(m)

class Sequencer(multiprocessing.Process):
    def __init__(
        self,
        outport_name="seq",
        queue=None,
        *args, 
        **kwargs):
        super(Sequencer, self).__init__(*args, **kwargs)
        self.queue = queue
        self.outport_name = outport_name
        self.router = None

        # sequencer variables
        self.playhead = 0
        self.playing = False
        self.start_time = 0
        self.tempo = 120
        self.quarter_per_ns = self.tempo / ( 60 * 1e9)
        self.next_time = 0

        # music variables
        self.default_velocity = 60
        self.loop_start_quarter = 0
        self.loop_end_quarter = 4
        self.looped_notes = None
        self.onset_quarter = None
        self.offset_quarter = None
        self.messages = None
        self.message_times = None

    def up(self, args):
        self.queue.put(args)

    def update_part(self, part):
        pass
        note_array = part.note_array()
        mask_lower = note_array["onset_quarter"] >= self.loop_start_quarter           
        mask_upper = note_array["onset_quarter"] < self.loop_end_quarter
        mask = np.all((mask_lower, mask_upper), axis=0)
        self.looped_notes = note_array[mask]
        self.onset_quarter = note_array[mask]["onset_quarter"]
        self.offset_quarter = np.clip(note_array[mask]["duration_quarter"] + self.onset_quarter, 
                                      self.loop_start_quarter, 
                                      self.loop_end_quarter-0.1)
        
        self.messages = defaultdict(list)
        self.message_times = np.array([])

        for i, note in enumerate(self.looped_notes):
            on = mido.Message('note_on', 
                         note=note["pitch"], 
                         velocity=self.default_velocity, 
                         time=0)
            off = mido.Message('note_off',
                            note=note["pitch"],
                            velocity=0,
                            time=0)
            self.messages[self.onset_quarter[i]].append(on)
            self.messages[self.offset_quarter[i]].append(off)

        self.message_times = np.sort(np.array(list(self.messages.keys())))
        self.next_time = self.message_times[0]
        
    def run(self):
        self.start_time = time.perf_counter_ns()
        self.router = MidiRouter(outport_name = self.outport_name)
        self.playing = True
        print("Sequencer started")        
        while self.playing:
            try: 
                args = self.queue.get_nowait()
                # print(args.note_array())
                self.update_part(args)
            except:
                pass

            current_time = time.perf_counter_ns()
            elapsed_time = current_time - self.start_time
            elapsed_quarter = elapsed_time * self.quarter_per_ns
            self.playhead = elapsed_quarter % (self.loop_end_quarter - self.loop_start_quarter)
            if self.playhead >= self.next_time - 0.02 and \
                self.playhead < self.next_time + 0.1 and \
                self.messages is not None:

                for msg in self.messages[self.next_time]:
                    self.router.output_port.send(msg)
                    

                # this_time = self.next_time
                idx, = np.where(self.message_times == self.next_time)
                i = idx[0]
                self.next_time = self.message_times[(i+1)%len(self.message_times)]
                # print("sent", msg, i, self.next_time, self.playhead, self.message_times)
                # time.sleep((self.next_time - this_time) / 2* self.quarter_per_ns * 1e9)

            else:
                time.sleep(0.02)

    # def stop(self):
    #     self.playing = False
    #     self.join()

def addnote(midipitch, part, 
            voice = 1, 
            start = 0, 
            end = 1, 
            idx = 0):
    """
    adds a single note by midipitch to a part
    """
    step, alter, octave = pt.utils.music.midi_pitch_to_pitch_spelling(midipitch)

    part.add(pt.score.Note(id='n{}'.format(idx), step=step, 
                        octave=int(octave), alter=alter, voice=voice, staff=int(voice)),
                        start=start, end=end)

if __name__ == "__main__":
    part = pt.load_musicxml(pt.EXAMPLE_MUSICXML)[0]
    queue =multiprocessing.Queue()
    s = Sequencer(queue=queue,
                  outport_name="iM/ONE")
    s.start()
    time.sleep(2)
    s.up(part)

    # addnote(97, part, start=3, end=4, idx=100)
    # s.up(part)

    # time.sleep(4)
    # s.terminate()
    # s.join()
