#%%
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this experiment we mashup the time signature of some Bach Fugues by manipulating the velocity and duration of the downbeat notes in otherwise deadpan performances.

Enjoy!
"""
import os
import glob
import numpy as np
import partitura as pt
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import warnings
warnings.filterwarnings("ignore")

bach_fugues_xml = os.path.join("path/to/your/data/..../bach_js/the_well-tempered_clavier_*/*2.mxl") # see readme for score data repo 
fugues = sorted(glob.glob(bach_fugues_xml))
out_midi_path = os.path.join(os.getcwd(), "midi")

TIMESIG_FUGUES_DICT = {
    '4/4': ['BWV846', 'BWV847', 'BWV848', 'BWV850', 'BWV852', 'BWV853', 'BWV854', 'BWV857', 'BWV858', 'BWV861', 'BWV862', 'BWV863', 'BWV865', 'BWV868', 'BWV869', 'BWV871', 'BWV872', 'BWV875', 'BWV877', 'BWV883', 'BWV886', 'BWV888', 'BWV889'],
    '3/8': ['BWV856', 'BWV884', 'BWV893'],
    '6/8': ['BWV860', 'BWV887'],
    '9/8': ['BWV864'],
    '6/16': ['BWV880'],
    '12/16': ['BWV873']
}

DOWNBEAT_VEL = 74
WEAK_DOWNBEAT_VEL = 64
DOWNBEAT_ARTLEN_FACTOR = 1.5
WEAK_DOWNBEAT_ARTLEN_FACTOR = 1.3

def get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig, bpm, midi_save_path):
    score = pt.load_musicxml(fugue_xml) # extract score
    part = pt.score.merge_parts(score.parts) # b/c each voice has its own part
    # create performance part and pna from score
    # note: single bpm value will be treated as beat period, i.e. 60/bpm
    ppart = pt.utils.music.performance_from_part(part, bpm=bpm, velocity=42)
    sna = score.note_array(include_metrical_position=True)
    
    pna = ppart.note_array()
    for i, is_downbeat in enumerate(sna['is_downbeat']):
        if is_downbeat == 1:
            pna[i]['velocity'] = 64
    
    ppart_downbeat_dead = ppart.from_note_array(pna)
    perf_dp = os.path.join(midi_save_path, f'{fugue_number}_{time_sig}_downbeat_deadpan.mid')
    pt.save_performance_midi(ppart_downbeat_dead, perf_dp)
    
    return part, ppart

def mashup_timesig(orig_timesig, new_timesig, fugue_number, part, ppart, midi_save_path):
    
    sna = part.note_array()
    pna = ppart.note_array()
    
    if orig_timesig == '44' and new_timesig == '34':
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 3, 0, 1)
    
    if orig_timesig == '44' and new_timesig == '68':
        sna_tmp_mask = np.where(sna['onset_beat'] % 3, 0, 1)
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 1.5, 0, 2)
        sna_new_timesig_mask[sna_tmp_mask == 1] = 1
    
    elif orig_timesig[-1] == '8' and new_timesig == '24':
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 4, 0, 1)
    elif orig_timesig[-1] == '8' and new_timesig == '34':
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 6, 0, 1)
    elif orig_timesig[-1] == '8' and new_timesig == '44':
        sna_tmp_mask = np.where(sna['onset_beat'] % 8, 0, 1)
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 4, 0, 2)
        sna_new_timesig_mask[sna_tmp_mask == 1] = 1
        
    elif orig_timesig[-2:] == '16' and new_timesig == '24':
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 8, 0, 1)
    elif orig_timesig[-2:] == '16' and new_timesig == '34':
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 12, 0, 1)
    elif orig_timesig[-2:] == '16' and new_timesig == '44':
        sna_tmp_mask = np.where(sna['onset_beat'] % 16, 0, 1)
        sna_new_timesig_mask = np.where(sna['onset_beat'] % 8, 0, 2)
        sna_new_timesig_mask[sna_tmp_mask == 1] = 1
    
    for i, is_downbeat in enumerate(sna_new_timesig_mask):
        if is_downbeat == 1:
            pna[i]['velocity'] = DOWNBEAT_VEL
        if is_downbeat == 2:
            pna[i]['velocity'] = WEAK_DOWNBEAT_VEL
    ppart_vel = ppart.from_note_array(pna)
    pt.save_performance_midi(ppart_vel, os.path.join(midi_save_path, f'{fugue_number}_{orig_timesig}-to-{new_timesig}_vel.mid'))
    
    # change duration slightly, without changing onsets of other notes
    pna = ppart.note_array()
    for i, is_downbeat in enumerate(sna_new_timesig_mask):
        if is_downbeat == 1:
            pna[i]['duration_sec'] = pna[i]['duration_sec'] * DOWNBEAT_ARTLEN_FACTOR
        if is_downbeat == 2:
            pna[i]['duration_sec'] = pna[i]['duration_sec'] * WEAK_DOWNBEAT_ARTLEN_FACTOR
    ppart_dur = ppart.from_note_array(pna)
    pt.save_performance_midi(ppart_dur, out = os.path.join(midi_save_path, f'{fugue_number}_{orig_timesig}-to-{new_timesig}_dur.mid'))

    # change velocity and duration
    pna = ppart.note_array()
    for i, is_downbeat in enumerate(sna_new_timesig_mask):
        if is_downbeat == 1:
            pna[i]['velocity'] = DOWNBEAT_VEL
            pna[i]['duration_sec'] = pna[i]['duration_sec'] * DOWNBEAT_ARTLEN_FACTOR
        if is_downbeat == 2:
            pna[i]['velocity'] = WEAK_DOWNBEAT_VEL
            pna[i]['duration_sec'] = pna[i]['duration_sec'] * WEAK_DOWNBEAT_ARTLEN_FACTOR
    ppart_vel_dur = ppart.from_note_array(pna)
    pt.save_performance_midi(ppart_vel_dur, out = os.path.join(midi_save_path, f'{fugue_number}_{orig_timesig}-to-{new_timesig}_vel_dur.mid'))
    
    return None

for fugue_xml in fugues:
    
    fugue_number = fugue_xml.split("/")[-1].split("-")[1]    
    
    if fugue_number in TIMESIG_FUGUES_DICT['4/4']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='44', bpm=64, midi_save_path = out_midi_path)
        new_timesigs = ['34', '68']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='44', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)
    
    elif fugue_number in TIMESIG_FUGUES_DICT['3/8']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='38', bpm=160, midi_save_path = out_midi_path)
        new_timesigs = ['24', '34', '44']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='38', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)
    
    elif fugue_number in TIMESIG_FUGUES_DICT['6/8']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='68', bpm=160, midi_save_path = out_midi_path)
        new_timesigs = ['24', '34', '44']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='68', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)
    
    elif fugue_number in TIMESIG_FUGUES_DICT['9/8']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='98', bpm=160, midi_save_path = out_midi_path)
        new_timesigs = ['24', '34', '44']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='98', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)
    
    elif fugue_number in TIMESIG_FUGUES_DICT['6/16']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='616', bpm=360, midi_save_path = out_midi_path)
        new_timesigs = ['24', '34', '44']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='616', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)

    elif fugue_number in TIMESIG_FUGUES_DICT['12/16']:
        part, ppart = get_downbeat_deadpan_from_scorexml(fugue_number, fugue_xml, time_sig='1216', bpm=360, midi_save_path = out_midi_path)
        new_timesigs = ['24', '34', '44']
        for new_timesig in new_timesigs:
            mashup_timesig(orig_timesig='1216', new_timesig=new_timesig, fugue_number=fugue_number, part=part, ppart=ppart, midi_save_path = out_midi_path)
            
    else:
        continue