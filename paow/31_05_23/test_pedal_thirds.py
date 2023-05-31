#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script generates a MIDI file with octave-doubled arpeggios made of stacked major and minor thirds.
Whether the next third is major or minor as well as the root pitch is randomly sampled.
The tempo starts at ~0.25 notes/sec and over the course of one hour is increased to 16 notes/sec.
The sustain pedal is controlled by sinusoid curves with varying frequency constants.

Enjoy!
"""
from mido import Message, MidiFile, MidiTrack
import numpy as np

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# some sinusoids with different frequency constants for pedal controls
midi_pedal_maps = []
factors = np.arange(1,11)
for n in range(1,11):
    midi_pedal_maps.append(
    np.round((np.sin(2*np.pi*np.arange(0,128)/(128/n*4))+1)/2*127).astype(int)
    )

# tempos: 100 tempos from whole notes at 60 bpm to sixteenth notes at 240 bpm
# => 0.25 notes/sec - 16 notes/sec
# MIDI default parts per quarter is 480, MIDI default tempo is 120 bpm -> 960 ticks/sec
tempos_in_notes_per_sec = np.linspace(0.25,16,100)
tempos_in_ticks_per_note = 960 / tempos_in_notes_per_sec
# 128 notes per tempo gives a duration of ~1h
total_duration_in_hours = (1/tempos_in_notes_per_sec * 128).sum()/3600 # 1.0089
# get nice integer times divisible by two
tempos_in_ticks_per_note_int = np.round(tempos_in_ticks_per_note / 2).astype(int) 

# creating the notes
for l in range(100):
    # lowest MIDI pitch: 21
    root = np.random.randint(21, 40)
    pitch = root
    local_duration_halfed = tempos_in_ticks_per_note_int[l] 
    for k in range(128):
        #track.append(Message('program_change', program=12, time=0))      
        track.append(Message('note_on', note=pitch, velocity=44, time=local_duration_halfed))
        track.append(Message('note_on', note=pitch+12, velocity=44, time=0))
        track.append(Message('note_off', note=pitch, velocity=0, time=local_duration_halfed))
        track.append(Message('note_off', note=pitch+12, velocity=0, time=0))
        track.append(Message("control_change",
                            control=64,
                            value=midi_pedal_maps[l%10][k]))
        # highest MIDI pitch: 108
        pitch = (pitch + np.random.randint(3,5) - root )%58 + root

mid.save('test_pedal_thirds_hour.mid')