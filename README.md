# Subcutanean Collapser

> **Note**: This is a modified version of Aaron A. Reed's original Subcutanean Collapser system. The original context and release notes from the author are quoted below.

## About Subcutanean

*From the original author*:

> Five years ago, on the palindromic date of 02/02/2020, I released [*Subcutanean*](https://subcutanean.textories.com/), a procedural horror novel where no two copies were the same. (In what now seems a distant past, the generation for the project was entirely hand-crafted, with no LLMs or AIs involved.) One of the exclusive perks for the crowdfunding project was a glass USB key which contained 10,000 unique permutations of the novel and a handful of early drafts, behind-the-scenes material, the complete origin text from which all copies were generated, and the generator source code. I promised at the time that this material would be publicly released five years after publication. It's been five years, so: here it is!

> (If you're curious about the motivations and design of Subcutanean, there's [a series of design blogs](https://medium.com/@aareed/subcutanean-design-posts-e25d9c158cce) I wrote near the time of release. A [reading and design talk](https://stars.library.ucf.edu/elo2020/live/plenaries/4/#.XxG89sCQ6Yk.twitter) is also available.)

## What's In This Repository

This repository contains:

1. The **Collapser** - The Python-based text generation system that creates unique versions of texts written in the `.quant` format
2. **Sample Files** - Basic examples of `.quant` format in the `source` directory
3. **Documentation** - Syntax documentation for writing `.quant` files
4. **Tests** - Test cases for various components of the system

## Getting Started

### Prerequisites

- Python (originally written for Python 2.7)
- Supporting libraries as needed by individual components

### Usage Example

Here's a basic workflow for using the Collapser system:

1. **Create your `.quant` file** in the `source` directory or use one of the samples
   - See `source/quantfile-syntax.md` for complete syntax documentation
   - Study `source/basic_example.quant` and `source/advanced_example.quant` for examples

2. **Generate a version** using the collapser tool:

```bash
# Basic usage
python collapser/collapser.py --input=source/your_file.quant --output=txt

# With a specific random seed
python collapser/collapser.py --input=source/your_file.quant --gen=42 --output=txt

# Using author-preferred choices
python collapser/collapser.py --input=source/your_file.quant --strategy=author --output=txt

# See all available options
python collapser/collapser.py --help
```

3. **Find your output** in the directory indicated in the terminal output (typically `./output`)

### Available Output Formats

The collapser supports multiple output formats:
- `txt` - Plain text
- `html` - Web-ready HTML
- `epub` - E-book format
- `latex` - For PDF production via LaTeX
- `mobi` - Kindle format
- And others (see `--help` for the complete list)

## Writing `.quant` Files

The `.quant` format allows you to create texts with controlled variations. Key features include:

- **Simple Alternatives**: `[option1|option2|option3]`
- **Variables**: `[DEFINE @varName]` and `[@varName>text if true|text if false]`
- **Macros**: `[MACRO name][content]` and `{name}` or `$name`
- **Formatting Controls**: `{chapter/1}`, `{section_break}`, etc.

For complete documentation, see `source/quantfile-syntax.md`.

## Original Author's Notes

*From the original author about the Subcutanean novel generation*:

> Part of the release is 10,000 new permutations of the novel. Why not release the original 10,000? Well, they were first generated in advance of the book's actual release, since I had to get them on the USB keys being sent to backers; so they're missing several rounds of updates to the generator code and improvements to the writing that happened in the immediate aftermath of release (and to a lesser extent, in the years since).

> Each major change to Subcutanean has been marked by incrementing the "generation" of random seeds used to create books, corresponding to the first digit of the seed number fed into the generator. These new copies are Generation 5, starting with seed #50000 and running up to seed #59999 inclusive. These are not available as part of this Github repo, but can be found at [a separate download](https://subcutanean.textories.com/SubcutaneanArchive.zip). 

> (Which seed should you read? I've picked out three seeds somewhat at random that include a wide range of some of the major possible divergences: [#52447](https://subcutanean.textories.com/52447.html), [#56019](https://subcutanean.textories.com/56019.html), and [#58238](https://subcutanean.textories.com/58238.html). These should in no way be considered canonical versions: every *Subcutanean* is equally canonical.)

> You can, as before, continue to [buy your own unique and freshly generated copies of the novel](https://subcutanean.textories.com/) directly from me, in digital or paperback format.

## License

*From the original author*:

> The source code, source text and all prior, current, and future renderings of Subcutanean generated from it have now been released under a CC-BY-4.0 license, meaning you are free to share, archive, copy, and redistribute the material, even commercially, as long as credit is given to the original author (me, Aaron A. Reed).

---

*Original README by Aaron A. Reed, February 2025.  
Modified and extended April 2025.*
