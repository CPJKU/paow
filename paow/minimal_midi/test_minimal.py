import mido
import time

print(mido.get_output_names())

ms = mido.Message("note_on", note = 64, velocity = 54)
me = mido.Message("note_off", note = 64, velocity = 0)

output_name = mido.get_output_names()[-1]
o = mido.open_output(output_name)


for k in range(19):
    o.send(ms)
    time.sleep(0.5)
    o.send(me)
    time.sleep(0.1)
