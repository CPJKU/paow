#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script contains a technical exercise investigating the limits of
reproduction of the Disklavier.

First, each note is played at different MIDI velocities. The audio for
this part will be analyzed to create a dictionary of sounds of the Disklavier
for later experiments.

Afterwards, we explore the speed limits of the hammer actuators of the
Disklavier, by playing repeated notes with increasing speed and velocity.
This experiment will be useful to assess how fast can the piano play, and
whether there are reproduction differences at different MIDI velocities.
"""
import numpy as np
import partitura as pt

from partitura.performance import PerformedPart, Performance

# MIDI velocities to test
MIDI_VELOCITIES = np.clip(np.arange(0, 140, 10), a_min=1, a_max=127)

# MIDI note numbers of the piano keys
PIANO_KEYS = np.arange(21, 109)

# Number of repetitions per second
REPETITIONS = np.arange(1, 16)


def test_note_velocities(
    midi_velocities: np.ndarray = MIDI_VELOCITIES,
    piano_keys: np.ndarray = PIANO_KEYS,
) -> np.ndarray:
    """
    Generate a note array to test the MIDI velocity of the Disklavier.

    Parameters
    ----------
    midi_velocities: np.ndarray
        An array specifying the MIDI velocities to test.
    piano_keys: np.ndarray
       MIDI pitch of the piano keys to include in the test.

    Returns
    -------
    note_array: np.ndarray
        A structured array with note information. This array follows the
        structure of the note arrays of `PerformedPart` objects.
    """

    # Number of notes
    n_onsets = len(piano_keys) * len(midi_velocities)

    # Initialize array
    note_array = np.zeros(
        n_onsets,
        dtype=[
            ("pitch", "i4"),
            ("onset_sec", "f4"),
            ("duration_sec", "f4"),
            ("velocity", "i4"),
        ],
    )

    note_array["pitch"] = np.repeat(piano_keys, len(midi_velocities))
    note_array["velocity"] = np.tile(midi_velocities, len(piano_keys))

    # onsets will be every second
    note_array["onset_sec"] = np.arange(n_onsets)

    # durations will be 0.5 seconds
    note_array["duration_sec"] = np.ones(n_onsets) * 0.5

    return note_array


def test_repetitions(
    repetitions: np.ndarray = REPETITIONS,
    pitch: int = 60,
    velocity: int = 60,
) -> np.ndarray:
    """
    Generate a note array to test the repetition speed of the Disklavier.

    Parameters
    ----------
    repetitions: np.ndarray
        An array specifying the number of repetitions per second of a note.
    pitch: int
        MIDI pitch of the note.
    velocity: int
        MIDI velocity of the note

    Returns
    -------
    note_array: np.ndarray
        A structured array with note information. This array follows the
        structure of the note arrays of `PerformedPart` objects.
    """

    n_onsets = sum(repetitions)

    # Initialize array
    note_array = np.zeros(
        n_onsets,
        dtype=[
            ("pitch", "i4"),
            ("onset_sec", "f4"),
            ("duration_sec", "f4"),
            ("velocity", "i4"),
        ],
    )

    start = 0
    for i, r in enumerate(repetitions):

        sl = slice(start, start + r)

        # set pitch
        note_array["pitch"][sl] = pitch
        onsets = np.linspace(0, 1, r, False)
        # set onsets
        note_array["onset_sec"][sl] = (
            onsets + note_array["onset_sec"][start - 1] + (2 * (i != 0))
        )
        # set duration (as half of the inter onset interval
        note_array["duration_sec"][sl] = np.ones(r) * 0.5 / r

        # set velocity
        note_array["velocity"][sl] = np.ones(r) * velocity

        start += r

    return note_array


def get_duration(note_arrays: list) -> float:
    """
    Get duration of the last array note array in the list.

    Parameters
    ----------
    note_arrays: list
        A list of structured note arrays with note information.

    Returns
    -------
    end_time : float
        Duration of the music in the note array in seconds.
    """

    end_time = (
        note_arrays[-1]["onset_sec"] + note_arrays[-1]["duration_sec"]
    ).max() - note_arrays[-1]["onset_sec"].min()

    return end_time


def main() -> None:
    """
    Generate a MIDI file that explores the reproduction limits of
    the Disklavier.
    """
    # Initialize note arrays with test of MIDI velocities
    note_arrays = [test_note_velocities()]

    na_start = get_duration(note_arrays) + 3

    diminished_chord = np.array([0, 3, 6, 9])

    pitch = np.hstack(
        ([21] + [diminished_chord + (i * 12) + 24 for i in range(7)] + [108])
    )

    for p in pitch:
        for vel in np.arange(10, 130, 25):
            note_arrays.append(test_repetitions(pitch=p, velocity=vel))
            note_arrays[-1]["onset_sec"] += na_start
            na_start += get_duration(note_arrays) + 3

    # Concatenate all Note arrays
    note_array = np.hstack(note_arrays)

    # Create a PerformedPart
    ppart = PerformedPart.from_note_array(note_array)

    # Create a Performance
    performance = Performance(ppart)

    # Export the Performance to a MIDI file
    pt.save_performance_midi(
        performance,
        out="limits_of_the_age_of_reproduction.mid",
    )


if __name__ == "__main__":

    main()
