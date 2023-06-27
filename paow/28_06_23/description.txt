This experiment uses the Pop Music Transformer [Huang et al.] fine-tuned for 26 epochs on a small dataset of transcribed (using Onsets and Frames [Hawthorne et al.]) and cleaned Mozart sonatas to generate 16 bar piano pieces.

The pre-trained model is the "REMI-tempo-checkpoint" provided in the original repository.

The Mozart pieces used for fine-tuning are: K309, K311, K545, K570, and K576.

The MIDI files are cherry-picked! :)


Generation environment:

Pop Music Transformer: https://github.com/YatingMusic/remi
Fine-tuned weights: https://drive.google.com/drive/folders/1wf1Wn2FNQ4Xly1pXb3sOaejd0cxUCjt9?usp=sharing
Python 3.7.16
tensorflow-gpu 1.14.0
miditoolkit 0.1.16
REAPER


References:

[Huang et al.]: https://arxiv.org/abs/2002.00212
[Hawthorne et al.]: https://arxiv.org/abs/1710.11153


Technical equipment:

Grand piano: Yamaha disklavier Enspire Pro C1X
Audio interface: Focusrite Scarlett 18i8
Microphones: a pair of AKG P420
Camera 1: Canon EOS 250D
Camera 2: Gopro 11 
