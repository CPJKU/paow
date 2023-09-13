#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment orders music performances.

Enjoy!
"""
import partitura as pt
import numpy as np
import numpy.lib.recfunctions as rfn
import glob
import os

# save the performance with note noise
def save_current_stack(note_array, 
                       filename,
                       performance):
    ppart = pt.performance.PerformedPart.from_note_array(note_array)
    ppart.controls = performance[0].controls
    pt.save_performance_midi(ppart, filename)

def update_onset_times(m_note_array):
    m_note_array["onset_sec"] = m_note_array["onset_sec"].min()
    for idx in np.arange(1,len(m_note_array)):
        m_note_array[idx]["onset_sec"] = m_note_array[idx-1]["onset_sec"] + m_note_array[idx-1]["onset_ioi"]
    return m_note_array

# get an original performance

for fp in glob.glob("midis/*.mid"):
    piece_name = os.path.basename(fp)
    performance = pt.load_performance_midi(fp)
    note_array = performance.note_array()[['onset_sec','duration_sec',"pitch","velocity", "id"]]

    note_onset_ioi = np.diff(note_array["onset_sec"])
    note_onset_ioi = np.append(note_onset_ioi, np.median(note_onset_ioi)) # add a median IOI to the end

    merged_note_array = rfn.append_fields(note_array, "onset_ioi", note_onset_ioi, dtypes='<f4', 
                                        fill_value=-1, usemask=True, asrecarray=False).data 

    seg_lengths = np.arange(2,2000)
    seg_lengths_cs = np.cumsum(seg_lengths)
    seg_lengths_csi = np.cumsum(seg_lengths[::-1])

    number_of_notes = len(merged_note_array)
    seg_lengths_to_use = seg_lengths[seg_lengths_cs < number_of_notes]
    seg_slices = np.cumsum(seg_lengths_to_use[::-1])
    seg_slices = np.insert(seg_slices, 0, 0, axis=0)
    seg_slices = np.append(seg_slices, number_of_notes)

    for sort_field in [("pitch", "duration_sec"), ("velocity","pitch"),("duration_sec","pitch")]:

        mnas = list()
        for seg_start, seg_end in zip(seg_slices[:-1],seg_slices[1:]): 
            mna = np.copy(merged_note_array[seg_start:seg_end])
            sort_idx = np.lexsort((
                        #note_array["duration_sec"], 
                        mna[sort_field[1]], 
                        mna[sort_field[0]]
                ))
            mna = mna[sort_idx]
            mnas.append(mna)

        fmna = rfn.stack_arrays(mnas).data

        fmna = update_onset_times(fmna)
        save_current_stack(fmna, "sorted_midis/order_{0}_{1}.mid".format(piece_name,sort_field[0]), performance)