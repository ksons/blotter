"""Runs importer tests in Blender and generates report file.

This script tests the glTF importer by trying to load the glTF
sample files. It writes a report about the test results to the
file report.json in the same directory as this script.

This script is designed to be called from run_tests.py. You
probably don't want to try running it on its own.

"""

import os
import sys
import bpy

base_dir = os.path.dirname(os.path.abspath(__file__))


def run_tests():
    #filename = sys.argv[-1]
    # sys.stderr.write(filename)

    bpy.ops.plot.plot()


def main():
    run_tests()


main()
