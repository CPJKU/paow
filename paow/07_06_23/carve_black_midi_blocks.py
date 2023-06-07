#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment carves three well-known pieces from blocks of black midi.

Enjoy!
"""
import partitura as pt
import numpy as np
import numpy.lib.recfunctions as rfn
from partitura.musicanalysis.performance_codec import to_matched_score

# get an original performance
performance, alignment, score = pt.load_match("MYSTERY.match", create_score=True)
m_score, _ = to_matched_score(score, performance, alignment)
ptime_to_stime_map, stime_to_ptime_map = pt.musicanalysis.performance_codec.get_time_maps_from_alignment(performance, score, alignment)

# parameters
dtypes=[('onset_sec', '<f4'), ('duration_sec', '<f4'), ('pitch', '<i4'), ('velocity', '<i4')]
window_width = 10
time_bins = 100
dur_bins = 100
dur_max = 1.0
temperature = 1 

# custom softmax with temperature and clipping
def softmax(array, temp=1):
    return np.exp(np.clip(array/temp, 0,100))/np.exp(np.clip(array/temp, 0,100)).sum()

# sample ids from a histogram-based distribution
def sample(histogram, number_of_samples, temp):
    return np.random.choice(np.arange(len(histogram)),
                            size = number_of_samples, 
                            replace = True,
                            p = softmax(histogram, temp = temp))

# sample from specific values, quantized to bins
def sample_from_values(values, v_min, v_max, bins, number_of_samples, temp):
    values_normalized = np.clip((values - v_min)/(v_max-v_min), 0 , 1)*bins
    histogram = np.zeros(bins+1)
    for val in values_normalized.astype(int):
        histogram[val] += 1
    new_value_idx = sample(histogram, number_of_samples, temp)
    new_values = v_min + new_value_idx/bins * ((v_max-v_min))
    return new_values

# save the performance with note noise
def save_current_stack(nas, filename, performance):
    full_note_array = rfn.stack_arrays(nas).data
    # print(full_note_array, full_note_array[["pitch"]])
    pitch_sort_idx = np.argsort(full_note_array["pitch"])
    full_note_array = full_note_array[pitch_sort_idx]
    onset_sort_idx = np.argsort(full_note_array["onset_sec"], kind="mergesort")
    full_note_array = full_note_array[onset_sort_idx]
    ppart = pt.performance.PerformedPart.from_note_array(full_note_array)
    ppart.controls = performance[0].controls
    pt.save_performance_midi(ppart, filename)

dur_score = (m_score["onset"]+m_score["duration"]).max() - m_score["onset"].min()
dur_perf = (m_score["p_onset"]+m_score["p_duration"]).max() - m_score["p_onset"].min()
windows = np.ceil(dur_score/window_width).astype(int)
nas = [performance.note_array()[['onset_sec','duration_sec',"pitch","velocity"]][:-1],
       performance.note_array()[['onset_sec','duration_sec',"pitch","velocity"]][-1:]]
save_current_stack(nas, "orig.mid", performance)

# factors for number of notes and temperature parameters
notes_factor = [np.linspace(1.0,0.75, windows),
                np.linspace(2.0,1.25, windows),
                np.linspace(4.0,2.0, windows)]
temperature_factor = [np.linspace(1.0,0.05, windows),
                      np.linspace(4.0,1.0, windows),
                      np.linspace(5.0,1.0, windows)]

# create three versions with increasing noise
for k in range(3):
    for no, ws in enumerate(np.arange(m_score["onset"].min(),(m_score["onset"]+m_score["duration"]).max(), window_width)):
        mask = np.all((m_score["onset"] >= ws, m_score["onset"] < ws+ window_width), axis=0)
        number_of_notes = int(mask.sum() * notes_factor[k][no])
        temperature = temperature_factor[k][no]
        # sample onsets
        if number_of_notes > 0:
            p_min = stime_to_ptime_map(ws)
            p_max = stime_to_ptime_map(ws+window_width)
            new_onsets = sample_from_values(m_score["p_onset"][mask], p_min, p_max, time_bins, number_of_notes, temperature)
            # sample durtions
            print(ws)
            new_durations = sample_from_values(m_score["p_duration"][mask], 0.001, dur_max, dur_bins, number_of_notes, temperature)
            # sample pitches
            # piano keyboard distribution 88 notes from 21 to 108
            new_pitches = sample_from_values(m_score["pitch"][mask], 21, 108, 87, number_of_notes, temperature).astype(int)
            # sample velocities
            new_velocities = sample_from_values(m_score["velocity"][mask], 0, 127, 127, number_of_notes, temperature).astype(int)
            new_note_array = np.array([(o,d,p,v) for o,d,p,v in zip(new_onsets, new_durations, new_pitches, new_velocities)], dtype = dtypes)
            nas.append(new_note_array)

    save_current_stack(nas, "noise{0}.mid".format(k), performance)