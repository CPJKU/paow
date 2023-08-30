import numpy as np
import os
import librosa
import soundfile as sf

segment_length=60*5
in_path = r"PATH0"
out_path = r"PATH1"

# LOAD
signal = librosa.load(in_path)

sr = signal[1]
sig_len = signal[0].shape[0]

snippets = int(np.ceil(sig_len / (sr*segment_length)))
for i in range(snippets):
    sf.write(os.path.join(out_path, 'other_cutsample_{}.wav'.format(i)),
             signal[0][(i)*sr*segment_length:(i+1)*sr*segment_length] , sr)