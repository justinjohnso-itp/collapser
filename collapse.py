#!/usr/bin/env python

import sys
import os
import subprocess
import argparse 
import random # Import random module

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run collapser.py with specified input and output format.")
    parser.add_argument("source_file", nargs='?', default="advanced_example.quant", 
                        help="The source .quant file to process (defaults to advanced_example.quant)")
    parser.add_argument("-o", "--output", default="txt", 
                        help="The output format (e.g., txt, html, pdf, etc. - defaults to txt)")
    parser.add_argument("-s", "--seed", default="random", 
                        help="Seed for generation ('random' or a specific integer - defaults to random)")
    
    # Parse arguments
    args = parser.parse_args()
    
    source_file_arg = args.source_file
    output_format = args.output
    seed_arg = args.seed

    # Determine the seed to use
    if seed_arg.lower() == "random":
        # Generate a random seed (e.g., 7 digits for consistency with example)
        actual_seed = random.randint(1000000, 9999999) 
    else:
        try:
            actual_seed = int(seed_arg)
        except ValueError:
            print("Error: Seed must be 'random' or an integer.")
            return 1
            
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

    # Construct output filename base including the seed
    base_name = os.path.splitext(os.path.basename(source_file_arg))[0]
    output_file_base_name = "{}_{}".format(base_name, actual_seed) # Append seed

    # Ensure the output directory exists, as collapser.py might assume it
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Build the command using the parsed arguments AND the base filename with seed
    cmd = [
        "python", 
        "collapser/collapser.py",
        "--input={}".format(source_file_path),
        "--output={}".format(output_format), 
        "--file={}".format(output_file_base_name), # Pass base name with seed
        "--seed={}".format(actual_seed), # Pass the specific seed number
        "--skipEndMatter"
    ]
    
    # Run the command
    print("Running: {}".format(" ".join(cmd)))
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
