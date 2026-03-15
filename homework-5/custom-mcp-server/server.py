"""
Custom MCP Server using FastMCP.

Exposes:
  - Resource: lorem://ipsum?word_count=N — returns N words from lorem-ipsum.md
  - Tool:     read(word_count=30)        — calls the resource and returns its content

Concepts:
  Resources are URIs that Claude can read from (e.g. files, APIs). They are
  declared with @mcp.resource and are fetched when Claude needs data.

  Tools are actions Claude can invoke to perform operations (e.g. reading a
  file, running a command). They are declared with @mcp.tool and are called
  when Claude decides to take an action.
"""

import re
from pathlib import Path

from fastmcp import FastMCP

LOREM_FILE = Path(__file__).parent / "lorem-ipsum.md"

mcp = FastMCP("lorem-ipsum-server")


def _get_words(word_count: int) -> str:
    text = LOREM_FILE.read_text(encoding="utf-8")
    words = re.split(r"\s+", text.strip())
    return " ".join(words[:word_count])


@mcp.resource("lorem://ipsum/{word_count}")
def lorem_resource(word_count: int = 30) -> str:
    """Return the first word_count words from lorem-ipsum.md."""
    return _get_words(word_count)


@mcp.tool()
def read(word_count: int = 30) -> str:
    """
    Read word_count words from the lorem ipsum source file.

    Args:
        word_count: Number of words to return (default: 30).

    Returns:
        A string containing exactly word_count words from lorem-ipsum.md.
    """
    return _get_words(word_count)


if __name__ == "__main__":
    mcp.run()
