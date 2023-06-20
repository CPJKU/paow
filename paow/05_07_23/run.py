import numpy as np
import mido
import random
import time
import swmixer
import os
import tempfile
import audiofile
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift
import urllib
import zipfile



grammar = {
    "Pattern" : [["P1", "A1", "D1"], ["P2", "A2", "D2"], ["P3", "A3", "D3"]],
    "P1": np.array([67, 57, 53, 70]),
    "P2": np.array([67, 57, 53, 70]),
    "P3": np.array([67, 57, 53, 70]),
    "A1": np.array([67, 57, 53, 70]),
    "A2": np.array([67, 57, 53, 70]),
    "A3": np.array([67, 57, 53, 70]),
    "D1": np.array([300, 200, 500, 700]),
    "D2": np.array([300, 200, 500, 700]),
    "D3": np.array([300, 200, 500, 700]),
}

def audio_grammar(main_path):
    path1 = os.path.join(main_path, "X")
    path2 = os.path.join(main_path, "Y")
    path3 = os.path.join(main_path, "Z")
    one = os.listdir(path1)
    two = os.listdir(path2)
    three = os.listdir(path3)
    grammar = {
        "Type": ["T1", "T2", "T3"],
        "T1": one,
        "T2": two,
        "T3": three
    }
    return grammar



def perturbation(p, a, d):
    new_p = np.array(p) + np.random.randint(-1, 2, len(p))
    new_a = np.array(a) + np.random.randint(-10, 10, len(a))
    add_mask = np.zeros(len(a))
    ind_a = random.choice(np.arange(len(a)))
    add_mask[ind_a] = 10
    new_a = new_a + add_mask
    new_d = np.array(d) + np.random.randint(-1000, 1000, len(d))
    # Filter out negative values
    new_d[new_d < 0] = 0
    return new_p, new_a, new_d


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

    p, a, d = pattern
    # Replace Letters
    ########
    p, a, d = grammar[p], grammar[a], grammar[d]

    # add to memory
    memory.append(pattern)
    # last element remove from memory if it exceeds size
    if len(memory) > mem_length:
        memory.pop(-1)
    return perturbation(p, a, d), memory


def generate_audio_grammar(grammar, memory, effects, mem_length=10):
    """Generate a pattern from the grammar"""
    if len(memory) == 0:
        # first pattern
        pattern = random.choice(grammar["Type"])
    else:
        # weight more recent patterns
        weights = np.arange(len(memory) + len(grammar["Type"]))
        pattern = random.choices(memory+grammar["Type"], weights=weights)[0]

    audio_clip, parameters = random.choice(grammar[pattern])

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
    tracked_generation_time = 0
    memory = list()
    while tracked_generation_time < generation_length*1000:
        (p, a, d), memory = generate_grammar(music_grammar, memory, mem_length)
        # Generate midi message
        ########
        tracked_generation_time += np.sum(d)
        # Send midi message
        for i in range(len(p)):
            if test:
                print("Note: {}, Velocity: {}, Duration: {}".format(p[i], a[i], d[i]))
                continue
            msg = mido.Message('note_on', note=int(p[i]), velocity=int(a[i]), time=int(d[i]))
            port.send(msg)
            time.sleep(d[i])
            msg = mido.Message('note_off', note=int(p[i]), velocity=int(a[i]), time=int(d[i]))
            port.send(msg)
            time.sleep(d[i])

            # Wait for the next generation
            ########
            time.sleep(0.1)
            tracked_generation_time += 0.1*1000
    # Close port
    if not test:
        port.close()


class AudioMixing:
    """
    Receives audio clips real time and plays them in a single stereo out.
    """
    def __init__(self, total_duration=3600, samplerate=44100, chunksize=1024, stereo=True):
        swmixer.init(samplerate=samplerate, chunksize=chunksize, stereo=stereo)
        swmixer.start()
        self.total_duration = total_duration

    def add_clip(self, audio_path, volume=0.5, time_until_next=60):
        if time_until_next - self.total_duration > 0:
            s = swmixer.StreamingSound(audio_path)
            s.play(volume=volume)
            self.total_duration -= time_until_next


class EffectClass:

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply_effect(self, audio_path, params):
        signal, sampling_rate = audiofile.read(audio_path)
        signal = self.select_effect(params)
        out = self.effect(signal, sampling_rate)
        fp = tempfile.TemporaryFile()
        audiofile.write(fp, out, sampling_rate)
        return fp

    def select_effect(self, params):
        self.effect = Compose([
            AddGaussianNoise(min_amplitude=params["min_amplitude"], max_amplitude=params["max_amplitude"], p=params["p"]),
            TimeStretch(min_rate=params["min_rate"], max_rate=params["max_rate"], p=params["p"]),
            PitchShift(min_semitones=params["min_semitones"], max_semitones=params["max_semitones"], p=params["p"]),
            Shift(min_fraction=params["min_fraction"], max_fraction=params["max_fraction"], p=params["p"])
        ])


class GrammarGeneration:
    def __init__(self, output_midi_port="dummy", generation_length=60, mem_length=10, ):
        save_path = self.download_files()
        # Initialize Audio
        self.mixer = AudioMixing(total_duration=generation_length)
        # Initialize Audio grammar
        self.audio_grammar = audio_grammar(save_path)
        # Generate and send midi
        generate_and_send_midi(grammar, port_name="dummy", generation_length=60, mem_length=10, test=True)

    def download_files(self):
        import urllib
        url = ""
        testfile = urllib.URLopener()
        save_path = os.path.join(os.path.dirname(__file__), "audio_files.zip")
        testfile.retrieve(url, save_path)
        # unzip files
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(__file__))
        return os.path.dirname(__file__)



if __name__ == "__main__":
    # Download Audio clips.
    GrammarGeneration()















