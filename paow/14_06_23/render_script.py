#!/usr/bin/env python
"""
This program generates an expressive performance of an input music score
(in any format supported by the Partitura package) using a (trained)
predictive model.
"""
import argparse
import json
import logging
import os
import sys
import warnings

from typing import Iterable, Dict, List, Tuple

import numpy as np
import torch
from basismixer import TOY_MODEL_CONFIG
from basismixer.performance_codec import get_performance_codec
from basismixer.predictive_models import FullPredictiveModel, construct_model
from basismixer.utils import (
    DEFAULT_VALUES,
    RENDER_CONFIG,
    get_all_output_names,
    get_default_values,
    load_score,
    post_process_predictions,
    sanitize_performed_part,
)
from partitura import save_match, save_performance_midi
from partitura.musicanalysis import make_note_feats
from partitura.score import merge_parts, remove_grace_notes, Part

logging.basicConfig(level=logging.INFO)


warnings.filterwarnings("ignore")

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


def load_model(
    model_config: Iterable,
    default_values: Dict = DEFAULT_VALUES,
) -> Tuple[FullPredictiveModel, List[str]]:
    """
    Load a saved model

    Parameters
    ----------
    model_config : iterable
        A list of tuples each containing the filename of the config file
        of the model and the filename of the parameters of the model.
    default_values : dict
        Default values for the parameters not included in the trained
        model(s) (e.g., the models might just be predicting velocity, and
        the rest of the parameters (beat_period, timing, etc.)
        will be set to these parameters.

    Returns
    -------
    full_model : basismixer.predictive_models.FullPredictiveModel
       An instance of a FullPredictiveModel for generating expressive
       performances.
    output_names : list
       List of the expressive parameters included in the models loaded
       from `model_config`.
    """

    # Load the models
    models = []
    for con, par in model_config:
        # Load config file
        model_config = json.load(open(con))
        # Load the parameters
        params = torch.load(
            par,
            map_location=torch.device("cpu"),
        )["state_dict"]
        # Construct the model according to its configuration and
        # set the parameters
        model = construct_model(
            model_config,
            params,
            device=torch.device("cpu"),
        )
        # append the model to the list of models
        models.append(model)

    # Get all output names (expressive parameters) predicted by the models
    output_names = list(
        set(
            [
                name
                for out_name in [m.output_names for m in models]
                for name in out_name
            ]
        )
    )
    # Get the name of the inputs (basis functions) included in the models
    input_names = list(
        set(
            [
                name
                for in_name in [m.input_names for m in models]
                for name in in_name
            ]
        )
    )
    input_names.sort()
    output_names.sort()

    # Get the appropriate list of expressive parameters for generating
    # a performance
    all_output_names = get_all_output_names(output_names)
    # Get the default values for those parameters not predicted by the
    # loaded models
    def_values = get_default_values(default_values, all_output_names)
    # Construct the full model
    full_model = FullPredictiveModel(
        models=models,
        input_names=input_names,
        output_names=all_output_names,
        default_values=def_values,
    )
    # Set of expressive parameters not included in the predicted models
    not_in_model_names = set(all_output_names).difference(output_names)

    LOGGER.info(
        "Trained models include the following parameters:\n"
        + "\n".join(output_names)
        + "\n\nThe following parameters will use default values:\n"
        + "\n"
        + "\n".join(
            [
                "{0}:{1:.2f}".format(k, default_values[k])
                for k in not_in_model_names
            ]
        )
    )

    return full_model, output_names


def compute_basis_from_score(
    score_fn: str,
    input_names: List[str],
) -> Tuple[np.ndarray, Part]:
    """
    Load a score and extract input score features through the basis functions

    Parameters
    ----------
    score_fn : str
        Filename of the score. Must be in one of the formats supported
        by partitura.
    input_names : list
        List of input basis functions to extract score features.
        See `basismixer.basisfunctions` for the full list of functions
        supported

    Returns
    -------
    basis : np.ndarray
        A 2D array with dimensions (n_notes, n_basis_functions), where n_notes
        is the number of notes in the score and
        n_basis_functions == len(input_names) is the number of basis functions.
        Each i-th row in this array corresponds to the basis functions
        evaluated for the i-th note in the score. The order of the notes is
        the same as in `part.notes_tied` (see below).
    part : partitura.score.Part
        A `Part` object representing the score.
    """
    # Load score
    part = merge_parts(load_score(score_fn))
    # Delete grace notes
    remove_grace_notes(part)
    # Compute basis functions
    _basis, bf_names = make_note_feats(
        part, list(set([bf.split(".")[0] for bf in input_names]))
    )
    basis = np.zeros((len(_basis), len(input_names)))
    for i, n in enumerate(input_names):
        try:
            ix = bf_names.index(n)
        except ValueError:
            continue
        basis[:, i] = _basis[:, ix]

    return basis, part


def predict(
    model_config: Iterable,
    score_fn: str,
    default_values: dict = DEFAULT_VALUES,
) -> Tuple[np.ndarray, FullPredictiveModel, Part]:
    """
    Main method for predicting a performance.

    Parameters
    ----------
     model_config : iterable
        A list of tuples each containing the filename of the config
        file of the model and the filename of the parameters of the model.
    score_fn : str
        Filename of the score. Must be in one of the formats supported
        by partitura.
    default_values : dict
        Default values for the parameters not included in the trained
        model(s) (e.g., the models might just be predicting velocity,
        and the rest of the parameters (beat_period, timing, etc.)
        will be set to these parameters.

    Returns
    -------
    predictions : structured array
        Numpy structured array containing the predictions by the model.
        The fields are the names of the parameters specified by the `model`.
    model : basismixer.predictive_models.FullPredictiveModel
       An instance of a FullPredictiveModel for generating expressive
       performances.
    part : partitura.score.Part
        A `Part` object representing the score.
    """
    # Load predictive model
    model, predicted_parameter_names = load_model(
        model_config, default_values=DEFAULT_VALUES
    )

    # Compute score representation
    basis, part = compute_basis_from_score(score_fn, model.input_names)

    # Score positions for each note in the score
    score_onsets = part.beat_map([n.start.t for n in part.notes_tied])

    # make predictions
    predictions = model.predict(basis, score_onsets)

    return predictions, model, part


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Render a piano performance of a given score file "
        "and save it as a MIDI file"
    )

    parser.add_argument(
        "score_fn",
        help=(
            "Score file (MusicXML, MIDI or formats supported by MuseScore 3)"
        ),
    )
    parser.add_argument("midi_fn", help="Output MIDI file")
    parser.add_argument(
        "--model-config",
        "-c",
        help=(
            "JSON file specifying the configuration and parameters of the"
            " model"
        ),
    )
    parser.add_argument(
        "--default-values",
        "-d",
        help=(
            "JSON file specifying the default values for rendering the"
            " performance"
        ),
        default=None,
    )
    parser.add_argument(
        "--render-config",
        "-r",
        help=(
            "JSON file specifying the configuration for post-processing the"
            " generated performance"
        ),
        default=None,
    )
    parser.add_argument(
        "--save-match",
        "-m",
        help="Export Score-Performance alignment in Matchfile format",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()
    # Use toy model if no model is given
    if args.model_config is None:
        model_config = TOY_MODEL_CONFIG
    else:
        model_config = json.load(open(args.model_config))
    # Use default config files if not given
    if args.default_values is None:
        default_values = DEFAULT_VALUES
    else:
        default_values = json.load(open(args.default_values))

    if args.render_config is None:
        render_config = RENDER_CONFIG
    else:
        render_config = json.load(open(args.render_config))

    # Predict performance
    preds, model, part = predict(
        model_config=model_config,
        score_fn=args.score_fn,
        default_values=default_values,
    )
    # Post process predictions
    post_process_predictions(preds, render_config)

    # decode predictions
    perf_codec = get_performance_codec(model.output_names)
    predicted_ppart = perf_codec.decode(
        part=part,
        parameters=preds,
        return_alignment=args.save_match,
    )

    if args.save_match:
        predicted_ppart, alignment = predicted_ppart

    # Sanitize part
    sanitize_performed_part(predicted_ppart)

    # Save MIDI file
    save_performance_midi(predicted_ppart, args.midi_fn)

    if args.save_match:
        save_match(
            alignment=alignment,
            performance_data=predicted_ppart,
            score_data=part,
            out=args.midi_fn.replace(".mid", ".match"),
            piece=os.path.basename(args.score_fn),
            performer="Basis Mixer",
        )
