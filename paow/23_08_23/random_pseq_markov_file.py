import numpy as np


def euclidean(cycle = 16, 
              pulses = 4, 
              offset= 0):
    """
    compute an Euclidean rhythm
    """
    rhythm = []
    bucket = cycle-pulses
    for step in range(cycle):
        bucket = bucket + pulses

        if (bucket >= cycle):
            bucket = bucket - cycle
            rhythm.append(step)

    rhythm_array = np.array(rhythm)
    rhythm_array = (rhythm_array + offset) % cycle
    rhythm_array = np.sort( rhythm_array)
    return rhythm_array


def pbinds(file,
           how_many_seqs=2,
           euc_seq_min=16,
           euc_seq_max=16,
           pulses_min= 4,
           pulses_max = 6,
           loop_len = 3.0):
    
    file.write("// start a server and a MIDIClient and define a MIDIOut with the variable name m.\n")
    file.write("(\n")
    file.write("var markovmatrix;\n")
    file.write("var no_of_seqs = {};\n".format(how_many_seqs*3-2))
    file.write("var currentstate = {}.rand;\n".format(how_many_seqs*3-2))
    first = list()
    second = list()
    third = list()
    for pseq_id in range(how_many_seqs*3):

        if pseq_id %3 == 0:
            first.append("\\x{0}".format(pseq_id))
            seq_len = np.random.randint(euc_seq_min, euc_seq_max+1)
            pulses = np.random.randint(pulses_min, np.min((pulses_max+1, seq_len)))
            pitch_plus = 0
        elif pseq_id %3 == 1:
            second.append("\\x{0}".format(pseq_id))
            seq_len = np.random.randint(euc_seq_min, euc_seq_max+1)
            pulses = np.random.randint(pulses_min, np.min((pulses_max+1, seq_len)))
            pitch_plus = 0
        else:
            third.append("\\x{0}".format(pseq_id))
            # seq_len = np.random.randint(euc_seq_min, euc_seq_max+1)
            pulses = np.max((1, np.floor(pulses/2).astype(int)))
            pitch_plus = -8

        
        pulse_onsets = euclidean(seq_len,pulses, np.random.randint(2))
        pseq_array = ["Rest(0)"]*seq_len
        for po in pulse_onsets:
            if pitch_plus == 0:
                pseq_array[po] = "[{1:d},{0:d}]".format(2+pseq_id%7, 2+pseq_id%7+ 14)
            else:
                pseq_array[po] = "[{1:d},{0:d}]".format(pseq_id%2 + pitch_plus, pseq_id%2 + pitch_plus-7)
        pseq_string = "Pseq(["+ ",".join(pseq_array)+"],1)"

        file.write('Pdef(\\x{0}, {{ Pbind(\\ctranspose, -1, \\degree, {1}, \\dur,{3}/{2} , \\amp, Pseq([0.3,0.31,0.29],inf))}});\n'.format(pseq_id,pseq_string,seq_len, loop_len))

    first =  [val for val in first for _ in (0, 1, 3)][2:]
    second =  [val for val in second for _ in (0, 1, 3)][1:-1]
    third =  [val for val in third for _ in (0, 1, 3)][0:-2]

    file.write("{inf.do{")
    file.write("(Pdef([" + ",".join(first)+ "].at(currentstate)) <> (type: \midi, midiout: m)).play;\n")
    file.write("(Pdef([" + ",".join(second)+ "].at(currentstate)) <> (type: \midi, midiout: m)).play;\n")
    file.write("(Pdef([" + ",".join(third)+ "].at(currentstate)) <> (type: \midi, midiout: m)).play;\n")

    file.write("currentstate = (currentstate-1..currentstate+3).wchoose([0.3,18,3,1,0.3].normalizeSum);\n")
    file.write("currentstate.postln;\n")
    file.write("if ( currentstate>(no_of_seqs - 1),   {currentstate = 0; }, {  } );\n")
    file.write("if ( currentstate<0,   {currentstate = 0; }, {  } );\n")
    file.write("{}.wait;\n".format(seq_len))
    file.write("};}.fork;\n")
    file.write(")\n")


if __name__ == "__main__":

    with open("markov.scd", "w") as f:
        pbinds(f, 31, 16, 24, 6, 18, 3.4)
