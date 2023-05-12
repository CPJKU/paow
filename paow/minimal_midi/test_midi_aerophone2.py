import mido
import warnings
import numpy as np

def scalify(input_array, 
            offset = 0, 
            scale = np.array([0,0,2,3,3,5,5,7,7,9,10,10])):
    """
    forces notes in an array to some scale
    """
    output_array = (input_array-offset)-(input_array-offset)%12 + scale[(input_array-offset)%12]+ offset
    return output_array


def f():
    if oport is not None:
        oport.close()
    if iport is not None:
        iport.close()
    
    
def g():
    sounding_notes = {}
    for msg in iport:
        note_on = msg.type == "note_on"
        note_off = msg.type == "note_off"

        if (note_on or note_off):
                    
            # hash sounding note
            pitch =  msg.note

            # start note if it's a 'note on' event with velocity > 0
            if note_on and msg.velocity > 0:


                repitch = scalify(pitch-12)
                # save the onset time and velocity
                sounding_notes[pitch] = (repitch)
                print(pitch, repitch)
                oport.send(mido.Message("note_on",
                                channel=msg.channel,
                                note=repitch,
                                velocity=msg.velocity))
        

            # end note if it's a 'note off' event or 'note on' with velocity 0
            elif note_off or (note_on and msg.velocity == 0):

                if pitch not in sounding_notes:
                    warnings.warn("ignoring MIDI message %s" % msg)
                    continue

                else:
                    
                    oport.send(mido.Message("note_off",
                                channel=msg.channel,
                                note=sounding_notes[pitch],
                                velocity=0))
                    
                    del sounding_notes[pitch]
    
            
if __name__ == "__main__":
    
    print(mido.get_output_names(), mido.get_input_names())

    oport = mido.open_output( 'seq 2')
    iport  = mido.open_input('3- AE-30 3')