#!/usr/bin/env python

import sys
import os
import subprocess

def main():
    # Get the source file from command-line argument
    if len(sys.argv) > 1:
        source_file = sys.argv[1]
    else:
        source_file = "advanced_example.quant"
    
    # Make sure we prepend "source/" if it's not already included
    if not source_file.startswith("source/"):
        source_file = os.path.join("source", source_file)
    
    # Make sure file exists
    if not os.path.exists(source_file):
        print("Error: File '{}' not found".format(source_file))
        return 1
    
    # Build the command
    cmd = [
        "python", 
        "collapser/collapser.py",
        "--input={}".format(source_file),
        "--output=txt",
        "--seed=random",
        "--skipEndMatter"
    ]
    
    # Run the command
    print("Running: {}".format(" ".join(cmd)))
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
