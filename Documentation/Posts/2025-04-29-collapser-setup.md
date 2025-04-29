# Getting the Subcutanean Collapser Running (and Adapting Twine)

For my Computational Approaches to Narrative class, I started working with Aaron Reed\'s Subcutanean Collapser tool. The goal was twofold: understand how this "quantum text" system worked and adapt a Twine piece I\'d previously written ("The Oldest House") into its `.quant` format.

The first step was trying to get the example `.quant` files to parse correctly using the provided `collapser.py` script (run via Docker and `makeBook`). This immediately threw a series of lexer errors. Debugging these became the initial phase of reverse-engineering the system.

I encountered several types of syntax issues repeatedly:
*   **Line Breaks:** The parser was sensitive to line breaks within conditional choices (`[...]`). Options separated by `|` needed to be contiguous. For instance, an error like `Found a @variable but in an unexpected spot` pointed to a line break before `@brave` in `[@timid>...|\n@brave>...]`. The fix was `[@timid>...|@brave>...]`.
*   **Nesting:** The biggest rule I learned was **no nesting**. You cannot put bracketed choices `[...]` or variable checks `[@var>...]` inside other brackets. An `Illegal nested control sequence` error for `[@hasKey>...revealing a [dusty|dark|dimly lit] hallway]` required "flattening" it into separate top-level options for dusty, dark, and dimly lit hallways.
*   **Invalid Syntax:** I initially tried using constructs like `{@male>his}` inside macros or `{#var=true}` to set state, based on assumptions from other systems. Looking at the `quantfile-syntax.md` documentation and the script\'s behavior confirmed these were invalid. Variable checks `[@var>...]` are only for conditional text output, and macros `{macro}` are simple text substitutions. There\'s no built-in way to set variables mid-flow like in Twine; state seems primarily set upfront via `[DEFINE @var]` or implicitly by reaching `[LABEL]`s. An error like `Comments not allowed within control sequences` for `{#var=true}` confirmed `#` is only for comments, which aren't allowed inside `[...]`.
*   **Standalone Variables:** Constructs like `[@var1][@var2>text]` also failed with `Can't have a standalone [@variable]`. The parser needs text after the `>` in *any* conditional block, leading me to use the OR syntax `[@var1|@var2>text]` for combined conditions.

Fixing these syntax errors involved a lot of trial-and-error, cross-referencing the minimal `quantfile-syntax.md`, and making inferences based on the parser\'s complaints.

While debugging, I started adapting my Twine story, "The Oldest House". This involved rethinking the structure significantly. Twine uses discrete passages and links, making state changes (`(set: $var to true)`) easy. Collapser uses a single, linear text file where variation comes from initial probabilities `[DEFINE @var]` and conditional text `[@var>...]`.

Translating "The Oldest House" meant:

1.  **Linearizing:** Copying Twine passage text into one `.quant` file.
2.  **Mapping State:** Defining key variables upfront using `[DEFINE ...]`. For example, the protagonist\'s gender and a key house characteristic:
    ```quant
    # --- Core State Variable Definitions ---
    [DEFINE 50>@male|50>@female] # Protagonist gender
    [DEFINE 50>@house_state_watchful] # Is the house watchful?
    ```
    And defining macros for substitutions:
    ```quant
    # --- Utility Macro Definitions ---
    [MACRO protagonistName][@male>Kwame|@female>Anaya]
    [MACRO pronounSubject][@male>he|@female>she]
    [MACRO pronounPossessive][@male>his|@female>her]
    [MACRO pronounSubjectCaps][@male>He|@female>She]
    [MACRO aunt_name][Mama Elodie|Auntie Isolde|Great-Aunt Seraphina]
    ```
3.  **Converting Choices/Conditionals:** Simple text variations became `[...]` blocks:
    ```quant
    # Setting the scene
    The [small plane bounced|ferry drifted|taxi squealed] to a halt. {protagonistName} took a deep breath and was greeted with the scent of [salt and hibiscus|frangipani and damp earth|woodsmoke and the sea]...
    ```
    This might generate: *"The ferry drifted to a halt. Kwame took a deep breath and was greeted with the scent of salt and hibiscus..."* or *"The taxi squealed to a halt. Anaya took a deep breath and was greeted with the scent of woodsmoke and the sea..."*.

    Twine\'s `<<if>>` statements were replaced with `[@variable>text|alternative text]`:
    ```quant
    # Conditional atmosphere based on house state
    {protagonistName} gathered {pronounPossessive} bags and started up the long, winding front path. [@house_state_watchful>It seemed to notice {pronounPossessive} approach, the shingles rustling, the walls creaking ponderously.|The house stood silent, waiting.]
    ```
    If `@house_state_watchful` was true (a 50% chance from the `DEFINE`), the output might be: *"Kwame gathered his bags and started up the long, winding front path. It seemed to notice his approach, the shingles rustling, the walls creaking ponderously."* Otherwise: *"Anaya gathered her bags and started up the long, winding front path. The house stood silent, waiting."*

4.  **Handling Jumps:** Using `[LABEL]` markers and `{JUMP Label}` to control flow, replacing Twine links:
    ```quant
    # Entering the house
    The main path led to the imposing front door. {protagonistName} pushed it open. {JUMP Foyer}

    # --- Foyer ---
    [LABEL Foyer]
    The door swung inward [silently|with a low groan], releasing a breath of stale air smelling of [dust and beeswax|mildew and flowers|salt and old wood].
    ```
    This ensures that after the "Entering the house" text, the generation continues from the section marked `[LABEL Foyer]`, potentially outputting: *"Anaya pushed it open. The door swung inward with a low groan, releasing a breath of stale air smelling of mildew and flowers."*

This adaptation process highlighted the different philosophies. Twine facilitates explicit player agency. Collapser generates plausible variations of a *pre-authored* text flow based on initial conditions, creating different "tellings." The lack of mid-stream variable setting was a key constraint.

Once the `.quant` files (`the-oldest-house.quant` and a simplified `tobago-house.quant`) were closer to being syntactically correct, I hit issues running `collapser.py` itself. It required Python 2 (`print """..."""` syntax error), and its argument handling for output files (`--output` vs `--file`) was particular, requiring only the base filename for `--file` (`Please do not include paths or file extensions...`).

I created a Python 2-compatible wrapper script, `collapse.py`, using `argparse` to handle input/output filenames, format selection, and seed management, constructing the final command correctly:

```python
#!/usr/bin/env python

import sys
import os
import subprocess
import argparse
import random # Import random module

def main():
    parser = argparse.ArgumentParser(description="Run collapser.py with specified input and output format.")
    parser.add_argument("source_file", nargs='?', default="advanced_example.quant",
                        help="The source .quant file to process (defaults to advanced_example.quant)")
    parser.add_argument("-o", "--output", default="txt",
                        help="The output format (e.g., txt, html, pdf, etc. - defaults to txt)")
    parser.add_argument("-s", "--seed", default="random",
                        help="Seed for generation ('random' or a specific integer - defaults to random)")

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
        source_file_path = source_file_arg
        source_file_arg = os.path.basename(source_file_arg)

    # Make sure source file exists
    if not os.path.exists(source_file_path):
        print("Error: File '{}' not found".format(source_file_path))
        return 1

    # Construct output filename base including the seed
    base_name = os.path.splitext(os.path.basename(source_file_arg))[0]
    output_file_base_name = "{}_{}".format(base_name, actual_seed) # Append seed

    # Ensure the output directory exists
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Build the command using the parsed arguments AND the base filename with seed
    cmd = [
        "python2", # Explicitly use python2
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
```

After this iterative process of syntax debugging, adapting the Twine structure, and reverse-engineering the script\'s behavior, I finally had a working setup capable of generating different text variations like `output/tobago-house_1234567.txt` or `output/tobago-house_9876543.html`.
