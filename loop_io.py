"""Shared file-block parsing for agents. DO NOT EDIT."""
import re

FILE_RE = re.compile(r"<<<FILE path=(.+?)>>>\n(.*?)\n<<<END>>>", re.DOTALL)


def extract_files(text: str) -> dict[str, str]:
    """Pull `<<<FILE path=...>>> ... <<<END>>>` blocks out of an agent's reply."""
    return {m.group(1).strip(): m.group(2) for m in FILE_RE.finditer(text)}
