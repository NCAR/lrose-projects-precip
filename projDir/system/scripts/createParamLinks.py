#!/usr/bin/env python

# ========================================================================== #
#
# Create links to the parameter files in the data tree template
#
# ========================================================================== #

from __future__ import print_function
import os
import sys
from optparse import OptionParser
import subprocess

def main():

    global options

    # parse the command line

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--debug',
                      dest='debug', default=False,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--templateDir',
                      dest='templateDir', default="/tmp/templateDir",
                      help='Path of template - i.e. the directory tree template')
    parser.add_option('--installDir',
                      dest='installDir', default="/tmp/installDir",
                      help='Where the tree will be installed')
    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    # debug print

    if (options.debug):
        print("Running script: ", os.path.basename(__file__), file=sys.stderr)
        print("  Options:", file=sys.stderr)
        print("    Debug: ", options.debug, file=sys.stderr)
        print("    Verbose: ", options.verbose, file=sys.stderr)
        print("    Template dir: ", options.templateDir, file=sys.stderr)
        print("    Install dir: ", options.installDir, file=sys.stderr)

    # make the install dir

    try:
        os.makedirs(options.installDir)
    except OSError as exc:
        if (options.verbose):
            print("WARNING: trying to create install dir", file=sys.stderr)
            print("  ", exc, file=sys.stderr)

    # Walk the template directory tree

    for dirPath, subDirList, fileList in os.walk(options.templateDir):
        for fileName in fileList:
            if (fileName[0] == '_'):
                handleParamFile(dirPath, fileName)

    sys.exit(0)

########################################################################
# Handle a parameter file entry

def handleParamFile(dirPath, paramFileName):

    if (options.debug):
        print("Handling param file, dir, paramFile: ", \
            dirPath, ", ", paramFileName, file=sys.stderr)

    # compute sub dir

    subDir = dirPath[len(options.templateDir):]

    # compute install sub dir

    installSubDir = options.installDir + subDir

    if (options.debug):
        print("subDir: ", subDir, file=sys.stderr)
        print("installSubDir: ", installSubDir, file=sys.stderr)

    # make the install sub dir and go there

    try:
        os.makedirs(installSubDir)
    except OSError as exc:
        pass

    if (options.debug):
        print("os.chdir: ", installSubDir, file=sys.stderr)
    os.chdir(installSubDir)

    # remove the link if it exists

    if (os.path.exists(paramFileName)):
        os.remove(paramFileName)

    # create the link

    paramFilePath = os.path.join(options.templateDir + subDir, paramFileName)
    cmd = "ln -s " + paramFilePath
    runCommand(cmd)

    return

########################################################################
# Run a command in a shell, wait for it to complete

def runCommand(cmd):

    if (options.verbose == True):
        print("running cmd:",cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal: ", -retcode, file=sys.stderr)
        else:
            if (options.verbose == True):
                print("Child returned code: ", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)

########################################################################
# Run - entry point

if __name__ == "__main__":
   main()
