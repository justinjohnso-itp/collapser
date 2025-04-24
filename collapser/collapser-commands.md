# Collapser Command-Line Options

This document lists all available command-line options for `collapser.py`, based on the output of `python collapser/collapser.py --help`.

**Usage:** `python2.7 collapser.py [options]`

---

**Arguments:**

*   `--help`
    *   Show the help message.
*   `--input=x,y,z`
    *   Alternate file(s) or manifest file(s) to load.
    *   *(default: `full-book-manifest.txt`)*
*   `--only=x,y`
    *   A subset of loaded files to render.
*   `--output=x`
    *   Format to output. *(default: `none`)*
    *   Options: `"pdf"` (for POD), `"pdfdigital"` (for online use), `"txt"`, `"html"`, `"web"`, `"md"`, `"epub"`, `"kpf"`, `"tweet"`, `"ebookorder"`
*   `--file=x`
    *   Write output to this filename. *(default: based on seed/strategy)*
*   `--seed=`
    *   What seed to use in book generation. *(default: `next` sequential seed, or `random` if sequential fails)*
    *   `N`: Use the given integer `N`.
    *   `random`: Use a purely random seed.
*   `--gen=x`
    *   What generation of seeds to use. *(default: `9`)*
    *   Options: `0` (ARC), `1` (backers), `2` (USB), `4` (current), `9` (test)
*   `--strategy=x`
    *   Selection strategy. *(default: `"random"`)*
    *   Options: `"random"`, `"author"` (Author's preferred), `"pair"` (Two versions optimizing for difference), `"longest"`, `"shortest"`
*   `--times=N`
    *   How many times to run this command.
*   `--set=x,y,z`
    *   A list of variables to set true for this run. Preface with `^` to negate.
*   `--discourseVarChance=x`
    *   Likelihood (0-100) to defer to a discourse variable. *(default: `80`)*
*   `--skipConfirm`
    *   Skip variant confirmation prompts.
*   `--skipPadding`
    *   Skip padding output to 232 pages (relevant for PDF).
*   `--skipFront`
    *   Skip frontmatter generation.
*   `--endMatter=x,y`
    *   Add specific end matter files (comma-separated). *(default: `auto`)*
*   `--skipEndMatter`
    *   Don't add any end matter.
