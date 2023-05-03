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


def partFromProgression(prog, quarter_duration = 4 ):
    part = pt.score.Part('P0', 'part from progression', quarter_duration=quarter_duration)
    for i, c in enumerate(prog.chords):
        for j, pitch in enumerate(c.pitches):
            addnote(pitch, part, j, i*quarter_duration, (i+1)*quarter_duration, str(j)+str(i))
    
    return part


def parttimefromrekorder(na, 
                         quarter_duration = 4,
                         num_frames = 8):
    frames = list()
    for k in range(num_frames):
        frames.append(na["pitch"][np.logical_and(na["onset_sec"] < (k+1)*1.25, na["onset_sec"] >= k*1.25)])
    time_per_div = (num_frames/10) / quarter_duration
    na["onset_sec"] = np.round(na["onset_sec"]/time_per_div)
    na["duration_sec"] = np.round(na["duration_sec"]/time_per_div)
    na["duration_sec"][na["duration_sec"] < 1] = 1   
    return na, frames

def addmelody2part(part, na, quarter_duration = 4):
    for j, note in enumerate(na):
            addnote(note["pitch"], part, j, 
                    note["onset_sec"], 
                    note["duration_sec"]+note["onset_sec"], 
                    str(j)+"_melody")