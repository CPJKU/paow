import numpy as np
from itertools import product
import string
import random


def randomword(length):
    """
    a random character generator
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def cycle_distance(u,v):
    """
    pitch class distance between two values u and v
    """
    a = np.sqrt(((u%12-v%12)%12)**2)
    b = np.sqrt(((v%12-u%12)%12)**2)
    return np.min([a, b])



def chordDistance(c1, c2):
    """
    compute the minimal pitch distance between to chords
    when every note of the second chord
    can be transposed by up to -1 / +1 octaves.
    assumes input chords as pitch-ordered np.arrays. 

    Parameters
    ----------
    c1 : np.array
        first chord
    c2 : np.array
        second chord

    Returns 
    -------
    best_adds : np.array
        the best transposition for each note of the second chord
    best_total : int
        the total distance between the two chords
        
    """
    l = min(c1.shape[0],c2.shape[0])
    c1 = c1[:l]
    c2 = c2[:l]
    local_adds = dict()
    for comb in product(np.arange(-1,1), repeat =  l):
        c=np.array(comb)
        new_c2 = c2 + 12* c
        total = np.sum(np.abs(new_c2-c1))
        local_adds[total] = c
    
    best_total = np.min(list(local_adds.keys()))
    best_adds = local_adds[best_total]
    
    return  best_adds, best_total


class Chord:
    """
    the Chord class representing a chord made of 3-4 notes of a scale.
    For diatonic scales the intervals between notes are thirds.

    Parameters
    ----------
    offset : int
        the MIDI pitch of scale degree 0
    scale : np.array
        the scale from which the chord is built
    how_many : int
        the number of notes in the chord
    root_id : int
        the index of the root in the scale

    """
    def __init__(self, 
                 offset = 48, #np.random.randint(48,60)-12, 
                 scale = np.array([0,2,4,5,7,9,11]),
                 how_many = None,
                 root_id = None
                ):
        self.offset = offset
        self.scale = scale
        if root_id is None:
            self.root_id = np.random.randint(self.scale.shape[0])
        else:
            self.root_id = root_id
        self.root = self.offset + self.scale[self.root_id]
        if how_many is None:
            self.how_many = np.random.randint(3,5)
        else:
            self.how_many = np.clip(how_many,3,4)
        if self.how_many == 3:
            self.jumps = [2,2,3]
        elif self.how_many == 4:
            self.jumps = [2,2,2,1]
        self.jumps_cs = np.cumsum([0]+ self.jumps) 
        self.inversion = 0
        self.inversion_jumps = None
        self.inversion_jumps_cs = None
        self.all_ids = None
        self.pitches = None
        self.pitch_classes = None
        self.pitch_classes_relative = None
        self.repitch = [0,0]
        self.compute_pitch()
        self.name = self.get_name()
        
    def get_name(self):
        """
        rudimentary naming convention for chords
        no difference between maj7 and dominant 7.
        suffix for inversions and chromatic alterations.
        """
        root_names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        root_name = root_names[self.root%12]
        first_jump =  cycle_distance(self.scale[(self.root_id+self.jumps[0])%self.scale.shape[0]],
                                        self.scale[self.root_id])
        if first_jump == 3:
            mod = "m"
        elif first_jump == 4:
            mod = "M"
        else:
            mod = "?"
        
        if self.how_many == 3:
            typ = ""
        elif self.how_many == 4:
            typ = "7"
            
        repitch_names = {1:"#", -1:"b"}
        if self.repitch != [0,0]:
            chromatic = "_" + str(self.repitch[0]) +repitch_names[self.repitch[1]]
        else:
            chromatic = ""
        name = root_name + mod + typ + "_" + str(self.inversion) + chromatic
        return name
        
    def compute_pitch(self):
        self.inversion_jumps = self.jumps[self.inversion:]+self.jumps[:self.inversion]
        self.inversion_jumps_cs = np.cumsum([0]+ self.inversion_jumps) 
        self.all_ids = np.array([(self.root_id+self.jumps_cs[self.inversion])%self.scale.shape[0]
                                 +self.inversion_jumps_cs[n] for n in range(self.how_many)])
        self.pitches = self.offset + np.concatenate((self.scale, self.scale+12))[self.all_ids]
        self.pitches[self.repitch[0]] += self.repitch[1]
        self.pitch_classes = self.pitches%12
        self.pitch_classes_relative = (self.pitches-self.offset)%12
        self.name = self.get_name()
        
    
    def invert(self, n):
        n %= self.how_many
        self.inversion = n
        self.compute_pitch()
        
    def add_repitch(self, idx, mod):
        mod = np.clip(mod,-1,1)
        idx %= self.how_many
        self.repitch = [idx, mod]
        self.compute_pitch()

class Progression:
    """
    the Progression class representing a sequence of chords
    """
    def __init__(self,
                 number_of_chords = 8, 
                 chords = None):
        if chords is not None:
            self.chords = chords
        else:
            self.chords = [Chord() for c in range(number_of_chords)]
        self.number_of_chords = number_of_chords
        self.id = randomword(10)
    
    
    def join(self, 
             another,
             idx = None):
        """
        create two new progressions by joining two existing ones
        where the split of chords is defined by an index array
        """
        if another.number_of_chords != self.number_of_chords:
            raise ValueError("progressions must have the same number of chords")

        if idx is None:
            idx = np.unique(np.random.randint(0,self.number_of_chords,self.number_of_chords//2))

        new_progression = Progression(number_of_chords = self.number_of_chords)
        new_another_progression = Progression(number_of_chords = self.number_of_chords)
        for k in range(8):
            if k in idx:
                new_progression.chords[k] = self.chords[k]
                new_another_progression.chords[k] = another.chords[k]
            else:
                new_progression.chords[k] = another.chords[k]
                new_another_progression.chords[k] = self.chords[k]
        return new_progression, new_another_progression
                

if __name__ == "__main__":

    a = Chord(how_many = 3, root_id = 0)

