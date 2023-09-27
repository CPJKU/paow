import partitura as pt
import numpy as np
import os
from tqdm import tqdm


def save_performance_midi(pianoroll, name="newmidi.mid"):

    new_note_array = pt.utils.pianoroll_to_notearray(pianoroll, time_unit="sec", time_div=100)

    # We can export the note array to a MIDI file
    ppart = pt.performance.PerformedPart.from_note_array(new_note_array)

    pt.save_performance_midi(ppart, os.path.join(os.path.dirname(__file__), "artifacts", name))


def get_pianoroll_from_midi(midi_files):

    pianorolls = []

    for midi_file in tqdm(midi_files):
        # Load MIDI file
        performance = pt.load_performance_midi(midi_file)

        # Get the pianoroll
        pianoroll = pt.utils.compute_pianoroll(
            performance,
            time_unit="sec",
            time_div=100,
            piano_range=True
        )
        pianorolls.append(pianoroll.T.todense())

    pianorolls = np.concatenate(pianorolls, axis=0)

    return pianorolls


def granulate_pianoroll(pianoroll, granularity):


    pianoroll = pianoroll
    # split pianoroll into granularity pieces

    dim = pianoroll.shape[0]
    if isinstance(granularity, tuple) or isinstance(granularity, list):
        import random
        granularity_start = int(granularity[0] * 100)
        granularity_end = int(granularity[1] * 100)
        rest = int(dim)
        split_sizes = []
        while rest > granularity_end:
            random_granularity = random.randint(granularity_start, granularity_end)
            split_sizes.append(random_granularity)
            rest = rest - random_granularity
        split_sizes.append(rest)
        x = np.split(pianoroll, split_sizes, axis=0)
        random_permutation = np.random.permutation(len(x))
        x_new = [x[i] for i in random_permutation]
    else:
        granularity = granularity * 100
        re_index = int(dim % granularity)
        x = np.array(np.split(pianoroll[:-re_index], dim // granularity, axis=0))
        # random permutation over the 0th axis
        random_permutation = np.random.permutation(x.shape[0])
        x_new = x[random_permutation]
    # concatenate over the 0th axis
    x_new = np.concatenate(x_new, axis=0)
    return x_new.T


def main():
    file_path = "/home/manos/Desktop/JKU/data/aligned_performance_data/alignments/midi_kaist_chopin/"

    # get file paths
    midi_files = [os.path.join(file_path, fn) for fn in os.listdir(file_path)]

    # get random permutation of file paths
    random_permutation = np.random.permutation(len(midi_files))
    midi_files = np.array(midi_files)[random_permutation]

    pianoroll = get_pianoroll_from_midi(midi_files[:10])

    granulation = (0.1, 4)
    # granulate pianoroll
    new_pianoroll = granulate_pianoroll(pianoroll, granulation)

    # save pianoroll as midi
    save_performance_midi(new_pianoroll, name=f"newmidi-granulated-{granulation}.mid")


if __name__ == "__main__":
    main()