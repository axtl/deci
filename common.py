#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

ERR = {
    'NO_INPUT': 2,
    'NO_OUTPUT': 3,
    'NO_SHARES': 4,
    'INSUF_OUTPUTS': 5,
    'NO_OVERWRITE': 6,
    'CHUNK_COUNT_MISMATCH': 7,
}


def setup_logging(ns):
    if ns.debug:
        lvl = logging.DEBUG
    elif ns.verbose:
        lvl = logging.INFO
    else:
        lvl = logging.WARNING
    logging.basicConfig(format='%(levelname)-8s %(message)s', level=lvl)
