# deci (Directory Erasure Coding Interface)

**deci** is a simple tool that will let you stripe all the data in one directory across a number of output directories and given a specified number of shares required for re-encoding.

**undeci** is the reverse: it takes a list of directories and reconstructs the data to the specified output directory.

## Usage Information

* **deci**

        $ ./deci.py -h
        usage: deci.py [-h] [-i IN_DIR] [-k SHARES] [-f] [-v] [-d]
                       OUT_DIR [OUT_DIR ...]

        Stripe data from one directory across a set of other directories

        positional arguments:
          OUT_DIR               a directory to strip TO

        optional arguments:
          -h, --help            show this help message and exit
          -i IN_DIR, --input IN_DIR
                                directory to stripe across output directories
          -k SHARES, --shares SHARES
                                the number of shares to use for striping (must be
                                smaller than the number of output directories)
          -f, --force           overwrite existing files in output directories
          -v, --verbose         detailed output of operations
          -d, --debug           debug information

* **undeci**

        $ /undeci.py -h
        usage: undeci.py [-h] [-o DIR] [-f] [-v] [-d] IN_DIR [IN_DIR ...]

        Rebuild directory from striped data

        positional arguments:
          IN_DIR                list of directories from where input chunks are taken

        optional arguments:
          -h, --help            show this help message and exit
          -o DIR, --output DIR  the output directory where files will be rebuilt
          -f, --force           overwrite the output directory, even if it exists
          -v, --verbose         detailed output of operations
          -d, --debug           debug information

_**NOTE:** Due to what appears to be a bug in Python's argparse, some of the required arguments are listed as optional._

## Dependencies

The heavy lifting is performed by the [zfec][] library.  Refer to `requirements.txt` for a list of all dependencies (which can be installed via pip)

[zfec]: http://tahoe-lafs.org/trac/zfec

## TODO

* simple test suite
* add daemon mode to **deci**, so that changes on the input folder are automatically striped on the outputs