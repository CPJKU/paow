import os
import partitura as pt
import numpy as np

Midi_path = r"PATH0"
Out_path = r"PATH1"
cur_time = 0
note_array = []

for l in range(10):

    mid = pt.load_performance_midi(os.path.join(Midi_path, 'other_cutsample_{}_basic_pitch.mid'.format(l)))
    print(l, mid.note_array()[0],mid.note_array()[-1] )
    for note in mid[0].notes:
        note['note_on'] += cur_time
        note['note_off'] += cur_time
        note['sound_off'] += cur_time
        note_array.append(tuple([note['midi_pitch'], note['note_on'], note['note_off'] - note['note_on'], note['velocity']]))

    cur_time += 60*5

performed_part = pt.performance.PerformedPart.from_note_array(np.array(note_array,dtype=[("pitch", "i4"),
           ("onset_sec", "f4"),
           ("duration_sec", "f4"),
           ("velocity", "i4")
           ]))

pt.save_performance_midi(performed_part, os.path.join(Out_path, "other.mid"))