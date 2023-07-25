import mido
import time

print(mido.get_output_names())
output_name = mido.get_output_names()[-1]
o = mido.open_output(output_name)


for k in range(21,100):
    o.send(mido.Message("note_on", note = k, velocity = 30))
time.sleep(0.5)
for k in range(21,100):
    o.send(mido.Message("note_off", note = k, velocity = 0))
    
time.sleep(0.5)

for k in range(21,77):
    o.send(mido.Message("note_on", note = k, velocity = 30))
time.sleep(0.5)
for k in range(21,77):
    o.send(mido.Message("note_off", note = k, velocity = 0))
