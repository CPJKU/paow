import numpy as np
import mido
import random
import time


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
            if random.random() < 0.1:
                # Hold down the pedal (sometimes it releases if no message is sent)
                msg = mido.Message('control_change', control=64, value=127)
                port.send(msg)
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


class GrammarGeneration:
    def __init__(self, output_midi_port="iM/ONE 1", generation_length=3600, mem_length=10):
        self.generation_length = generation_length
        self.mem_length = mem_length
        self.output_midi_port = output_midi_port
        # Define grammar
        self.grammar = self.define_grammar()
        # Initialize thread for midi generation
        self.start_midi_generation()

    def start_midi_generation(self):
        generate_and_send_midi(
            music_grammar=self.grammar,
            port_name=self.output_midi_port,
            generation_length=self.generation_length,
            mem_length=self.mem_length,
        )

    def define_grammar(self):
        return {
            "Pattern": [[f"P{i}", f"A{i}", f"D{i}", f"W{i}"] for i in range(5)],
            "P1": np.array([67, 75, 71, 78, 77, 88]),
            "P2": np.array([27, 107, 62, 55, 71, 63]),
            "P3": np.array([55, 62, 69, 76, 81, 82, 88]),
            "P4": np.array([25, 108]),
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


if __name__ == "__main__":
    import argparse

    args = argparse.ArgumentParser()
    args.add_argument("--generation_length", type=int, default=3600, help="Length of the generated audio in seconds")
    args.add_argument("--mem_length", type=int, default=5, help="Length of the memory of the audio and midi generation")
    args.add_argument("--output_midi_port", type=str, default="iM/ONE 1", help="Name of the midi port to send the generated midi to")

    args = args.parse_args()

    GrammarGeneration(generation_length=args.generation_length, mem_length=args.mem_length,
                      output_midi_port=args.output_midi_port)















