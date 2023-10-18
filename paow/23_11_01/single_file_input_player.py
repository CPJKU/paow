import partitura as pt
import mido
import threading
import copy
import time
import numpy as np
from mido import Message
from scipy.interpolate import interp1d
import argparse
import os
import glob


PPART_FIELDS = [
    ("onset_sec", "f4"),
    ("duration_sec", "f4"),
    ("pitch", "i4"),
    ("velocity", "i4"),
    ("track", "i4"),
    ("channel", "i4"),
    ("id", "U256"),
]

def performance_from_part(part, bpm=100, velocity=64):
    """
    TODO
    ----
    * allow for bpm to be a callable or an 2D array with columns (onset, bpm)
    * allow for velocity to be a callable or a 2D array (onset, velocity)
    """
    if not isinstance(part, pt.score.Part):
        raise ValueError("The input `part` must be a "
                         f"`partitura.score.Part` instance, not {type(part)}")

    snote_array = part.note_array()

    pnote_array = np.zeros(len(snote_array), dtype=PPART_FIELDS)

    unique_onsets = np.unique(snote_array['onset_beat'])
    unique_onset_idxs = np.array([np.where(snote_array['onset_beat'] == u)[0]
                                  for u in unique_onsets],
                                 dtype=object)

    iois = np.diff(unique_onsets)

    bp = 60 / float(bpm)

    # TODO: allow for variable bpm and velocity
    pnote_array['duration_sec'] = bp * snote_array['duration_beat']
    pnote_array['velocity'] = int(velocity)
    pnote_array['pitch'] = snote_array['pitch']
    pnote_array['id'] = snote_array['id']

    # if isinstance(bpm, (float, int)):
    #     bp = float(60 / bpm) * np.ones_like(iois)

    # if isinstance(velocity, float, int):
    #     velocity = int(velocity) * np.ones(len(iois), dtype=int)

    p_onsets = np.r_[0, np.cumsum(iois * bp)]

    for ix, on in zip(unique_onset_idxs, p_onsets):

        pnote_array['onset_sec'][ix] = on

    ppart = pt.performance.PerformedPart.from_note_array(pnote_array)

    return ppart


class Note(object):
    """
    Class for representing notes
    """

    def __init__(self, pitch, onset, duration, p_onset=None,
                 p_duration=None, velocity=64):

        self.pitch = pitch
        self.onset = onset
        self.duration = duration
        self.p_onset = p_onset
        self.p_duration = p_duration
        self.already_performed = False
        self.velocity = velocity
        self._note_on = Message(
            type='note_on',
            velocity=self.velocity,
            note=self.pitch#,
            #time=self.p_onset if self.p_onset is not None else 0
            )

        self._note_off = Message(
            type='note_off',
            velocity=0,
            note=self.pitch#,
            #time=self.p_offset
            )

    @property
    def p_onset(self):
        return self._p_onset

    @p_onset.setter
    def p_onset(self, onset):
        self._p_onset = onset

    @property
    def note_on(self):
        self._note_on.velocity = self.velocity
        self._note_on.time = self.p_onset
        return self._note_on

    @property
    def note_off(self):
        self._note_off.velocity = self.velocity
        self._note_off.time = self.p_offset
        return self._note_off

    @property
    def p_offset(self):
        return self.p_onset + self.p_duration

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = int(velocity)


class Chord(object):
    """
    Class for representing Score onsets or "chords".
    """

    def __init__(self, notes):

        assert all([n.onset == notes[0].onset for n in notes])

        self.notes = notes
        self.num_notes = len(notes)

        self.onset = self.notes[0].onset
        self.pitch = np.array([n.pitch for n in self.notes])
        self.duration = np.array([n.duration for n in self.notes])

    def __getitem__(self, index):
        return self.notes[index]

    def __len__(self):
        return self.num_notes

    @property
    def p_onset(self):

        if any([n.p_onset is None for n in self.notes]):
            return None
        else:
            return np.mean([n.p_onset for n in self.notes])

    @p_onset.setter
    def p_onset(self, p_onset):
        if isinstance(p_onset, (float, int)):
            for n in self.notes:
                n.p_onset = p_onset
        elif len(p_onset) == self.num_notes:
            for n, po in zip(self.notes, p_onset):
                n.p_onset = po

    @property
    def p_duration(self):
        if any([n.p_duration is None for n in self.notes]):
            return None
        else:
            return np.mean([n.p_duration for n in self.notes])

    @p_duration.setter
    def p_duration(self, p_duration):
        if isinstance(p_duration, (float, int)):
            for n in self.notes:
                n.p_duration = p_duration
        elif len(p_duration) == self.num_notes:
            for n, po in zip(self.notes, p_duration):
                n.p_duration = po

    @property
    def velocity(self):
        if any([n.velocity is None for n in self.notes]):
            return None
        else:
            return np.max([n.velocity for n in self.notes])

    @velocity.setter
    def velocity(self, velocity):
        if isinstance(velocity, (float, int)):
            for n in self.notes:
                n.velocity = velocity
        elif len(velocity) == self.num_notes:
            for n, po in zip(self.notes, velocity):
                n.velocity = po


class Score(object):

    def __init__(self, notes, access_mode='indexwise'):

        # TODO: Seconday sort by pitch
        self.notes = np.array(sorted(notes, key=lambda x: x.pitch))

        self.access_mode = access_mode
        onsets = np.array([n.onset for n in self.notes])

        # Unique score positions
        self.unique_onsets = np.unique(onsets)
        self.unique_onsets.sort()

        # indices of the notes belonging to each
        self.unique_onset_idxs = [np.where(onsets == u)
                                  for u in self.unique_onsets]

        self.chords = np.array(
            [Chord(self.notes[ui])
             for ui in self.unique_onset_idxs],
            dtype=object)

        self.chord_dict = dict(
            [(u, c) for u, c in zip(self.unique_onsets, self.chords)])

    @property
    def access_mode(self):
        return self._access_mode

    @access_mode.setter
    def access_mode(self, access_mode):
        if access_mode not in ('indexwise', 'timewise'):
            raise ValueError('`access_mode` should be "indexwise" or "timewise". '
                             'Given {0}'.format(access_mode))
        self._access_mode = access_mode

    def __getitem__(self, index):
        if self.access_mode == 'indexwise':
            return self.chords[index]
        elif self.access_mode == 'timewise':
            return self.chord_dict[index]

    def __len__(self):
        return len(self.unique_onsets)


def part_to_score(fn_spart_or_ppart, bpm=100, velocity=64):
    """
    Get a `Score` instance from a partitura `Part` or `PerformedPart`

    Parameters
    ----------
    fn_spart_or_ppart : filename, Part of PerformedPart
        Filename or partitura Part
    bpm : float
        Beats per minute to generate the performance (this is ignored if
        the input is a `PerformedPart`
    velocity : int
        Velocity to generate the performance (this is ignored if the input
        is a `PerformedPart`

    Returns
    -------
    score : Score
        A `Score` object.
    """

    #nif isinstance(fn_spart_or_ppart, str):
    score = pt.load_score(fn_spart_or_ppart)

    if len(score) > 1:
        part = pt.score.merge_parts(score.parts)

    else: 
        part = score[0]
    # elif isinstance(fn_spart_or_ppart, (pt.score.Part, pt.performance.PerformedPart)):
    #     part = fn_spart_or_ppart

    s_note_array = part.note_array()
    if isinstance(part, pt.score.Part):
        p_note_array = performance_from_part(part, bpm).note_array()
    else:
        p_note_array = s_note_array

    notes = []
    for sn, pn in zip(s_note_array, p_note_array):
        note = Note(pitch=sn['pitch'],
                    onset=sn['onset_beat'],
                    duration=sn['duration_beat'],
                    p_onset=pn['onset_sec'],
                    p_duration=pn['duration_sec'],
                    velocity=pn['velocity'])
        notes.append(note)

    score = Score(notes)

    return score

class MidiInputPlayer():#threading.Thread):

    def __init__(self, i_name, o_name, chords, virtual=False):
        # threading.Thread.__init__(self)

        self.chords = chords

        self.midi_out_music_port_name = o_name
        self.midi_out_music = mido.open_output(self.midi_out_music_port_name)
        # 
        self.input_port_name = i_name
        self.input_port =mido.open_input(self.input_port_name, virtual=virtual)
        self.running = False


    def run(self):
        local_chords = copy.deepcopy(self.chords)
        self.running = True
        try: 
            print("listening-----")
            # set the pedal to zero
            self.midi_out_music.send(mido.Message(type = "control_change", control=64, value=0))
            while self.running:
                
                for In_msg in self.input_port.iter_pending():

                    if len(local_chords) == 0:
                        print("exit")
                        self.exit()
                        break

                    # print(In_msg)
                    if In_msg.type == "note_on":

                        for note in local_chords[0].notes:
                            msg_on = note._note_on
                            msg_on.velocity =  In_msg.velocity
                            print(msg_on.velocity)
                            self.midi_out_music.send(msg_on)
          
                    elif In_msg.type == "note_off":
                        
                        for note in local_chords[0].notes:
                            self.midi_out_music.send(note._note_off)

                        local_chords = np.delete(local_chords,0)

                time.sleep(0.005)


        except KeyboardInterrupt:
            self.exit()

    def exit(self):
        self.running = False
        self.input_port.close()
        self.midi_out_music.close()

def proper_port_name(try_name, available_input_ports):
        if isinstance(try_name, str):
            possible_names = [(i, name) for i, name in enumerate(available_input_ports) if try_name in name]
            if len(possible_names) == 1:
                print("port name found for trial name: ", try_name, "the port is set to: ", possible_names[0]) 
                return possible_names[0]
            elif len(possible_names) < 1:
                print("no port names found for trial name: ", try_name) 
                return None
            elif len(possible_names) > 1:
                print("too many port names found for trial name: ", try_name) 
                return possible_names[0]
        else:
            return None

def perf_score_map_from_match(match_path):
    """

    Parameters
    ----------
    match_path : string
        a path of a match file
    
    Returns
    -------
    
    """

    ppart, alignment, part = pt.load_match(match_path, create_part=True)

    beat_map = part.beat_map

    perf_times = []
    score_times = []

    ppart_by_id = {note["id"]: note["note_on"] for note in ppart.notes}
    part_by_id = {note.id: beat_map(note.start.t) for note in part.notes_tied}

    for line in alignment:
        if line["label"] == "match":
            perf_times.append(ppart_by_id[line["performance_id"]])
            score_times.append(part_by_id[line["score_id"]])

    perf_score_map = interp1d(perf_times, score_times, fill_value="extrapolate")
   
    return perf_times, score_times, perf_score_map

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, default=0)
    parser.add_argument("--no", type=int, default=30)
    args = parser.parse_args()

    # https://github.com/musedata/humdrum-haydn-quartets
    quartet_path = "to_set"

    pieces = [f for f in glob.glob(os.path.join(quartet_path, "*.krn"))]
    pieces.sort()

    o_name = proper_port_name("ocus", mido.get_output_names())[1]
    i_name = proper_port_name("seq", mido.get_input_names())[1]

    for ids in range(args.id, args.id+ args.no):
        print("preparing ", os.path.basename(pieces[ids]))
        score = part_to_score(pieces[ids])
        dummy_solo = MidiInputPlayer(i_name, o_name, score.chords)
        dummy_solo.run()