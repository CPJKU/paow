#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The top level of the package.
"""
import pkg_resources
EXAMPLE = pkg_resources.resource_filename("paow", 
                                          "assets/dummy.txt")


from .utils import Sequencer, MidiRouter
from .evolutionary import Optimizer

__all__ = [
    "Sequencer",
    "MidiRouter",
    "Optimizer",
]
