import os
import partitura as pt
import numpy as np

Midi_address = 'MIDIs/'
dir = os.listdir(Midi_address)

cur_time = 0
note_array = []

for file in dir:

    mid = pt.load_performance_midi(Midi_address+file)

    for note in mid[0].notes:
        note['note_on'] += cur_time
        note['note_off'] += cur_time
        note['sound_off'] += cur_time
        note_array.append(tuple([note['midi_pitch'], note['note_on'], note['note_off'] - note['note_on'], note['velocity']]))

    cur_time = mid[0].notes[-1]['note_off'] + 3

performed_part = pt.performance.PerformedPart.from_note_array(np.array(note_array,dtype=[("pitch", "i4"),
           ("onset_sec", "f4"),
           ("duration_sec", "f4"),
           ("velocity", "i4")
           ]))

pt.save_performance_midi(performed_part, 'wannabe_mozert.mid')