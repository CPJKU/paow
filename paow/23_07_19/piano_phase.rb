# Piano Phase in Sonic Pi

# starts on E4 = 64
phase1 = (ring 64,66,71,73,74,66,64,73,71,66,74,73)
phase21 = (ring 64,66,71,73,74,66,71,73)
phase22 = (ring 64,76,69,71,74,76,69,71)
phase3 = (ring 69,71,74,76)

# speed roughly 16th notes at 130 bpm
note_duration_ref = 60.0/(130.0*4.0)
# each segment 15 min
target_duration = 60.0 * 15.0
# how many notes fit in there
notes_in_fifteen_min =  target_duration / note_duration_ref

# pattern length
pattern1 = 12
# how many patterns fit in there
number_of_patterns1 = notes_in_fifteen_min.to_i / pattern1
# actual duration
actual_duration1 = number_of_patterns1 * pattern1 * note_duration_ref
# add 12 notes that should be played in the same time
note_duration1 =  actual_duration1 / ((number_of_patterns1 + 1) * pattern1)

# pattern length
pattern2 = 8
# how many patterns fit in there
number_of_patterns2 = notes_in_fifteen_min.to_i / pattern2
# actual duration
actual_duration2 = number_of_patterns2 * pattern2 * note_duration_ref
# add 12 notes that should be played in the same time
note_duration2 =  actual_duration2 / ((number_of_patterns2 + 1) * pattern2)

# pattern length
pattern3 = 4
# how many patterns fit in there
number_of_patterns3 = notes_in_fifteen_min.to_i / pattern3
# actual duration
actual_duration3 = number_of_patterns3 * pattern3 * note_duration_ref
# add 12 notes that should be played in the same time
note_duration3 =  actual_duration3 / ((number_of_patterns3 + 1) * pattern3)

def midi_n (port: "im_one_1", channel: 0, pitch: 48, velocity: 64, duration: 0.5)
  # puts port, channel, pitch, velocity, duration
  midi_note_on pitch, port: port, velocity: velocity, channel: channel
  sleep duration
  midi_note_off pitch, port: port, channel: channel, velocity: 0
end


in_thread do
  (number_of_patterns1*pattern1).times do
    len = rrand(0.1, 0.1)
    vel = rrand(40,50)
    midi_n pitch: phase1.tick, channel: 0 ,duration: len, velocity: vel
    sleep note_duration_ref-len
  end
  
  (number_of_patterns2*pattern2).times do
    len = rrand(0.1, 0.1)
    vel = rrand(40,50)
    midi_n pitch: phase21.tick, channel: 0 ,duration: len, velocity: vel
    sleep note_duration_ref-len
  end
  
  (number_of_patterns3*pattern3).times do
    len = rrand(0.01, 0.1)
    vel = rrand(40,50)
    midi_n pitch: phase3.tick, channel: 0 ,duration: len, velocity: vel
    sleep note_duration_ref-len
  end
end



in_thread do
  (number_of_patterns1*pattern1 + pattern1).times do
    len = rrand(0.1, 0.1)
    vel = rrand(80,90)
    midi_n pitch: phase1.tick, channel: 10 ,duration: len, velocity: vel
    sleep note_duration1-len
  end
  
  (number_of_patterns2*pattern2 + pattern2).times do
    len = rrand(0.1, 0.1)
    vel = rrand(80,90)
    midi_n pitch: phase22.tick, channel: 10 ,duration: len, velocity: vel
    sleep note_duration2-len
  end
  
  (number_of_patterns3*pattern3 + pattern3).times do
    len = rrand(0.01, 0.1)
    vel = rrand(80,90)
    midi_n pitch: phase3.tick, channel: 10 ,duration: len, velocity: vel
    sleep note_duration3-len
  end
end