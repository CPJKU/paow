import partitura as pt
import numpy as np

def addnote(midipitch, part, voice, start, end, idx):
    """
    adds a single note by midiptich to a part
    """
    offset = midipitch%12
    octave = int(midipitch-offset)/12
    name = [("C",0),
            ("C",1),
            ("D",0),
            ("D",1),
            ("E",0),
            ("F",0),
            ("F",1),
            ("G",0),
            ("G",1),
            ("A",0),
            ("A",1),
            ("B",0)]
    # print( id, start, end, offset)
    step, alter = name[int(offset)]
    part.add(pt.score.Note(id='n{}'.format(idx), step=step, 
                        octave=int(octave), alter=alter, voice=voice), 
                        start=start, end=end)


def partFromProgression(prog, 
                        quarter_duration = 4,
                        rhythm = None):
    part = pt.score.Part('P0', 'part from progression', quarter_duration=quarter_duration)
    if rhythm is None:
        rhythm = [(i*quarter_duration, (i+1)*quarter_duration) for i in range(len(prog.chords))]
    for i, c in enumerate(prog.chords):
        for j, pitch in enumerate(c.pitches):
            addnote(pitch, part, j, rhythm[i][0], rhythm[i][1], str(j)+str(i))
    
    return part


def parttimefromrekorder(na, 
                         quarter_duration = 4,
                         quarters = 8,
                         num_frames = 8,
                         rhythm = None):
    positions = quarter_duration * quarters
    sec_per_div = 10/quarters/quarter_duration
    if rhythm is None:
        interval = positions//num_frames
        rhythm = [(i*interval, (i+1)*interval) for i in range(num_frames)]

    frames = list()
    for k in range(num_frames):
        frames.append(na["pitch"][np.logical_and(
            na["onset_sec"] < rhythm[k][1]*sec_per_div, 
            na["onset_sec"] >= rhythm[k][0]*sec_per_div)])
    # time_per_div = (num_frames/10) / quarter_duration
    na["onset_sec"] = np.round(na["onset_sec"]/sec_per_div)
    na["duration_sec"] = np.round(na["duration_sec"]/sec_per_div)
    na["duration_sec"][na["duration_sec"] < 1] = 1   
    return na, frames


def addmelody2part(part, na, quarter_duration = 4):
    for j, note in enumerate(na):
            addnote(note["pitch"], part, j, 
                    note["onset_sec"], 
                    note["duration_sec"]+note["onset_sec"], 
                    str(j)+"_melody")
            

def progression_and_melody_to_part(progression, 
                                   melody,
                                   quarter_duration = 4,
                                   rhythm = None):
    """
    converts a progression and a melody to a partitura part
    """
    part = partFromProgression(progression,
                               quarter_duration = quarter_duration,
                               rhythm = rhythm
                               )
    na, _ = parttimefromrekorder(melody,
                                 quarter_duration = quarter_duration,
                                 num_frames = len(progression.chords)
                                )
    addmelody2part(part, na)
    return part