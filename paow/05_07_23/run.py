import numpy as np
import mido
import random
import time
import os
import audiofile
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift, AirAbsorption, ApplyImpulseResponse, TimeMask, GainTransition
import zipfile
import wave
import pyaudio
import threading
from scipy import signal
from scipy.interpolate import interp1d


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
    """Perturb the parameters of the audio file"""
    new_parameters = {}
    for key, value in parameters.items():
        if key == "min_amplitude":
            # sample from a gaussian distribution
            new_min_amplitude = np.random.normal(value, 0.1)
            new_parameters[key] = new_min_amplitude if new_min_amplitude > 0 else 0.001
            new_parameters["max_amplitude"] = new_parameters["min_amplitude"] + 0.1
        if key == "min_rate":
            new_min_rate = np.random.normal(value, 1.)
            new_parameters[key] = new_min_rate if new_min_rate > 0.1 else 0.5
            max_rate = np.random.normal(value, 1.)
            max_rate = max_rate if max_rate > 0 else 0
            new_parameters["max_rate"] = new_parameters["min_rate"] + max_rate
        if key == "min_semitones":
            new_parameters[key] = -np.random.randint(0, 12)
        if key == "max_semitones":
            new_parameters[key] = np.random.randint(0, 12)
        if key == "min_fraction":
            new_parameters[key] = - np.random.uniform(0., 1.)
        if key == "max_fraction":
            new_parameters[key] = np.random.uniform(0., 1.)
        if key == "p":
            new_parameters[key] = np.random.uniform(0., 1.)
        if key == "volume":
            new_parameters[key] = np.random.uniform(0.5, 1.)
    return new_parameters


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


def generate_audio_grammar(grammar, effects, memory=[], mem_length=10, mode=1):
    """Generate a pattern from the grammar"""
    if len(memory) == 0:
        # first pattern
        pattern = random.choice(grammar["Type"])
    else:
        # weight more recent patterns
        weights = np.arange(len(memory) + len(grammar["Type"]))
        pattern = random.choices(memory+grammar["Type"], weights=weights)[0]
    # add to memory
    memory.append(pattern)
    # last element remove from memory if it exceeds size
    if len(memory) > mem_length:
        memory.pop(-1)

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
        "p": 0.5,
        "volume": 1.0
    }
    # return audio_clip
    parameters = audio_param_perturbation(parameters)
    path = effects.apply_effect(audio_clip, parameters, mode)
    return path, memory


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
        try:
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
                time.sleep(w[i] / 1000)
            # Wait for the next generation
            ########
            time.sleep(random.randint(1, 50) * 0.1)
        except KeyboardInterrupt:
            if not test:
                # Release the pedal
                msg = mido.Message('control_change', control=64, value=0)
                port.send(msg)
                port.close()
            raise ValueError("Interrupted by user")

    # Close port
    if not test:
        # Release the pedal
        msg = mido.Message('control_change', control=64, value=0)
        port.send(msg)
        port.close()


class EffectClass:

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def apply_effect(self, audio_path, params, mode):
        signal, sampling_rate = audiofile.read(audio_path)
        # reverse signal
        signal = np.flip(signal) if random.gauss(mu=0, sigma=1) > 0.6 else signal
        # normalize signal
        # signal = signal/signal.max()
        effect = self.select_effect(params)
        out = effect(signal, sampling_rate)
        # adjust volume
        out = out*params["volume"]
        # do a fade in and fade out
        fade_in = np.linspace(0, 1, 10000)
        fade_out = np.linspace(1, 0, 10000)
        out[:10000] = out[:10000]*fade_in
        out[-10000:] = out[-10000:]*fade_out

        fp = os.path.join(os.path.dirname(__file__), "temp-{}.wav".format(mode))
        audiofile.write(fp, out, sampling_rate)
        return fp

    def select_effect(self, params):
        effect = Compose([
            # AddGaussianNoise(min_amplitude=params["min_amplitude"], max_amplitude=params["max_amplitude"], p=params["p"]),
            TimeStretch(min_rate=params["min_rate"], max_rate=params["max_rate"], p=params["p"]),
            PitchShift(min_semitones=params["min_semitones"], max_semitones=params["max_semitones"], p=params["p"]),
            Shift(min_fraction=params["min_fraction"], max_fraction=params["max_fraction"], p=params["p"])
        ])
        return effect

def random_wave(length, sr=48000, base_freq=60, change_every=1, step=50):
    change_every = length // change_every

    x_samples = np.arange(0, change_every*step, step)
    freq_samples = (np.random.random(x_samples.shape)*2*step - step) + base_freq

    x = np.arange(length * sr) / sr

    dx = 2*np.pi*x

    interpolation = interp1d(x_samples, freq_samples, kind='quadratic')
    freq = interpolation(x)

    x_plot = freq*dx  # Cumsum freq * change in x

    y = np.sin(x_plot)
    return y


class GrammarGeneration:
    def __init__(self, output_midi_port="iM/ONE 1", generation_length=3600, mem_length=10):
        self.generation_length = generation_length
        self.mem_length = mem_length
        self.output_midi_port = output_midi_port
        # Download audio files
        save_path = self.download_files()
        # Initialize Background Audio
        self.background_audio_path = self.generate_background_audio(save_path)


        # Initialize Audio grammar
        self.audio_grammar = audio_grammar(save_path)

        # Initialize thread for midi generation
        self.midi_thread = threading.Thread(target=generate_and_send_midi, args=(grammar, output_midi_port, generation_length, 10, False))
        # Initialize effects
        self.effects = EffectClass()

        # Start midi generation
        self.midi_thread.start()

        # Start audio generation
        self.start_audio_generation()

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

    def generate_background_audio(self, save_path, sr=48000):
        # Fixed background audio time in seconds (5 minutes)
        fixed_backround_audio_time = 5*60
        fixed_backround_audio_time = fixed_backround_audio_time if fixed_backround_audio_time < self.generation_length else self.generation_length

        # Initialize numpy array with gaussian noise
        x = np.random.normal(0, 1, fixed_backround_audio_time * sr)
        # Filter out values lower than 0.9 to create random impulse responses
        x[x < 2.5] = 0

        # create a wave of random frequency that changes every second
        waves = np.array([
            random_wave(fixed_backround_audio_time, sr=sr, base_freq=60, step=30),
            # create a wave of 61Hz
            random_wave(fixed_backround_audio_time, sr=sr, base_freq=80, step=30),
            # create a wave of 100Hz
            random_wave(fixed_backround_audio_time, sr=sr, base_freq=200, step=50),
            0.9*random_wave(fixed_backround_audio_time, sr=sr, base_freq=200, step=50),
            random_wave(fixed_backround_audio_time, sr=sr, base_freq=500, step=100),
            random_wave(fixed_backround_audio_time, sr=sr, base_freq=1000, step=400),
        ])



        # Create filter of sawtooth impulse response
        b = np.linspace(1, 0, sr//20, endpoint=False)
        s = signal.lfilter(b, [1], x)
        # add all together
        waves = np.sum(waves, axis=0)
        # normalize
        waves = waves / np.max(np.abs(waves))
        s = waves*s
        # Normalize s between -1 and 1
        s = s / np.max(np.abs(s))

        # Apply other audio effects
        effects = Compose([
            # AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.01, p=0.5),
            # ApplyImpulseResponse(, p=0.5),
            AirAbsorption(min_temperature=10, max_temperature=20, p=0.2),
            GainTransition(min_gain_in_db=-20, max_gain_in_db=0, p=0.5),
            TimeMask(min_band_part=0.01, max_band_part=0.1, fade=True, p=0.8),
        ])
        # Apply effects
        # s = effects(s, sr)
        # Normalize s between -1 and 1
        s = s / np.max(np.abs(s))
        # Do a Fade-in of 1s
        ramp = np.linspace(0., 1., sr)
        s[:sr] = s[:sr] * ramp
        # Scale audio to 0.5
        s = s * 0.1
        # Save audio file
        audiofile.write(os.path.join(save_path, "background.wav"), s, sr)
        # ApplyImpulseResponse(os.path.join(save_path, "background.wav"), p=0.5)
        return os.path.join(save_path, "background.wav")

    def start_audio_generation(self):
        CHUNK = 1024
        wf = wave.open(self.background_audio_path, 'rb')
        p = pyaudio.PyAudio()


        background_stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )
        audio_stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()), channels=1, rate=48000, output=True)

        audio_stream_p = p.open(
            format=p.get_format_from_width(wf.getsampwidth()), channels=1, rate=48000, output=True
        )

        background_data = wf.readframes(CHUNK)
        running_audio_data = b''
        running_audio_data_p = b''
        start_time = time.time()
        audio_memory = []

        while time.time() - start_time < self.generation_length:
            # If background audio is finished, rewind
            # Background audio is 5 minutes long to reduce memory and cpu usage
            if background_data == b'':
                wf.rewind()
                background_data = wf.readframes(CHUNK)

            background_stream.write(background_data)
            background_data = wf.readframes(CHUNK)
            if running_audio_data == b'':
                audio_path, audio_memory = generate_audio_grammar(self.audio_grammar, self.effects, audio_memory, self.mem_length, mode=1)
                wf_audio = wave.open(audio_path, 'rb')
                if random.randint(0, 100) < 80:
                    print("Playing audio clip.")
                    running_audio_data = wf_audio.readframes(CHUNK)
            else:
                audio_stream.write(running_audio_data)
                running_audio_data = wf_audio.readframes(CHUNK)

            if running_audio_data_p == b'':
                audio_path, audio_memory = generate_audio_grammar(self.audio_grammar, self.effects, audio_memory, self.mem_length, mode=2)
                wf_audio_p = wave.open(audio_path, 'rb')
                if random.randint(0, 100) < 80:
                    print("Playing audio clip.")
                    running_audio_data_p = wf_audio_p.readframes(CHUNK)
            else:
                audio_stream.write(running_audio_data_p)
                running_audio_data_p = wf_audio_p.readframes(CHUNK)


        background_stream.stop_stream()
        audio_stream.stop_stream()
        audio_stream_p.stop_stream()

        background_stream.close()
        audio_stream.close()
        audio_stream_p.close()

        p.terminate()


if __name__ == "__main__":
    # Download Audio clips.
    GrammarGeneration(generation_length=120)















