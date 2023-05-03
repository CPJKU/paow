import numpy as np


def euclidean(cycle = 16, pulses = 4, offset= 0):
    """
    compute an Euclidean rhythm
    """
    rhythm = []
    # pulses = how_many_notes-1
    bucket = cycle-pulses
    timepoint = 0
    for step in range(cycle):
        # print(bucket, rhythm) 
        bucket = bucket + pulses

        if (bucket >= cycle):
            bucket = bucket - cycle
            rhythm.append(timepoint)
        
        timepoint += 1

    rhythm_array = np.array(rhythm)
    rhythm_array = (rhythm_array + offset) % cycle
    rhythm_array = np.sort( rhythm_array)
    return rhythm_array

if __name__ == "__main__":
    a = euclidean()