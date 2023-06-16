import numpy as np
import mido
import random
import time



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
    def __init__(self):
        pass

    def add_clip(self, audio_clip):
        pass

    def mix(self):
        pass





if __name__ == "__main__":
    # Generate and send midi
    generate_and_send_midi(grammar, port_name="dummy", generation_length=60, mem_length=10, test=True)
    # Close port












