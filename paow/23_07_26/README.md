# Formal Grammar Generation with MIDI and Audio

This experiment explores the use of formal grammar for music generation for finite fixed length generation.


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
