PAOW! #23 

In this experiment, we spatialize individual voices in performances of Bach Fugues.
The performances come from the (n)ASAP dataset, which gives us the necessary annotations to separate the MIDI performances by voice.
We then record each voice individually and spatialize it in ambisonic audio using the IEM plug-in suite.
The spatial position of each voice is procedurally controlled by a visual swarm algorithm implemented in p5js which sends MIDI CC to DAW.
The ambisonic tracks are finally mixed to binaural stereo, so headphones are necessary.
The stream video shows all voices being played on the grand piano at the same time as in the original performances.

Enjoy!


Generation environment:

Python 3.9  
partitura: https://github.com/CPJKU/partitura
p5js swarm: https://editor.p5js.org/oemei/full/3cVYsgCjq
IEM plug-in suite for spatialization: https://plugins.iem.at/
(n)ASAP dataset: https://github.com/CPJKU/asap-dataset

Technical equipment:

Grand piano: Yamaha Disklavier Enspire ST C1X
Audio interface: Focusrite Scarlett 18i8
Microphones: a pair of AKG P420
Camera: Canon EOS 250D
