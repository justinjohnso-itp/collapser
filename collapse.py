#!/usr/bin/env python

import sys
import os
import subprocess
import argparse 

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run collapser.py with specified input and output format.")
    parser.add_argument("source_file", nargs='?', default="advanced_example.quant", 
                        help="The source .quant file to process (defaults to advanced_example.quant)")
    parser.add_argument("-o", "--output", default="txt", 
                        help="The output format (e.g., txt, html, pdf, etc. - defaults to txt)")
    
    # Parse arguments
    args = parser.parse_args()
    
    source_file_arg = args.source_file
    output_format = args.output
    
    # Construct full source path
    if not source_file_arg.startswith("source/"):
        source_file_path = os.path.join("source", source_file_arg)
    else:
        # Handle case where user might provide "source/file.quant"
        source_file_path = source_file_arg
        # Extract just the filename part for constructing output name
        source_file_arg = os.path.basename(source_file_arg) 

    # Make sure source file exists
    if not os.path.exists(source_file_path):
        print("Error: File '{}' not found".format(source_file_path))
        return 1

    # Construct output filename base
    base_name = os.path.splitext(os.path.basename(source_file_arg))[0]
    # Ensure the output directory exists, as collapser.py might assume it
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # NOTE: Pass ONLY the base_name to --file. collapser.py handles the directory.
    output_file_base_name = base_name 

    # Build the command using the parsed arguments AND the base filename
    cmd = [
        "python", 
        "collapser/collapser.py",
        "--input={}".format(source_file_path),
        "--output={}".format(output_format), 
        "--file={}".format(output_file_base_name), # Pass ONLY base name
        "--seed=random",
        "--skipEndMatter"
    ]
    
    # Run the command
    print("Running: {}".format(" ".join(cmd)))
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
