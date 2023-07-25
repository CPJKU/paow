# Formal Grammar Generation with MIDI and Audio

This experiment explores the use of formal grammar for music generation.
We combine two grammars one for audio and one for MIDI generation.
The MIDI grammar contains 4 patterns and everytime a pattern is selected there is perturbation applied.
Similarly, for the audio grammar. In addition, every grammar is accompanied by a memory that keeps track of the
last selected patterns. The memory is used to select the next pattern to be generated giving more probability to the
last selected pattern to be selected again. This experiment is based on works created by the composer
Morton Feldmann, we use a soft dynamic range, a slow tempo and a repetive feeling that always repeats patterns but never quite at the same way.


## MIDI Message Generation

The MIDI Message generation is based on a formal grammar. The grammar is defined in the beginning of the `run.py` file.
The grammar is defined as a dictionary of rules. Each rule has a name and a list of possible expansions.
Each expansion represents a music pattern.
However, the grammar is not used directly. Instead, we use a perturbation of the grammar values.
Each value represents a MIDI message with relevant pitch, dynamics, timing, duration, and articulation information.
The perturbation is done by adding random values to each of the values in the grammar.
In parallel, we keep a memory containing past grammar rules. A weight is applied to each rule in the memory.
The weight is used to select the next rule to be generated. 
The weight is updated by adding higher value to the rule that was just generated.

## Audio Generation

The audio generation is also based on a formal grammar. The grammar is defined in the beginning of the `run.py` file.
This grammar contains directories of audio files separated into sound categories. In every generation step, 
a random sound is selected from the grammar extracted sound category. The sound is then played with a random combination
of effects and parameters.


## Installation

To install the dependencies run:

```bash
pip install -r requirements.txt
```

## Usage

To run the experiment run:

```bash
python run.py --generation_length 60 --output_midi_port SomeMidiDeviceName
```

### Technical equipment

Grand piano: Yamaha Disklavier Enspire Pro C1X  
Audio interface: Focusrite Scarlett 18i8  
Microphones: a pair of AKG P420  
Camera: Canon EOS 250D  