#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script generates a MIDI file with increasing numbers of simultaneous notes at increasing tempos.
Setting the "MIDI IN Delay" of the Disklavier to on make the grand piano shut down when too many simultaneous notes arrive.
We turn it off for this experiment, which means the notes are handled as fast as possible and for many simultaneous notes, strange rhythms emerge. 
The MIDI heard in the stream is a concatenation of two calls to this script with different settings.

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
    order = np.random.permutation(np.arange(21,21+88))
    local_duration_halfed = tempos_in_ticks_per_note_int[l] 
    for k in range(44): # 44 -> at most half of the keys will be pressed 
        track.append(Message('note_on', note=order[0], velocity=np.random.randint(20,30), time=local_duration_halfed))
        for pitch in order[1:k+1]:  
            track.append(Message('note_on', note=pitch, velocity=np.random.randint(20,30), time=0))
        track.append(Message('note_off', note=order[0], velocity=0, time=local_duration_halfed))
        for pitch in order[1:k+1]:
            track.append(Message('note_off', note=pitch, velocity=0, time=0))
        # use sinusoidal pedal messages
        # track.append(Message("control_change",
        #                     control=64,
        #                     value=midi_pedal_maps[l%10][k]))

mid.save('half_all_notes_no_pedal.mid')