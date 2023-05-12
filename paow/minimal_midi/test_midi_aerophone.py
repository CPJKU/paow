import mido

print(mido.get_output_names(), mido.get_input_names())
# if oport is not None:
#     oport.close()
oport = mido.open_output( 'AE-30 1')
iport  = mido.open_input('AE-30 0')

def f(no, val):
    oport.send(mido.Message("control_change",
                                channel=0,
                                control=no, # control number k, can be mapped later as you like
                                value=val))
    
def g():
    for msg in iport:
        if msg.is_cc():
            # 2 = breath, 3 too?, 11,9
            # 4 button
            if msg.control == 95:# in [2,3,9,11]: 
                print(msg)
        
def h():
    iport.close()
    oport.close()