# Prompt Template Parser

**Prompt Template Parser** is a Python script that converts specially formatted Markdown files into interactive HTML pages. These pages let users dynamically generate structured prompts using a variety of custom input elements.

## Features

- **Extended Markdown Conversion:** Transforms extended Markdown into structured HTML.
- **Multi-line Textbox Inputs:**  
  Use triple square brackets syntax (`[[[label: default text]]]`) to generate a multi-line textbox.
- **Inline Text Inputs:**  
  Use double square brackets syntax (`[[label: default text]]`) for single-line inline text inputs.
- **Inline Integer Inputs:**  
  Insert a small inline number textbox using the syntax `<<integer_value>>`. *(Note: These inputs are not included in the prompt assembly.)*
- **File Upload Inputs:**  
  Insert file load elements with `(())`.
- **Checkboxes:**  
  Use `[ ]` for unchecked and `[x]` for checked boxes.
- **Verbatim Blocks:**  
  Enclose content in triple curly braces (`{{{ ... }}}`) to preserve exact formatting. Multi-line content is wrapped in `<pre><code>`, while single-line content appears inline using `<code>`.
- **Inline Comments:**  
  Write `(* comment *)` to include visible comments in HTML that are excluded from the generated prompt.
- **Language Specification:**  
  Specify localization using the `#lang:xx#` syntax (default is `"en"`).

The generated HTML includes inline CSS (optimized to include only the rules for elements present) and JavaScript that dynamically assembles the final prompt based on user inputs.

## Installation

Clone the repository:

```bash
git clone https://github.com/nobucshirai/prompt-template-parser.git
cd prompt-template-parser
```

## Usage

To convert a Markdown file (`input.md`) to an HTML file:

```bash
python3 prompt_template_parser.py input.md
```

To specify a custom output filename:

```bash
python3 prompt_template_parser.py input.md -o output.html
```

*If no output file is specified, the script generates an HTML file with the same basename as the input file. In case the output file already exists, the script will prompt for confirmation before overwriting it.*

## Acknowledgment

These scripts were partially generated with the assistance of ChatGPT.

## License

This project is licensed under the MIT License.