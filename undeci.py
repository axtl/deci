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
import re
import os
import shutil
import sys
import tempfile
from zfec import filefec

import common
from common import ERR

DESCRIPTION='Rebuild directory from striped data'


def _verify_args(ns):
    logging.debug('verifying CLI arguments')
    if not ns.output:
        sys.stderr.write('No output directory specified\n')
        sys.exit(ERR['NO_OUTPUT'])
    if not ns.inputs:
        sys.stderr.write('No input directories specified\n')
        sys.exit(ERR['NO_INPUT'])
    if not ns.force and os.path.exists(ns.output):
        sys.stderr.write('Destination exists\n')
        sys.exit(ERR['NO_OVERWRITE'])
    logging.info('Will recover to %s with chunks from %s' % (ns.output,
        ns.inputs))
    logging.debug('inputs=%s' % ns.inputs)
    logging.debug('output=%s' % ns.output)
    logging.debug('force=%s' % ns.force)


def _fec_decode(ns):
    logging.debug('UNFEC pass started')
    tmpd = tempfile.mkdtemp(dir=os.getcwd())
    logging.debug('created tempdir at %s' % tmpd)

    # walk first input dir, decode as we go along
    for root, dirs, files in os.walk(ns.inputs[0]):
        unrooted = os.path.relpath(root, ns.inputs[0])
        logging.debug('unrooted path: %s' % unrooted)
        for dname in dirs:
            osubdir = os.path.join(tmpd, dname)
            os.mkdir(osubdir)
            logging.debug('created: %s' % osubdir)
        for f in files:
            # get real name
            rname = re.split('\.[0-9]*_[0-9]*\.fec$', f, re.IGNORECASE)[0]
            logging.debug('processing chunks for file: %s' % rname)
            # get all the file chunks into a list
            fecs = []
            for indir in ns.inputs:
                gpath = common.fec_glob(os.path.join(indir, unrooted, rname))
                fecs.extend(glob.glob(gpath))
            logging.debug('FEC chunks found for %s: %s' % (rname, fecs))
            fec_fds = [open(fec, 'rb') for fec in fecs]
            try:
                outpath = os.path.join(tmpd, unrooted, rname)
                outfd = open(outpath, 'wb')
                filefec.decode_from_files(outfd, fec_fds, False)
                logging.debug('decoded successfully to %s' % outpath)
            except filefec.InsufficientShareFilesError as e:
                logging.debug('failed to write %s' % outpath)
                sys.stderr.write(repr(e))
                common.cleanup(tmpd)
                sys.exit(ERR['INSUF_SHARES'])

    # all done, rename to output dir
    if os.path.exists(ns.output) and ns.force:
        shutil.rmtree(ns.output)
        logging.debug('removed existing output dir at %s' % ns.output)
    shutil.move(tmpd, ns.output)
    logging.debug('renamed temp dir %s to output dir %s' % (tmpd, ns.output))
    logging.info('UNFEC pass completed')


def main(argv):
    # setup and parse arguments
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-o', '--output',
        action='store',
        metavar='DIR',
        help='the output directory where files will be rebuilt')
    parser.add_argument('inputs',
        metavar='IN_DIR',
        type=str,
        nargs='+',
        help='list of directories from where input chunks are taken')
    parser.add_argument('-f', '--force',
        action='store_true',
        help='overwrite the output directory, even if it exists')
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
    _fec_decode(ns)

if __name__ == '__main__':
    main(sys.argv[1:])
