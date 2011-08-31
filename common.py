#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import shutil

ERR = {
    'NO_INPUT': 2,
    'NO_OUTPUT': 3,
    'NO_SHARES': 4,
    'INSUF_OUTPUTS': 5,
    'NO_OVERWRITE': 6,
    'CHUNK_COUNT_MISMATCH': 7,
    'INSUF_SHARES': 8,
}


def setup_logging(ns):
    """Setup logging infrastructure based on set flags"""
    if ns.debug:
        lvl = logging.DEBUG
    elif ns.verbose:
        lvl = logging.INFO
    else:
        lvl = logging.WARNING
    logging.basicConfig(format='%(levelname)-8s %(message)s', level=lvl)


def cleanup(tmpd):
    """Log and remove the work directory"""
    logging.info('Cleaning up...')
    logging.debug('removing temp dir at %s' % tmpd)
    shutil.rmtree(tmpd)


def fec_glob(f):
    """Returns a glob path that will match fec files"""
    return f + '.[0-9]*_[0-9]*.fec'