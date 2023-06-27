import numpy as np
import mido
import random
import time
import swmixer
import os
import tempfile
import audiofile
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift
import zipfile
import pyaudio
import wave
import threading


class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True,
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """
        self.stream.close()
        self.p.terminate()



grammar = {
    "Pattern" : [["P1", "A1", "D1", "W1"], ["P2", "A2", "D2", "W2"], ["P3", "A3", "D3", "W3"], ["P4", "A4", "D4", "W4"]],
    "P1": np.array([67, 75, 71, 78, 77, 88]),
    "P2": np.array([27, 98, 62, 55, 71, 63]),
    "P4": np.array([27, 98, 62, 55, 71, 63]),
    "P3": np.array([55, 62, 69, 76, 81, 82, 88]),
    "P4": np.array([27, 100]),
    "A1": np.array([30, 30, 30, 30, 30, 30]),
    "A2": np.array([20, 20, 20, 20, 20, 20]),
    "A3": np.array([20, 20, 20, 20, 20, 20, 20]),
    "A4": np.array([20, 20]),
    "D1": np.array([300, 300, 300, 300, 300, 300]),
    "D2": np.array([4000, 4000, 3000, 3000, 3000, 3000]),
    "D3": np.array([3000, 3000, 3000, 3000, 3000, 3000, 3000]),
    "D4": np.array([3000, 3000]),
    "W1": np.array([800, 800, 800, 800, 800, 800]),
    "W2": np.array([0, 5000, 0, 0, 0, 3000]),
    "W3": np.array([100, 100, 100, 100, 100, 100, 3000]),
    "W4": np.array([0, 3000])

}

def audio_grammar(main_path):
    path1 = os.path.join(main_path, "T1")
    path2 = os.path.join(main_path, "T2")
    path3 = os.path.join(main_path, "T3")
    one = list(map(lambda x: os.path.join(path1, x), os.listdir(path1)))
    two = list(map(lambda x: os.path.join(path2, x), os.listdir(path2)))
    three = list(map(lambda x: os.path.join(path3, x), os.listdir(path3)))
    grammar = {
        "Type": ["T1", "T2", "T3"],
        "T1": one,
        "T2": two,
        "T3": three
    }
    return grammar



def perturbation(p, a, d, w):
    new_p = np.array(p) + np.random.randint(-1, 2, len(p))
    new_a = np.array(a) + np.random.randint(-10, 10, len(a))
    add_mask = np.zeros(len(a))
    ind_a = random.choice(np.arange(len(a)))
    add_mask[ind_a] = 10
    new_a = new_a + add_mask
    new_d = np.array(d) + np.random.randint(-1000, 1000, len(d))
    new_w = np.array(w) + np.random.randint(-300, 300, len(d))
    # Filter out negative values
    new_d[new_d < 0] = 0
    new_w[new_w < 0] = 0
    return new_p, new_a, new_d, new_w


def audio_param_perturbation(parameters):
    new_parameters = parameters
    return parameters


def generate_grammar(grammar, memory, mem_length=10):
    """Generate a pattern from the grammar"""

    if len(memory) == 0:
        # first pattern
        pattern = random.choice(grammar["Pattern"])
    else:
        # weight more recent patterns
        weights = np.arange(len(memory) + len(grammar["Pattern"]))
        pattern = random.choices(memory+grammar["Pattern"], weights=weights)[0]

    p, a, d, w = pattern
    # Replace Letters
    ########
    p, a, d, w = grammar[p], grammar[a], grammar[d], grammar[w]

    # add to memory
    memory.append(pattern)
    # last element remove from memory if it exceeds size
    if len(memory) > mem_length:
        memory.pop(-1)
    return perturbation(p, a, d, w), memory


def generate_audio_grammar(grammar, effects, memory=[], mem_length=10):
    """Generate a pattern from the grammar"""
    if len(memory) == 0:
        # first pattern
        pattern = random.choice(grammar["Type"])
    else:
        # weight more recent patterns
        weights = np.arange(len(memory) + len(grammar["Type"]))
        pattern = random.choices(memory+grammar["Type"], weights=weights)[0]

    audio_clip = random.choice(grammar[pattern])
    parameters = {
        "min_amplitude": 0.001,
        "max_amplitude": 0.015,
        "min_rate": 0.8,
        "max_rate": 1.2,
        "min_semitones": -4,
        "max_semitones": 4,
        "min_fraction": -0.5,
        "max_fraction": 0.5,
        "p": 0.5

    }
    # return audio_clip
    parameters = audio_param_perturbation(parameters)
    path = effects.apply_effect(audio_clip, parameters)
    return path


def generate_and_send_midi(music_grammar, port_name, generation_length=3600, mem_length=10, test=False):
    """Generate a midi message and send it to the port

    Parameters
    ----------
    music_grammar : dict
        The grammar for the music
    port_name : mido port name
        The port to send the midi message
    generation_length : int
        The length of the generation in seconds
    mem_length : int
        The length of the memory
    """
    # Initialize port
    port = mido.open_output(port_name) if not test else None
    # Hold down the pedal
    msg = mido.Message('control_change', control=64, value=127)
    port.send(msg)
    start_time = time.time()
    memory = list()
    while time.time() - start_time < generation_length:
        (p, a, d, w), memory = generate_grammar(music_grammar, memory, mem_length)
        # Generate midi message
        ########
        # Send midi message
        for i in range(len(p)):
            if test:
                print("Note: {}, Velocity: {}, Duration: {}".format(p[i], a[i], d[i]))
                continue
            msg = mido.Message('note_on', note=int(p[i]), velocity=int(a[i]), time=0)
            port.send(msg)
            print(msg)
            msg = mido.Message('note_off', note=int(p[i]), velocity=int(a[i]), time=int(d[i]))
            port.send(msg)

            # Wait for the next note
            time.sleep(w[i]/1000)
        # Wait for the next generation
        ########
        time.sleep(random.randint(1, 50)*0.1)


    # Close port
    if not test:
        # Release the pedal
        msg = mido.Message('control_change', control=64, value=0)
        port.send(msg)
        port.close()

def play_clip(audio_path):
    a = AudioFile(audio_path)
    a.play()
    a.close()


class AudioMixing:
    """
    Receives audio clips real time and plays them in a single stereo out.
    """
    def __init__(self, total_duration=3600, samplerate=44100, chunksize=1024, stereo=True):
        self.total_duration = total_duration

    def add_clip(self, audio_path, volume=0.5, time_until_next=60):
        if time_until_next - self.total_duration < 0:
            # start a new process thread
            # play the clip
            play_clip(audio_path)
            # t = threading.Thread(target=play_clip, args=(audio_path))
            # t.start()





class EffectClass:

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply_effect(self, audio_path, params):
        signal, sampling_rate = audiofile.read(audio_path)
        # reverse signal
        signal = np.flip(signal) if random.gauss(mu=0, sigma=1) > 0.6 else signal
        # normalize signal
        # signal = signal/signal.max()
        effect = self.select_effect(params)
        out = effect(signal, sampling_rate)
        # fp = tempfile.TemporaryFile(dir=".",suffix=".wav")
        fp = os.path.join(os.path.dirname(__file__), "temp.wav")
        audiofile.write(fp, out, sampling_rate)
        return fp

    def select_effect(self, params):
        effect = Compose([
            AddGaussianNoise(min_amplitude=params["min_amplitude"], max_amplitude=params["max_amplitude"], p=params["p"]),
            TimeStretch(min_rate=params["min_rate"], max_rate=params["max_rate"], p=params["p"]),
            PitchShift(min_semitones=params["min_semitones"], max_semitones=params["max_semitones"], p=params["p"]),
            Shift(min_fraction=params["min_fraction"], max_fraction=params["max_fraction"], p=params["p"])
        ])
        return effect


class GrammarGeneration:
    def __init__(self, output_midi_port="iM/ONE 1", generation_length=3600, mem_length=10, ):
        # Download audio files
        save_path = self.download_files()
        # Initialize Audio
        self.mixer = AudioMixing(total_duration=generation_length)
        # Initialize Audio grammar
        self.audio_grammar = audio_grammar(save_path)

        # Initialize thread for midi generation
        self.midi_thread = threading.Thread(target=generate_and_send_midi, args=(grammar, output_midi_port, generation_length, 10, False))
        # Initialize effects
        effects = EffectClass()

        # Start midi generation
        self.midi_thread.start()
        start_time = time.time()
        while time.time() - start_time < generation_length:
            # Generate audio clip
            audio_clip = generate_audio_grammar(self.audio_grammar, effects)
            # Add to mixer
            self.mixer.add_clip(audio_clip, volume=0.5, time_until_next=60)
            time.sleep(10)


    def download_files(self):

        url = ""
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "audio_files")):
            import requests
            save_path = os.path.join(os.path.dirname(__file__), "audio_files.zip")
            r = requests.get(url, stream=True)
            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            # unzip files
            with zipfile.ZipFile(save_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(__file__))
        return os.path.join(os.path.dirname(__file__), "audio_files")


if __name__ == "__main__":
    # Download Audio clips.
    GrammarGeneration()















