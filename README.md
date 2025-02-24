# Prompt Template Parser

[![Pytest](https://github.com/nobucshirai/prompt-template-parser/actions/workflows/pytest.yml/badge.svg)](https://github.com/nobucshirai/prompt-template-parser/actions/workflows/pytest.yml)

**Prompt Template Parser** is a Python-based tool that converts specially formatted extended Markdown files into interactive HTML pages. These pages let users dynamically generate structured prompts using a variety of custom input elements.

## Features

- **Extended Markdown Conversion:**  
  Transforms extended Markdown into a complete HTML document with interactive elements.
- **Inline Text Inputs:**  
  Use double square brackets syntax (`[[label: default text]]`) for single-line text inputs.
- **Multi-line Textbox Inputs:**  
  Use triple square brackets syntax (`[[[label: default text]]]`) to generate multi-line textarea inputs.
- **Inline Integer Inputs:**  
  Insert a small number input field using the syntax `<<integer_value>>`.  
- **File Upload Inputs:**  
  Use `(())` to insert file load elements. Selected files are read and their content is included in the final prompt.
- **Checkboxes:**  
  Convert markdown checkboxes `[ ]` (unchecked) and `[x]` (checked) into interactive checkbox elements.
- **Verbatim Blocks:**  
  Enclose content in triple curly braces (`{{{ ... }}}`) to preserve exact formatting. Multi-line blocks are wrapped in `<pre><code>`, while single-line content is rendered inline with `<code>`.
- **Inline Comments:**  
  Write `(* comment *)` to include comments that are visible in the HTML but are excluded from the generated prompt.
- **Language Specification:**  
  Set localization using the syntax `#lang:xx#` (default is `"en"`).
- **Dynamic CSS and JavaScript Generation:**  
  The generated HTML automatically includes only the CSS rules and JavaScript functions needed based on the interactive elements present.

## Installation

Clone the repository:

```bash
git clone https://github.com/nobucshirai/prompt-template-parser.git
cd prompt-template-parser
```

## Usage

### Command-Line Interface

Convert an extended Markdown file (`input.md`) to an interactive HTML file:

```bash
python3 prompt_template_parser.py input.md
```

To specify a custom output filename:

```bash
python3 prompt_template_parser.py input.md -o output.html
```

*If no output file is specified, the script generates an HTML file with the same basename as the input file. If the output file already exists, you will be prompted for confirmation before overwriting.*

### Web Interface

The repository also includes a client-side version of the parser. Open the file [`prompt_template_parser.html`](prompt_template_parser.html) in your browser. From there, you can select a Markdown file with the extended syntax and click the button to generate and download an interactive HTML prompt.

## Sample Inputs

Two sample Markdown files are provided to demonstrate the tool’s capabilities:

- **sample_input_1.md:**  
  Demonstrates a prompt generator for meeting minutes—using multi-line textboxes and file uploads to build a structured meeting minutes document. The corresponding HTML ([sample_input_1.html](sample_input_1.html)) shows how the generated interface appears.

- **sample_input_2.md:**  
  Provides an example for a CLI tool prompt generator that features inline text inputs, checkboxes, and verbatim code blocks. The generated interface is illustrated in [sample_input_2.html](sample_input_2.html).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgment

Parts of this project were developed with the assistance of ChatGPT.