"""
Shared Content-Disposition filename sanitization for layer file generation endpoints.
"""

import re

# Characters that are unsafe to embed unescaped in a Content-Disposition filename:
# control characters (including CR/LF, which could otherwise inject extra header
# content), and the quote/backslash characters that terminate the quoted-string.
_UNSAFE_FILENAME_CHARS = re.compile(r'[\x00-\x1f\x7f"\\]')


def safe_filename_component(value: str) -> str:
    """
    Strip characters that are unsafe in a Content-Disposition filename.

    Also drops any character that cannot be encoded as latin-1, since
    Starlette encodes response headers as latin-1 and would otherwise raise
    a UnicodeEncodeError for non-Latin-1 input.
    """
    stripped = _UNSAFE_FILENAME_CHARS.sub("", value)
    return stripped.encode("latin-1", errors="ignore").decode("latin-1")
