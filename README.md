# Prompt Template Parser

**Prompt Template Parser** is a Python script that converts specially formatted Markdown files into interactive HTML pages. These HTML pages allow users to dynamically generate structured prompts using text inputs, checkboxes, and file uploads.

## Features

- Converts Markdown-like syntax into structured HTML.
- Supports custom elements like:
  - Inline integer inputs (`<<integer_value>>`)
  - Text inputs (`[[label: default text]]`)
  - Checkboxes (`[x] Checked` / `[ ] Unchecked`)
  - File upload inputs (`(())`)
  - Verbatim code blocks (`{{{ code }}}`)
  - Inline comments (`(* comment *)`)
- Generates copyable text output from user inputs.

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

To specify an output filename:

```bash
python3 prompt_template_parser.py input.md -o output.html
```

## Acknowledgment

These scripts were partially generated with the assistance of ChatGPT. 

## License
This project is licensed under the MIT License.