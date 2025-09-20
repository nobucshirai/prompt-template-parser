#!/usr/bin/env python3
"""
Prompt Template Parser

This script converts an extended Markdown file—designed for prompt templates—
into a structured HTML file. It enables users to define interactive prompt elements
that can be compiled into a cohesive text prompt.

In addition to standard Markdown syntax, the following custom elements are supported:

- [[[background text:prefilled text]]] → Converts to a textbox input.
- [[background text:prefilled text]] → Converts to an inline text box input.
- (()) → Converts to a file load input element.
- [ ] and [x] → Converts to unchecked/checked checkboxes.
- (* Comment *) → Renders as visible text in HTML but is excluded from clipboard copying.
- #lang:jp# → Specifies the language for localization (default: "en").
- Verbatim blocks: {{{ ... }}} → Content is preserved exactly. Multi-line blocks are wrapped in <pre><code>, while single-line content is rendered inline with <code>.
- <<integer_value>> → Inserts a small inline number textbox with the given integer value as its default.
  (Note: The inline number input is no longer given the "prompt-item" class so that it isn’t processed separately.)

Usage:
    python3 prompt_template_parser.py input.md
    python3 prompt_template_parser.py input.md -o output.html

If no output file is specified, the script will generate an HTML file with the same
basename as the input file. If the output file already exists, the script will prompt
for confirmation before overwriting.
"""

import argparse
import os
import re
import sys
from typing import Tuple

def parse_custom_markdown(md: str) -> Tuple[str, str]:
    """
    Parse extended Markdown text and return the full HTML output and language code.

    The parser:
      - Extracts a language code if specified via #lang:xx# (default: en)
      - Converts custom textarea elements, file load elements, checkboxes,
        inline comments, inline integer inputs, inline text inputs, and verbatim blocks.
      - Wraps the generated body in an HTML document with inline CSS and JS.

    Args:
        md (str): The input extended Markdown content.

    Returns:
        Tuple[str, str]: A tuple where the first element is the complete HTML output
                         and the second is the language code.
    """
    # Detect language (default "en")
    lang_match = re.search(r'#lang:(\w+)#', md)
    lang: str = lang_match.group(1) if lang_match else 'en'
    md = re.sub(r'#lang:\w+#', '', md)

    # Normalize language key for lookup (treat 'jp' and 'ja' the same)
    lang_key = lang.lower()
    if lang_key == 'jp':
        lang_key = 'ja'

    # Button labels per language (HTML-escaped where necessary)
    BUTTON_LABELS = {
        'en': "Generate Prompt &amp; Copy to Clipboard",
        'ja': "プロンプトを生成してクリップボードにコピー",
        'fr': "Générer le prompt et copier dans le presse-papiers",
        'it': "Genera prompt e copia negli appunti",
        'es': "Generar prompt y copiar al portapapeles",
    }
    button_label = BUTTON_LABELS.get(lang_key, BUTTON_LABELS['en'])

    title: str = "Document"
    body_parts: list[str] = []

    # 1. Inline integer input: <<integer_value>>
    # NOTE: Removed "prompt-item" so it remains inline.
    md = re.sub(
        r'<<\s*(?P<value>\d+)\s*>>',
        lambda m: '<input type="number" class="inline-input" value="{}" min="1" />'.format(m.group('value')),
        md
    )

    # 2. Textbox: [[[placeholder:prefilled text]]]
    def replace_textarea(match: re.Match) -> str:
        placeholder = match.group('placeholder').strip().strip('"')
        prefilled = match.group('prefilled').strip()
        return f'<textarea id="textbox" placeholder="{placeholder}">{prefilled}</textarea>'
    md = re.sub(
        r'\[\[\[\s*(?P<placeholder>[^:]+?)\s*:\s*(?P<prefilled>.*?)\s*\]\]\]', 
        replace_textarea, 
        md
    )

    # 2.1. Inline text box: [[placeholder:prefilled text]]
    def replace_inline_textbox(match: re.Match) -> str:
        placeholder = match.group('placeholder').strip().strip('"')
        prefilled = match.group('prefilled').strip()
        # Removed the "prompt-item" class to prevent duplicate copying.
        return f'<input type="text" class="inline-text" placeholder="{placeholder}" value="{prefilled}" />'
    md = re.sub(
        r'\[\[\s*(?P<placeholder>[^:]+?)\s*:\s*(?P<prefilled>.*?)\s*\]\]',
        replace_inline_textbox,
        md
    )

    # 3. File load element: (())
    # Updated to include class "prompt-item" so that file inputs are included in the prompt assembly.
    md = re.sub(r'\(\(\s*\)\)', '<input type="file" id="fileLoad" class="prompt-item" />', md)

    # 4. Inline comment: (* Comment *)
    def replace_comment(match: re.Match) -> str:
        comment_text = match.group(1).strip()
        return f'<span class="comment" data-no-clipboard="true">{comment_text}</span>'
    md = re.sub(r'\(\*\s*(.*?)\s*\*\)', replace_comment, md)

    # 5. Verbatim blocks: {{{ ... }}}
    def replace_verbatim(match: re.Match) -> str:
        content = match.group(1)
        if "\n" in content:
            # Block-level verbatim: preserve whitespace and newlines.
            return f'\n<pre><code>{content}</code></pre>\n'
        else:
            # Inline verbatim.
            return f'<code>{content}</code>'
    md = re.sub(r'\{\{\{(.*?)\}\}\}', replace_verbatim, md, flags=re.DOTALL)

    # Re-split the text (which now may include inserted HTML) into lines.
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        # If the current line is part of a block-level verbatim section,
        # detect and join all lines up to the closing </code></pre>
        if lines[i].lstrip().startswith("<pre><code>"):
            verbatim_lines = []
            while i < len(lines):
                verbatim_lines.append(lines[i])
                if lines[i].rstrip().endswith("</code></pre>"):
                    i += 1
                    break
                i += 1
            body_parts.append("\n".join(verbatim_lines))
            continue

        line = lines[i].strip()
        # Process header lines (e.g. "# Header")
        if line.startswith("#"):
            header_match = re.match(r'^(#{1,6})\s*(.+)$', line)
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                if title == "Document":
                    title = header_text
                body_parts.append(f'<h{header_level}>{header_text}</h{header_level}>')
            i += 1
        # Process checkbox lines that start with "[ ]" or "[x]"
        elif re.match(r'^\[(?:x|X| )\]', line):
            checkbox_block: list[str] = []
            while i < len(lines) and re.match(r'^\[(?:x|X| )\]', lines[i].strip()):
                cb_line = lines[i].strip()
                cb_match = re.match(r'^\[(?P<status>[xX ]?)\]\s*(?P<label>.+)$', cb_line)
                if cb_match:
                    status = cb_match.group('status').lower().strip()
                    label_text = cb_match.group('label').strip()
                    checkbox_id = re.sub(r'\s+', '', label_text)
                    checkbox_id = re.sub(r'\W+', '', checkbox_id)
                    checked_attr = ' checked' if status == 'x' else ''
                    checkbox_block.append(
                        f'<label class="prompt-item"><input type="checkbox" id="{checkbox_id}"{checked_attr} /> {label_text}</label>'
                    )
                i += 1
            if checkbox_block:
                body_parts.append('<div class="checkbox-container">')
                body_parts.extend(checkbox_block)
                body_parts.append('</div>')
        else:
            # For textarea elements inserted by our custom syntax, add the "prompt-item" class.
            if line.startswith("<textarea"):
                if 'class="' in line:
                    line = re.sub(r'class="([^"]+)"', r'class="\1 prompt-item"', line)
                else:
                    line = line.replace("<textarea", '<textarea class="prompt-item"', 1)
                body_parts.append(line)
            else:
                # For any non-empty line, wrap it in a paragraph tag.
                if line:
                    body_parts.append(f'<p class="prompt-item">{line}</p>')
            i += 1

    html_body = "<div id=\"promptContent\">\n" + "\n".join(body_parts) + "\n</div>"

    # Build a dynamic <style> block including only the rules for elements that appear in the HTML.
    style_rules = []

    # Always include basic body styling.
    style_rules.append("""body {
      max-width: 800px;
      margin: 0 auto;
      font-family: sans-serif;
    }""")

    if "<h1>" in html_body:
       style_rules.append("""h1 {
      margin-top: 1em;
      font-size: 2em;
    }""")

    if "<textarea" in html_body:
       style_rules.append("""textarea {
      width: 100%;
      height: 100px;
      margin-bottom: 1em;
    }""")

    if 'class="inline-text"' in html_body:
       style_rules.append("""input.inline-text {
      padding: 2px;
      font-size: 1em;
      text-align: center;
    }""")

    if "<button" in html_body:
       style_rules.append("""button {
      padding: 0.5em 1em;
      cursor: pointer;
    }""")

    style_rules.append(""".result-box {
      white-space: pre-wrap;
      border: 1px solid #ddd;
      padding: 1em;
      margin-top: 1em;
    }""")

    if 'class="checkbox-container"' in html_body:
       style_rules.append(""".checkbox-container {
      margin-bottom: 1em;
    }""")

    if "<label" in html_body:
       style_rules.append("""label {
      display: block;
      margin-bottom: 0.5em;
    }""")

    if 'class="comment"' in html_body:
       style_rules.append(""".comment {
      color: grey;
    }""")

    if 'class="inline-input"' in html_body:
       style_rules.append(""".inline-input {
      width: 3em;
      padding: 2px;
      font-size: 1em;
      text-align: center;
    }""")

    style_block = "<style>\n" + "\n".join(style_rules) + "\n</style>"

    # Determine which features are present so we only output the necessary JavaScript.
    has_file_input = '<input type="file"' in html_body
    has_inline_input = 'class="inline-text"' in html_body

    # Build the script block dynamically.
    # Note: We no longer include input[type='number'] in the querySelector so that inline number inputs
    # are processed as part of their parent element.
    script_parts = []
    script_parts.append("<script>\n(function(){\n")
    script_parts.append("  document.getElementById(\"generateButton\").addEventListener(\"click\", async () => {\n")
    script_parts.append("    const promptItems = [];\n")
    if has_file_input:
        script_parts.append("    const elements = document.querySelectorAll(\"#promptContent .prompt-item, pre code, input[type='file']\");\n")
    else:
        script_parts.append("    const elements = document.querySelectorAll(\"#promptContent .prompt-item, pre code\");\n")
    script_parts.append("    for (const el of elements) {\n")
    script_parts.append("      const tag = el.tagName.toLowerCase();\n")
    script_parts.append("      if (tag === \"textarea\") {\n")
    script_parts.append("        promptItems.push(el.value);\n")
    script_parts.append("      } else if (tag === \"p\") {\n")
    script_parts.append("        promptItems.push(getElementText(el));\n")
    script_parts.append("      } else if (tag === \"label\") {\n")
    script_parts.append("        const checkbox = el.querySelector(\"input[type='checkbox']\");\n")
    script_parts.append("        if (checkbox && checkbox.checked) {\n")
    script_parts.append("          promptItems.push(getElementText(el));\n")
    script_parts.append("        }\n")
    script_parts.append("      } else if (tag === \"code\") {\n")
    script_parts.append("        promptItems.push(el.textContent);\n")
    script_parts.append("      } else if (tag === \"input\" && el.type === \"text\") {\n")
    script_parts.append("        promptItems.push(el.value);\n")
    script_parts.append("      }\n")
    if has_file_input:
        script_parts.append("      else if (tag === \"input\" && el.type === \"file\") {\n")
        script_parts.append("        if (el.files && el.files.length > 0) {\n")
        script_parts.append("          try {\n")
        script_parts.append("            const fileContent = await readFileAsText(el.files[0]);\n")
        script_parts.append("            promptItems.push(fileContent);\n")
        script_parts.append("          } catch (err) {\n")
        script_parts.append("            console.error(\"Error reading file:\", err);\n")
        script_parts.append("          }\n")
        script_parts.append("        }\n")
        script_parts.append("      }\n")
    script_parts.append("    }\n")
    script_parts.append("    const prompt = promptItems.join(\"\\n\");\n")
    script_parts.append("    navigator.clipboard.writeText(prompt)\n")
    script_parts.append("      .then(() => { alert(\"Copied to clipboard!\"); })\n")
    script_parts.append("      .catch((err) => { alert(\"Failed to copy: \" + err); });\n")
    script_parts.append("    const resultPromptDiv = document.getElementById(\"resultPrompt\");\n")
    script_parts.append("    resultPromptDiv.hidden = false;\n")
    script_parts.append("    resultPromptDiv.textContent = prompt;\n")
    script_parts.append("  });\n")
    if has_file_input:
        script_parts.append("\n  function readFileAsText(file) {\n")
        script_parts.append("    return new Promise((resolve, reject) => {\n")
        script_parts.append("      const reader = new FileReader();\n")
        script_parts.append("      reader.onload = () => resolve(reader.result);\n")
        script_parts.append("      reader.onerror = reject;\n")
        script_parts.append("      reader.readAsText(file);\n")
        script_parts.append("    });\n")
        script_parts.append("  }\n")
    script_parts.append("\n  function getElementText(el) {\n")
    script_parts.append("    let text = \"\";\n")
    script_parts.append("    el.childNodes.forEach(node => {\n")
    script_parts.append("      if (node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === \"input\") {\n")
    script_parts.append("        if (node.type === \"text\" || node.type === \"number\") {\n")
    script_parts.append("          text += node.value;\n")
    script_parts.append("        }\n")
    script_parts.append("      } else {\n")
    script_parts.append("        text += node.textContent;\n")
    script_parts.append("      }\n")
    script_parts.append("    });\n")
    script_parts.append("    return text.replace(/\\s+/g, \" \").trim();\n")
    script_parts.append("  }\n")
    script_parts.append("})();\n</script>")
    script_block = "".join(script_parts)

    html_output = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  {style_block}
</head>
<body>
{html_body}

<button id="generateButton">{button_label}</button>

<div class="result-box" id="resultPrompt" hidden></div>

{script_block}

</body>
</html>
'''
    return html_output, lang

def main() -> None:
    """
    Main function: parses command-line arguments, reads input Markdown files,
    converts them to HTML, and writes the output files (after confirming overwrites).
    """
    parser = argparse.ArgumentParser(
        description="Extended Markdown Parser: Convert extended Markdown to HTML."
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Input Markdown file(s) to parse."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output HTML filename. Default: same basename as input with .html extension."
    )
    args = parser.parse_args()

    for input_file in args.input_files:
        if not os.path.isfile(input_file):
            print(f"Error: File '{input_file}' not found.")
            continue

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
        except Exception as e:
            print(f"Error reading '{input_file}': {e}")
            continue

        html_output, _ = parse_custom_markdown(md_content)

        if args.output:
            output_file = args.output
        else:
            base, _ = os.path.splitext(input_file)
            output_file = base + ".html"

        if os.path.exists(output_file):
            overwrite = input(f"File '{output_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite not in ('y', 'yes'):
                print(f"Skipping file '{output_file}'.")
                continue

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            print(f"Generated HTML file: {output_file}")
        except Exception as e:
            print(f"Error writing to '{output_file}': {e}")

if __name__ == "__main__":
    main()
