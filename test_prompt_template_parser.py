#!/usr/bin/env pytest
import re
import pytest
from prompt_template_parser import parse_custom_markdown
from bs4 import BeautifulSoup

def test_default_language():
    md = "This is a simple test."
    html, lang = parse_custom_markdown(md)
    # Default language should be "en"
    assert lang == "en"
    # The HTML should reflect the language in the <html> tag.
    assert '<html lang="en">' in html

def test_language_specified():
    md = "#lang:jp#\nSome content here."
    html, lang = parse_custom_markdown(md)
    # Extracted language should be "jp"
    assert lang == "jp"
    # The <html> tag should have lang="jp" and the language marker should be removed.
    assert '<html lang="jp">' in html
    assert "#lang:" not in html

def test_inline_integer():
    md = "Value: << 42 >>"
    html, _ = parse_custom_markdown(md)
    expected = '<input type="number" class="inline-input" value="42" min="1" />'
    assert expected in html

def test_textbox_and_inline_textbox():
    # Test the textarea element (triple-bracket syntax)
    md_textarea = '[[[Input text:something]]]'
    html_textarea, _ = parse_custom_markdown(md_textarea)
    soup = BeautifulSoup(html_textarea, 'html.parser')
    textarea = soup.find('textarea', id='textbox')
    assert textarea is not None, "Textarea with id 'textbox' not found"
    assert textarea.get('placeholder') == "Input text"
    assert "prompt-item" in textarea.get('class', [])
    assert textarea.text.strip() == "something"

    # Test the inline text input (double-bracket syntax)
    md_inline = '[[Input text:something]]'
    html_inline, _ = parse_custom_markdown(md_inline)
    soup_inline = BeautifulSoup(html_inline, 'html.parser')
    input_text = soup_inline.find('input', {'type': 'text'})
    assert input_text is not None, "Inline text input not found"
    assert input_text.get('placeholder') == "Input text"
    assert input_text.get('value') == "something"

def test_file_load_element():
    md = "Load file: (())"
    html, _ = parse_custom_markdown(md)
    expected = '<input type="file" id="fileLoad" class="prompt-item" />'
    assert expected in html

def test_inline_comment():
    md = "Comment here: (* This is a comment *)"
    html, _ = parse_custom_markdown(md)
    expected = '<span class="comment" data-no-clipboard="true">This is a comment</span>'
    assert expected in html

def test_verbatim_inline():
    md = "Inline code: {{{print('hello')}}}"
    html, _ = parse_custom_markdown(md)
    expected = '<code>print(\'hello\')</code>'
    assert expected in html

def test_verbatim_block():
    md = "Block verbatim:\n{{{\nprint('hello')\nprint('world')\n}}}"
    html, _ = parse_custom_markdown(md)
    # Block verbatim should be wrapped in <pre><code> ... </code></pre>
    assert '<pre><code>' in html
    assert '</code></pre>' in html

def test_checkbox_elements():
    md = "[ ] Option 1\n[x] Option 2"
    html, _ = parse_custom_markdown(md)
    # The checkboxes should be wrapped in a container.
    assert '<div class="checkbox-container">' in html
    # The checkbox IDs are derived from the label text (whitespace and non-word characters removed).
    expected_unchecked = '<label class="prompt-item"><input type="checkbox" id="Option1" /> Option 1</label>'
    expected_checked = '<label class="prompt-item"><input type="checkbox" id="Option2" checked'
    assert expected_unchecked in html
    assert expected_checked in html

def test_heading_and_paragraph():
    md = "# My Document\nThis is a paragraph."
    html, _ = parse_custom_markdown(md)
    # Check that the header is processed correctly.
    assert '<h1>My Document</h1>' in html
    # Non-header non-empty lines should be wrapped in a paragraph tag.
    assert '<p class="prompt-item">This is a paragraph.</p>' in html

def test_combined_elements():
    md = (
        "# Title\n"
        "Introduction text.\n"
        "[[[Input text:something]]]\n"
        "[[Input text:something]]\n"
        "Number: << 100 >>\n"
        "File: (())\n"
        "(* A comment *)\n"
        "[ ] Checkbox Option\n"
        "Inline verbatim: {{{inline code}}}\n"
        "Block verbatim:\n{{{\nBlock\nContent\n}}}"
    )
    html, lang = parse_custom_markdown(md)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check heading
    h1 = soup.find('h1')
    assert h1 is not None and h1.text.strip() == "Title"
    
    # Check paragraph wrapping for the introduction
    intro_paragraph = soup.find('p', class_='prompt-item')
    assert intro_paragraph is not None
    assert "Introduction text." in intro_paragraph.text

    # Check textarea element
    textarea = soup.find('textarea', id='textbox')
    assert textarea is not None, "Textarea with id 'textbox' not found"
    assert textarea.get('placeholder') == "Input text"
    assert "prompt-item" in textarea.get('class', [])
    assert textarea.text.strip() == "something"

    # Check inline text input
    inline_input = soup.find('input', {'type': 'text'})
    assert inline_input is not None, "Inline text input not found"
    assert inline_input.get('placeholder') == "Input text"
    assert inline_input.get('value') == "something"

    # Check inline integer input
    inline_integer = soup.find('input', {'type': 'number'})
    assert inline_integer is not None, "Inline integer input not found"
    assert inline_integer.get('value') == "100"

    # Check file load element
    file_input = soup.find('input', {'type': 'file'})
    assert file_input is not None, "File input not found"

    # Check inline comment
    comment_span = soup.find('span', class_='comment')
    assert comment_span is not None, "Comment span not found"
    assert comment_span.text.strip() == "A comment"

    # Check checkbox element
    checkbox_label = soup.find('label', class_='prompt-item')
    assert checkbox_label is not None, "Checkbox label not found"

    # Check inline verbatim element
    inline_verbatim = soup.find('code')
    assert inline_verbatim is not None, "Inline verbatim code element not found"
    assert inline_verbatim.text.strip() == "inline code"

    # Check block verbatim element exists
    pre_code = soup.find('pre')
    assert pre_code is not None, "Block verbatim (pre element) not found"
