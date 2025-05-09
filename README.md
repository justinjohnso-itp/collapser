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

**Note:** This code was originally written for Python 2.7 and has specific dependencies. Using the provided Docker environment is the recommended way to ensure compatibility and run the system.

### Prerequisites (Recommended: Docker)

The easiest way to run the Collapser and ensure all dependencies (including Python 2.7) are correctly configured is by using Docker and the provided `docker-compose.yml` file.

1.  **Install Docker:** If you don't have it, install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/).
2.  **Create Necessary Directories (on your computer):** The script expects certain directories to exist in the project root *before* running. Create them if they don't exist:
    ```bash
    mkdir -p output confirms seeds
    ```
    - `output/`: Where generated text files will be placed.
    - `confirms/`: Stores user confirmations for specific text variations (optional feature).
    - `seeds/`: Used for sequential seed generation if not using `--seed=random` or `--seed=N` (optional feature, see below).
3.  **Build & Run Container:** Open a terminal in the project's root directory and run:
    ```bash
    docker-compose up -d
    ```
    This command builds the Docker image (if it doesn't exist), installs Python dependencies inside the container, downloads necessary NLTK data, and starts the container running in the background.
4.  **Access the Container Shell:** To run commands inside the container's environment:
    ```bash
    docker-compose exec collapser bash
    ```
    This will give you a shell prompt (`root@<container_id>:/app#`) inside the container, ready to run the `collapser.py` script.

### Prerequisites (Alternative: Manual Python 2.7)

If you prefer not to use Docker, you will need a working Python 2.7 environment and install dependencies manually. See previous revisions of this README for details, but this path may be complex due to Python 2.7's age. You will still need to create the `output/`, `confirms/`, and `seeds/` directories manually.

### Seed Management (Optional)

If you want to generate seeds sequentially within a specific "generation" (instead of randomly), you need to set up the `seeds/` directory:

1.  Inside the `seeds` directory (created above), create a file named `gen-X.dat`, where `X` is the generation number (default is 9 for testing).
2.  Initialize this file with the *last used seed number* for that generation (e.g., `0` if you want the next seed to be `X0001`).
    ```bash
    # Example: Initialize generation 9, starting count at 0
    echo "0" > seeds/gen-9.dat 
    ```
**Note:** If you don't provide a `--seed` argument and this file structure isn't present, the script now defaults to using a random seed.

## Usage Example (Using Docker)

1.  **Start the Docker container and get a shell** (if you haven't already):
    ```bash
    # Start container in background
    docker-compose up -d 
    # Get shell inside the container
    docker-compose exec collapser bash
    ```
2.  **Run the collapser (inside the container shell):**
    ```bash
    # Test command using the basic example, random seed, and skipping end matter:
    python collapser/collapser.py --input=source/basic_example.quant --output=txt --seed=random --skipEndMatter
    ```
    Check the `output/` directory on your host machine (your computer) for the resulting `.txt` file. The filename will be the random seed number used (e.g., `1234567.txt`).

3.  **Explore other options:**
    ```bash
    # See all available command-line options
    python collapser/collapser.py --help
    ```
    (See [collapser/collapser-commands.md](collapser/collapser-commands.md) for a reference list of all commands.)

## Available Output Formats

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

For complete documentation on the syntax and how to structure your files, see [source/quantfile-syntax.md](source/quantfile-syntax.md).

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
