import argparse
import sys
import datetime
import os
import pathlib

def testArgs():
    parser = argparse.ArgumentParser()
    script_path = pathlib.Path(sys.argv[0]).resolve()
    scriptpath = str(script_path).rstrip(".py")
    scriptname = scriptpath.split("/")[-1]
    suffix = datetime.datetime.now().isoformat()
    logFileName = scriptname + "_" + suffix + ".log"
    logFileName = os.path.expanduser("~/git_code/relex/logs/" + logFileName)
    paramFileName = scriptpath + ".prm"
    defaultStation = os.path.expanduser("~/git_code/relex/testbed/sampletb.yaml")
    parser.add_argument(
        "-logfile", help="File to store execution log", default=logFileName
    )
    parser.add_argument(
        "-param", help="File to store script parameters", default=paramFileName
    )
    parser.add_argument(
        "-loglevel", help="Debug level to be used while executing", default="debug"
    )
    parser.add_argument(
        "-station", help="File to get test device info", default=defaultStation
    )
    return parser.parse_args(sys.argv[1:])
