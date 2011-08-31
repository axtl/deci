#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, alexandru totolici http://alexandrutotolici.com @xorbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import argparse
import glob
import logging
import os
import shutil
import sys
import tempfile
from zfec import filefec

import common
from common import ERR

DESCRIPTION='Stripe data from one directory across a set of other directories'


def _verify_args(ns):
    logging.debug('Verifying CLI arguments')
    elif not os.path.exists(ns.input):
        sys.stderr.write('Input directory does not exist\n')
        sys.exit(ERR['NO_INPUT'])
    if not ns.outputs:
        sys.stedrr.write('No output directories specified\n')
        sys.exit(ERR['NO_OUTPUT'])
    elif len(ns.outputs) < 2:
        sys.stderr.write('No reason to stripe to only 1 output (use cp)\n')
        sys.exit(ERR['INSUF_OUTPUTS'])
    elif len(ns.outputs) <= ns.shares:
        sys.stderr.write('Need more output directories than shares\n')
        sys.exit(ERR['INSUF_OUTPUTS'])
    logging.info('Will stripe %s to %s and require %d shares for \
reconstruction' % (ns.input, ns.outputs, ns.shares))
    logging.debug('input=%s' % ns.input)
    logging.debug('outputs=%s' % ns.outputs)
    logging.debug('shares=%d' % ns.shares)
    logging.debug('force=%s' % ns.force)


def _make_output_dirs(ns):
    for odir in ns.outputs:
        if not os.path.exists(odir):
            os.mkdir(odir)
            logging.debug('created %s' % odir)


def _fec_encode(ns):
    logging.info('FEC pass started')

    tmpd = tempfile.mkdtemp(dir=os.getcwd())
    logging.debug('created temp dir at %s' % tmpd)

    # total shares
    tshares = len(ns.outputs)

    for root, dirs, files in os.walk(ns.input):
        # output dir, name mapping
        od = root.replace(ns.input, os.path.basename(tmpd))
        # recreate tree structure in temp dir
        for dname in dirs:
            osubdir = os.path.join(tmpd, dname)
            os.mkdir(osubdir)
            logging.debug('created %s' % osubdir)
        for f in files:
            fpath = os.path.join(root, f)
            logging.debug('processing file: %s' % fpath)
            with open(os.path.join(root, f)) as fd:
                fsize = os.path.getsize(fpath)
                logging.debug('FEC %s (%d bytes)' % (fpath, fsize))
                filefec.encode_to_files(fd, fsize, od, f, ns.shares, tshares,
                    '.fec', ns.force, False)

    logging.info('FEC pass completed')
    logging.info('Distribution pass started')
    for root, dirs, files in os.walk(ns.input):
        unrooted = os.path.relpath(root, ns.input)
        logging.debug('unrooted path: %s' % unrooted)
        # map dir tree structure unto output directories
        for outdir in ns.outputs:
            for dname in dirs:
                try:
                    osubdir = os.path.join(outdir, dname)
                    os.mkdir(osubdir)
                    logging.debug('created %s' % osubdir)
                except OSError:
                    logging.debug('exists: %s' % osubdir)
        for f in files:
            # glob on FEC output files to build list of things to distribute
            gexpr = common.fec_glob(f)
            gpath = os.path.join(tmpd, unrooted, gexpr)
            logging.debug('glob path for %s: %s' % (f, gpath))
            fecs = [os.path.basename(fec) for fec in glob.glob(gpath)]
            logging.debug('FEC chunks for %s: %s' % (f, fecs))
            if len(fecs) != tshares:
                logging.debug('len(fecs)=%d;shares=%d' % (len(fecs), tshares))
                sys.stdout.write('Chunks and output dir counts mismatch\n')
                common.cleanup(tmpd)
                sys.exit(ERR['CHUNK_COUNT_MISMATCH'])
            # spread chunks over output dirs
            for idx, fec in enumerate(fecs):
                ofec = os.path.join(ns.outputs[idx], unrooted, fec)
                if not ns.force and os.path.exists(ofec):
                    logging.debug('chunk collision: %s' % ofec)
                    sys.stderr.write('Some chunks with the same name exist\n')
                    common.cleanup(tmpd)
                    sys.exit(ERR['NO_OVERWRITE'])
                ifec = os.path.join(tmpd, unrooted, fec)
                logging.debug('input FEC for %s: %s' % (f, ifec))
                shutil.copyfile(ifec, ofec)
                logging.debug('wrote %s' % ofec)

    logging.info('Distribution pass completed')
    common.cleanup(tmpd)


def main(argv):
    # setup and parse arguments
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--input',
        required=True,
        action='store',
        metavar='IN_DIR',
        help='directory to stripe across output directories')
    parser.add_argument('outputs',
        metavar='OUT_DIR',
        type=str,
        nargs='+',
        help='a directory to strip TO')
    parser.add_argument('-k', '--shares',
        required=True,
        action='store',
        type=int,
        help='the number of shares to use for striping (must be smaller than\
            the number of output directories)')
    parser.add_argument('-f', '--force',
        action='store_true',
        help='overwrite existing files in output directories')
    parser.add_argument('-v', '--verbose',
        action='store_true',
        help='detailed output of operations')
    parser.add_argument('-d', '--debug',
        action='store_true',
        help='debug information')

    # create namespace with args
    ns = parser.parse_args(args=argv)

    common.setup_logging(ns)
    _verify_args(ns)
    _make_output_dirs(ns)
    _fec_encode(ns)


if __name__ == '__main__':
    main(sys.argv[1:])
