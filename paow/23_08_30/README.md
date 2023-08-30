This experiment is another shot at transcription, this time a bit more difficult: a fantastic album by a trio of double bass, piano, and drums.
We first downloaded the mp3 from youtube, computed a source separation using Demucs, and transcribed the stems using
Basic Pitch, the ATEPP transcription model, and Ableton live's built-in drum to MIDI converter.
All instruments are played on the grand piano, the transcribed drums were (MIDI) pitched to keys closest to the drums' spectral peaks.

Unfortunately, for double bass but also for drums the transcription quality was not satisfying for any model we tried.
Any hints for open-source yet maintained transcription models for these instruments are very welcome!

Enjoy!


Generation environment:

python 3.9
Demucs: https://github.com/facebookresearch/demucs
Basic Pitch: https://github.com/spotify/basic-pitch
ATEPP: https://github.com/BetsyTang/ATEPP/tree/master/piano_transcription-master
Ableton Live
https://github.com/CPJKU/paow

Technical equipment:

Grand piano: Yamaha Disklavier Enspire ST C1X
Audio interface: Focusrite Scarlett 18i8
Microphones: a pair of AKG P420
Camera: Canon EOS 250D
