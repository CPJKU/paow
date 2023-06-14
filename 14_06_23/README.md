# In Search of the Mystic Art of Piano Playing I: Hanon

In Search of the Mystic Art of Piano Playing (ISMAPP) is a series of musical experiments exploring the complex art of how humans learn to play the piano.

The initial installment of this series explores one of the most fundamental, yet feared parts of learning to play an instrument: developing technique. In the case of piano, few other books are more influential (and infamous) than Charles-Louis Hanon's [*The Virtuoso Pianist in 60 Exercises*](https://en.wikipedia.org/wiki/The_Virtuoso_Pianist_in_60_Exercises), commonly referred to simply as **The Hanon**. Published in 1873, this book is a compilation of exercises designed to enhance the pianist's speed, accuracy, finger strength and independence, as well as improve wrist flexibility. The exercises are meant to be played as precisely as possible, without tempo changes and with constant loudness and true independence of the hands, i.e., as *machine-like* as possible. While playing the exercises with perfect accuracy is impossible for human pianists, it is a trivial task for a MIDI capable instrument such as the Disklavier.

Instead of just having the Dikslavier play like a machine, we explore the question what it means to play like a human by using an AI model trained to play expressively like a human to generate an **expressive** performance of the Hanon. This experiment aims to highlight our conception of what an expressive performance is, as well as the limitations of generative AI systems that imitate the way humans perform a specific task.

In this experiment, we use the [Basis Mixer](http://www.carloscancinochacon.com/documents/thesis/Cancino-JKU-2018.pdf), a neural  network-based model that renders a human like performance of a piece of music given its score, in terms of variations in dynamics, tempo, timing and articulation. This Basis Mixer was trained on a corpus of performances of (nearly) the entire solo piano ouvre by [Frédéric Chopin](https://en.wikipedia.org/wiki/Frédéric_Chopin) played by [Nikita Magaloff](https://en.wikipedia.org/wiki/Nikita_Magaloff), one of the last "Romantic" pianists of the 20th Century.


## Generation environment

* Python 3.9
* mido / python-rtmidi
* numpy
* pytorch
* partitura
* basismixer
* https://github.com/CPJKU/paow/tree/main/paow/14_06_23

## Technical equipment

* Grand piano: Yamaha disklavier Enspire Pro C1X
* Audio interface: Focusrite Scarlett 18i8
* Microphones: a pair of AKG P420
* Camera 1: Canon EOS 250D
* Camera 2: GoPro Hero 11 
