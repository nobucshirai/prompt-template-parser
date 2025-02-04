#!/usr/bin/env python3
"""
Prompt Template Parser

This script converts an extended Markdown file—designed for prompt templates—
into a structured HTML file. It enables users to define interactive prompt elements
that can be compiled into a cohesive text prompt.

In addition to standard Markdown syntax, the following custom elements are supported:

- [[background text:prefilled text]] → Converts to a textbox input.
- (()) → Converts to a file load input element.
- [ ] and [x] → Converts to unchecked/checked checkboxes.
- (* Comment *) → Renders as visible text in HTML but is excluded from clipboard copying.
- #lang:jp# → Specifies the language for localization (default: "en").
- Verbatim blocks: {{{ ... }}} → Content is preserved exactly. Multi-line blocks are wrapped in <pre><code>, while single-line content is rendered inline with <code>.

The generated HTML includes inline CSS for styling and JavaScript that
assembles the final prompt by extracting text from textboxes, paragraphs, checkboxes,
and verbatim code blocks. The compiled prompt can then be copied to the clipboard.

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
        inline comments, and verbatim blocks.
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

    title: str = "Document"
    body_parts: list[str] = []

    # 1. Textbox: [[placeholder:prefilled text]]
    def replace_textarea(match: re.Match) -> str:
        placeholder = match.group('placeholder').strip().strip('"')
        prefilled = match.group('prefilled').strip()
        return f'<textarea id="textbox" placeholder="{placeholder}">{prefilled}</textarea>'
    md = re.sub(
        r'\[\[\s*(?P<placeholder>[^:]+?)\s*:\s*(?P<prefilled>.*?)\s*\]\]', 
        replace_textarea, 
        md
    )
    # 2. File load element: (())
    # Updated to include class "prompt-item" so that file inputs are included in the prompt assembly.
    md = re.sub(r'\(\(\s*\)\)', '<input type="file" id="fileLoad" class="prompt-item" />', md)
    # 3. Inline comment: (* Comment *)
    def replace_comment(match: re.Match) -> str:
        comment_text = match.group(1).strip()
        return f'<span class="comment" data-no-clipboard="true">{comment_text}</span>'
    md = re.sub(r'\(\*\s*(.*?)\s*\*\)', replace_comment, md)

    # 4. Verbatim blocks: {{{ ... }}}
    def replace_verbatim(match: re.Match) -> str:
        content = match.group(1)
        if "\n" in content:
            # Block-level verbatim: preserve all whitespace and newlines
            return f'\n<pre><code>{content}</code></pre>\n'
        else:
            # Inline verbatim
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

    html_output = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <style>
    body {{
      max-width: 800px;
      margin: 0 auto;
      font-family: sans-serif;
    }}
    h1 {{
      margin-top: 1em;
      font-size: 2em;
    }}
    textarea {{
      width: 100%;
      height: 100px;
      margin-bottom: 1em;
    }}
    button {{
      padding: 0.5em 1em;
      cursor: pointer;
    }}
    .result-box {{
      white-space: pre-wrap;
      border: 1px solid #ddd;
      padding: 1em;
      margin-top: 1em;
    }}
    .checkbox-container {{
      margin-bottom: 1em;
    }}
    label {{
      display: block;
      margin-bottom: 0.5em;
    }}
    .comment {{
      color: grey;
    }}
  </style>
</head>
<body>
{html_body}

<button id="generateButton">Generate Prompt &amp; Copy to Clipboard</button>

<div class="result-box" id="resultPrompt" hidden></div>

<script>
  // Helper: read a File object as text, returning a Promise.
  function readFileAsText(file) {{
    return new Promise((resolve, reject) => {{
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    }});
  }}

  document.getElementById("generateButton").addEventListener("click", async () => {{
    const promptItems = [];
    // Select all prompt items, verbatim code blocks, and file inputs.
    const elements = document.querySelectorAll("#promptContent .prompt-item, pre code, input[type='file']");
    
    // Process each element in document order.
    for (const el of elements) {{
      const tag = el.tagName.toLowerCase();
      if (tag === "textarea") {{
        promptItems.push(el.value);
      }} else if (tag === "p") {{
        promptItems.push(el.textContent);
      }} else if (tag === "label") {{
        const checkbox = el.querySelector("input[type='checkbox']");
        if (checkbox && checkbox.checked) {{
          promptItems.push(el.textContent.trim());
        }}
      }} else if (tag === "code") {{
        promptItems.push(el.textContent);
      }} else if (tag === "input" && el.type === "file") {{
        // If a file is selected, read its content asynchronously.
        if (el.files && el.files.length > 0) {{
          try {{
            const fileContent = await readFileAsText(el.files[0]);
            promptItems.push(fileContent);
          }} catch (err) {{
            console.error("Error reading file:", err);
          }}
        }}
      }}
    }}
    
    const prompt = promptItems.join("\\n");
    
    // Copy to clipboard.
    navigator.clipboard.writeText(prompt)
      .then(() => {{
        alert("Copied to clipboard!");
      }})
      .catch((err) => {{
        alert("Failed to copy: " + err);
      }});
    
    // Also display the generated prompt.
    const resultPromptDiv = document.getElementById("resultPrompt");
    resultPromptDiv.hidden = false;
    resultPromptDiv.textContent = prompt;
  }});
</script>

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
