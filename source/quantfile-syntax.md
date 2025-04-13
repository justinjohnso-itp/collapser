# .quant File Format Documentation

`.quant` files are the source files for the Subcutanean Collapser system, a procedural text generation engine that creates combinatorial narrative variations from a single master text. This document explains the syntax and workflow for writing your own `.quant` files.

## Guidelines for Writing .quant Files

- Syntax should be easy to type, and minimize control characters.
- The smallest amount of variation is a word: don't waste time making versions with alternate punctuation or minor variants like dialog tags.
- A good metric: only include a variant when it's interesting. Avoid minor imperceptible variations.
- No nesting is allowed (to prevent wasting time on sub-probabilities of sub-probabilities). Every alternative is either seen or not.
- Think extremely hard before using a probability less than 10.
- Control characters should never be ones that would appear in your actual text.

## Basic Formatting

- Use a blank line between paragraphs.
- Three dashes for em-dash, or the em-dash character directly: `Look---Peter---the thing is...`
- Write extended Unicode characters directly: `Dvořák`
- Create a line break by ending a line with `\\` (same as LaTeX).
- For smart quotes, paste them directly into the document: `" " ' '`

## Basic Syntax

A `.quant` file consists of plain text interspersed with **control sequences** that define variation points in the narrative. These control sequences are enclosed in square brackets `[...]` and provide the engine with options to choose from during generation.

### Control Characters

The following special characters are used by the Collapser system:
- `[ ]` Begin and end a control sequence
- `{ }` Macro/format block
- `|` Divide alternatives
- `>` Conditional text
- `@` Indicates a variable
- `^` Author-preferred
- `#` Comment
- `~` Always print this block
- `/` Split params in formatting block
- `*` Surrounds control sequence labels

### Comments

Start a line with a `#` for a comment that will be stripped/ignored:

```
# This is a comment.
```

### Simple Alternatives

The most basic form of variation is a simple choice between alternatives:

```
I [love|like|adore] programming.
```

This will generate one of:
- "I love programming."
- "I like programming."
- "I adore programming."

It's valid to have an empty option. The below will print "alpha" or nothing randomly:

```
[alpha|]     => this is the same as [alpha]
```

### Author Preferences

The "author's preferred version" is assumed to be the first one listed. When this is not possible, it can also be indicated with a `^` immediately proceeding the content:

```
[alpha|^beta|gamma]   (or, better):    [beta|alpha|gamma]
[|alpha|beta]         => author's preferred version is to print nothing
```

When using `--strategy=author`, the preferred option will always be chosen. The code also has a slight preference for the author-preferred version (approximately 25%) in random mode.

### Single Item Options

If there is just a single item in brackets, it will either randomly print or not:

```
[alpha]     Print "alpha" randomly (or never when using author-preferred strategy)
[^alpha]    Print "alpha" randomly (or always when using author-preferred strategy)
```

### Always Print

If you preface a single block of text with `~`, it will always be printed (useful for macros):

```
[~alpha]    Always prints "alpha"
```

### Weighted Choices

You can assign weights to options to make some choices more likely:

```
The weather is [70>sunny|20>cloudy|10>rainy].
```

The numbers represent percentage chances, which must sum to 100 or less. If they sum to less than 100, there's a chance of selecting nothing. It's invalid for values to sum to > 100. 

If one alternative uses a number, they all must. The author-preferred indicator should go on the token, not the number:

```
[80>alpha|10>beta|10>^gamma]
[50>alpha]  => (equivalent to "[alpha]")
```

## Variables and Persistence

### Defining Variables

You can define a boolean variable, which always starts with @, by using the reserved word DEFINE (caps matter). This will be randomly set to true or false, unless you give it a probability. Author-preferred goes before the @ (which is part of the variable name):

```
[DEFINE @wordy]     => randomly true/false, or never true if author-preferred
[DEFINE 80>@wordy]  => @wordy is true 80% of the time, or never if author-preferred
[DEFINE 10>^@wordy] => @wordy is true 10% of the time, or always if author-preferred
```

Variables can contain letters, numbers, -, or _ and can't start with a number. Prefer camelCase.

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

You can also define an enum variable by specifying multiple options numerically. These must always add up to 100:

```
[DEFINE 50>@wordy|50>^@taciturn]
```

### Author-Preferred Variables

Mark variables as author-preferred with `^`:

```
[DEFINE ^@stormToday|@noStorm]

[@stormToday>Dark clouds gathered overhead.|@noStorm>The sky was clear.]
```

### Conditional Text

Restrict text to showing only when a defined variable is true. Note that it's a mistake to indicate author-preferred here: that's set by the variable.

```
[@wordy>he said loquaciously] 
```

Include an alternative with `|`:

```
[@wordy>You unlocked the door.|The door remained locked.]
[@angry>|He was very calm.]  // Only show "He was very calm" when @angry is false
```

## Advanced Features

### Macros

Define macros by starting with MACRO in caps, a space, then the macro label. The required replacement immediately following will be used whenever the macro is expanded:

```
[MACRO it's not][75>it's not|25>it isn't]
```

If you use STICKY_MACRO, the choice will be made once and then consistently for the rest of this collapse:

```
[STICKY_MACRO Soda][Pepsi|Sprite|Coke]
```

Invoke a macro in text by wrapping it in curly braces, or (if its name has no spaces) prefacing it with $:

```
"But {it's not} relevant"
She ordered a $Soda.
```

### Faking Conditional Logic

Conditional logic is not directly supported, but you can use macros to work around this. For example:

1. `@wordy AND @lostKeys -> I can't find my keys!`
```
[@wordy>{ifLostKeys}]
[MACRO ifLostKeys][@lostKeys>I can't find my keys!]
```

2. `@wordy AND NOT @lostKeys -> I'm wordy and organized!`
```
[@wordy>{ifNotLostKeys}]
[MACRO ifNotLostKeys][@lostKeys>|I'm wordy and organized!]
```

3. `@wordy OR @lostKeys -> I'm wordy or confused!`
```
[@wordy>{txt}|{orLostKeys}]
[MACRO orLostKeys][@lostKeys>{txt}]
[MACRO txt][~I'm wordy or confused!]
```

### Labels and Jumps (Gotos)

You can jump to a later point in the text by invoking a macro beginning with the word "JUMP" followed by a label:

```
{JUMP myLabel}
```

You can then later have a label: the text will continue afterwards:

```
[LABEL myLabel]
```

### Formatting Codes

The system has predefined formatting codes to print things in certain ways. These can either take parameters or not and can appear within control sequences:

```
{section_break}
{chapter/2}
{part/ONE/DOWNSTAIRS/Surely tis nobler.../William Shakespeare}
{verse/text}
{verse_inline/text}   => no pp breaks
{pp}
{i/italics}
{vspace/9}
```

Since both macros and formatting codes use curly braces and nesting is not allowed, macros don't play well with formatting codes. To work around this, you can reference a macro with no spaces in its name by prefacing it with a $, either in a formatting code or anywhere:

```
[MACRO destination][movies|store|beach]
{i/going to the $destination}
```

Note that using this approach to nest formatting codes within each other might lead to layout or rendering issues.

### Control Sequence Labels

To enable the "alternate version" End Matter bonus feature, authors can manually label a control sequence (which allows code to later retrieve and re-render that sequence). Put an identifier surrounded by asterisks as the first thing after the opening bracket:

```
[*Label1*alpha|omega]
[*AlphaOrOmegaVersion*@alpha>version one|@beta>version two]
[*AnotherLabel*50>X|50>Y]
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
