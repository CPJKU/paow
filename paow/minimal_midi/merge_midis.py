import os
import partitura as pt
import numpy as np
import glob

def new_note(note, cur_time, start_offset):
    new_note = dict()
    new_note['note_on'] = note['note_on'] + cur_time - start_offset
    new_note['note_off'] = note['note_off'] + cur_time - start_offset
    new_note['sound_off'] = note['sound_off'] + cur_time - start_offset
    new_note['pitch'] = note['pitch']
    new_note['velocity'] = note['velocity']
    return new_note

if __name__ == "__main__":
    Midi_path = r"PATH0" # directory for input midi files
    Out_path = r"PATH1" # directory for output midi file
    cur_time = 0 # time counter starting point
    note_array = []
    OFFSET = 1.0 # time between input midi files (sec)

    # loop over input files and concatenate notes
    for file in glob.glob(os.path.join(Midi_path, '*.mid')):
        mid = pt.load_performance_midi(file)
        pna = mid.note_array()
        START = np.min(pna["onset_sec"]) 
        END = np.max(pna["onset_sec"]+pna["duration_sec"]) 
        DURATION = END - START
        print(file, mid.note_array()[0],mid.note_array()[-1] )
        for note in mid[0].notes:
            new_note_ = new_note(note, cur_time, START)
            note_array.append(tuple([new_note_['midi_pitch'], 
                                     new_note_['note_on'], 
                                     new_note_['note_off'] - new_note_['note_on'], 
                                     note['new_note_']]))

        cur_time += DURATION + OFFSET

    # create a performedpart from the collected notes
    performed_part = pt.performance.PerformedPart.from_note_array(np.array(note_array,dtype=[("pitch", "i4"),
                                                                                            ("onset_sec", "f4"),
                                                                                            ("duration_sec", "f4"),
                                                                                            ("velocity", "i4")]))
    # save it 
    pt.save_performance_midi(performed_part, os.path.join(Out_path, "merged_midi.mid"))