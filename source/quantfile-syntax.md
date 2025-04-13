# .quant File Format Documentation

`.quant` files are the source files for the Subcutanean Collapser system, a procedural text generation engine that creates combinatorial narrative variations from a single master text. This document explains the syntax and workflow for writing your own `.quant` files.

## Basic Syntax

A `.quant` file consists of plain text interspersed with **control sequences** that define variation points in the narrative. These control sequences are enclosed in square brackets `[...]` and provide the engine with options to choose from during generation.

### Simple Alternatives

The most basic form of variation is a simple choice between alternatives:

```
I [love|like|adore] programming.
```

This will generate one of:
- "I love programming."
- "I like programming."
- "I adore programming."

### Weighted Choices

You can assign weights to options to make some choices more likely:

```
The weather is [70>sunny|20>cloudy|10>rainy].
```

The numbers represent percentage chances, which must sum to 100 or less. If they sum to less than 100, there's a chance of selecting nothing.

### Author Preferences

Mark a choice as author-preferred with `^` at the start:

```
The house was [big|^massive|enormous].
```

When using `--strategy=author`, "massive" will always be chosen.

### Optional Text

Square brackets with a single option create optional text (50% chance by default):

```
The painting was [quite] beautiful.
```

You can specify probability for optional text:

```
The painting was [30>quite] beautiful.
```

Or make an option explicitly empty:

```
The painting was [beautiful|].
```

## Variables and Persistence

### Defining Variables

Variables allow consistent choices across the text:

```
[DEFINE @protagonist|@antagonist]

[@protagonist>Jack|Sarah] looked at [@antagonist>the wolf|the witch].
Later, [@protagonist>he|she] confronted [@antagonist>it|her] again.
```

If "Jack" and "the wolf" are chosen in the first sentence, they'll be used in the second sentence too.

### Weighted Variable Definitions

You can assign probabilities to variables:

```
[DEFINE 60>@male|40>@female]

[@male>He|@female>She] walked into the room.
```

### Author-Preferred Variables

Mark variables as author-preferred with `^`:

```
[DEFINE ^@stormToday|@noStorm]

[@stormToday>Dark clouds gathered overhead.|@noStorm>The sky was clear.]
```

### Conditional Text

Show text only when a variable is true:

```
[DEFINE @hasKey]
The door was locked. [@hasKey>Fortunately, you had the key.]
```

Include an alternative with `|`:

```
[@hasKey>You unlocked the door.|The door remained locked.]
```

## Advanced Features

### Macros

Define reusable text with macros:

```
[MACRO characterName][John Smith|Jane Doe]

{characterName} entered the room. Later, {characterName} left.
```

Sticky macros persist across generations:

```
[STICKY_MACRO toolName][Grapple Hook|Climbing Gear]
```

### Labels and Jumps

Create named sections and jump to them:

```
[LABEL startScene]This is the beginning.

{JUMP endScene}Text that will be skipped.

[LABEL endScene]This is the end.
```

### Comments

Add comments with `#`. These are ignored by the parser:

```
# This is a comment explaining the next section
This text will appear in the output.
```

### Control Sequence Labels

Assign internal IDs to control sequences for debugging:

```
[*openingChoice*option A|option B]
```

## Generation Strategies

The collapser supports different generation strategies:

- `random` - Default, selects randomly based on weights
- `author` - Uses author-preferred choices (marked with `^`)
- `longest` - Always selects the longest option
- `shortest` - Always selects the shortest option
- `pair` - Generates two versions optimized for difference

## Example Workflow

Here's a simple workflow to get started with `.quant` files:

1. Create a `.quant` file in the `quant_files` directory
2. Write your text with variation points using the syntax above
3. Run the collapser with your file:

```bash
cd /path/to/collapser
python collapser/collapser.py --input=quant_files/your_file.quant --gen=42 --output=txt
```

4. Check the generated output in the `output` directory

## Tips for Writing Good `.quant` Files

1. Start small with simple variations
2. Use variables for consistency across your text
3. Test frequently to ensure your syntax is correct
4. Break complex narratives into separate files
5. Use comments to document your intentions
6. Keep your variation points focused and meaningful

## Reference

For more detailed information, refer to:
- Aaron Reed's blog posts in the `blog-posts` directory
- The test files in `collapser/test_quantparse.py` and `collapser/test_quantlex.py`
