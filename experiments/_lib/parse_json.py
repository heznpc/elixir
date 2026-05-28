"""
Brace-balanced JSON object extraction from LLM output text.

The naive regex `\\{[^{}]*"verdict".*?\\}` fails on outputs where the
JSON value itself contains nested objects (e.g. {"verdict":"...", "usage":{"x":1}}).
The lazy match stops at the FIRST `}`, producing an unbalanced fragment.

`extract_first_balanced_object` walks the text counting braces, respecting
strings (including backslash escapes), and returns the first complete
top-level JSON object substring. Returns "" if none is found.
"""

from __future__ import annotations


def extract_first_balanced_object(text: str) -> str:
    if not text:
        return ""
    n = len(text)
    i = 0
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        # Walk forward tracking depth + string state
        depth = 0
        in_str = False
        esc = False
        j = i
        while j < n:
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        return text[i:j+1]
            j += 1
        # Reached end without balancing this { ; try next
        i += 1
    return ""
