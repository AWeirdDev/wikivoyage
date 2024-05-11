"""Wikivoyage package core.

.. code-block :: python

    wikivoyage.get("https://en.wikivoyage.org/wiki/United_States_of_America")
    # WikivoyageSections(url="...", sections=[...])

Try it yourself.

(c) 2024 AWeirdDev
"""

# DO NOT USE DATACLASSES
# for backwards compatibility.
# I need to use this on the edge.

from __future__ import annotations

from typing import List, Optional, Tuple

import requests
from selectolax.parser import HTMLParser as Parser, Node


def clamp(t: str, m: int = 51):
    """(util) Clamp."""
    assert m > 1 and isinstance(m, int), "m must be greater than 1 and is an int."
    return t[: min(len(t), m - 1)] + ("…" if len(t) > m else "")


class WikivoyageSections:
    def __init__(self, *, url: str, sections: List[dict]):
        self._url = url
        self._sections = [Section(sec) for sec in sections]

    @property
    def url(self) -> str:
        """Requested URL."""
        return self._url

    @property
    def sections(self) -> List[Section]:
        """All category sections."""
        return self._sections

    def __repr__(self) -> str:
        return f"WikivoyageSections(url={clamp(self.url, 21)!r}, sections={self.sections!r})"


class Section:
    """Repersents a Wikivoyage section."""

    def __init__(self, dictionary: dict):
        self._dict = dictionary

    @property
    def title(self) -> str:
        """The section title."""
        return self._dict["section"]

    @property
    def section(self) -> str:
        """The section title. *(alias)*"""
        return self._dict["section"]

    @property
    def content(self) -> str:
        """The section content."""
        return self._dict["content"]

    @property
    def markdown(self) -> str:
        """The section content. *(alias)*"""
        return self._dict["content"]

    def __repr__(self) -> str:
        return f"Section(title={self.title!r}, content={clamp(self.content)!r})"


def get(url: str, **requests_kwargs) -> WikivoyageSections:
    """Fetches a Wikivoyage page and parses it into Markdown.

    Args:
        url (str): The URL.
        **requests_kwargs: Keyword-only arguments to pass into
            `requests.get`.

    Returns:
        WikivoyageSections: Wikivoyage sections.
    """
    r = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
        },
        **requests_kwargs,
    )
    r.raise_for_status()

    block = Node()

    def safe(node: Optional[Node]):
        return block if node is None else node

    def make_markdown(node: Node) -> str:
        text = ""
        iterator = node.iter(include_text=True)

        for n in iterator:
            tag = n.tag

            if not n.text():
                continue

            if tag in {"strong", "b"}:
                text += f"**{n.text()}**"
            elif tag == "i":
                text += f"*{n.text()}*"
            elif tag == "ins":
                text += f"<ins>{n.text()}</ins>"
            elif tag == "a":
                text += f"[{n.text()}](https://en.wikivoyage.org{n.attributes['href']})"
            elif tag in {"meta", "link", "script", "style"}:
                continue
            else:
                tn = n.text(separator=" ", strip=True)

                if not tn:
                    # not a text node
                    text += make_markdown(n)
                else:
                    text += ("" if tn[0] in {",", ".", "!", "?"} else " ") + tn + " "

        return text.strip()

    parser = Parser(r.text)
    title = safe(parser.css_first("#firstHeading h1")).text()

    markdown = ""
    current_sec = title
    sections = []

    def drop():
        nonlocal markdown, current_sec
        if markdown:
            sections.append({"section": current_sec, "content": markdown.strip()})
            markdown = ""

    this = safe(parser.css_first("#mw-content-text .mw-content-ltr"))

    for node in this.iter():
        tag = node.tag

        if tag == "p":
            t = make_markdown(node)
            if t:
                markdown += t + "\n\n"

        elif tag == "h2":
            drop()
            current_sec = safe(node.css_first("span.mw-headline")).text(strip=True)

        elif tag == "ul":
            markdown += "\n"
            for li in node.css("li"):
                markdown += (
                    "- "
                    + li.text(strip=True, separator=" ").replace(chr(8211), ":", 1)
                    + "\n"
                )
            markdown += "\n"

        elif tag == "ol":
            markdown += "\n"
            for i, li in enumerate(node.css("li")):
                markdown += (
                    f"{i+1}. "
                    + li.text(strip=True, separator=" ").replace(chr(8211), ":", 1)
                    + "\n"
                )
            markdown += "\n"

        elif tag in {"meta", "link", "script", "style"}:
            continue

    drop()
    return WikivoyageSections(url=url, sections=sections)

def search(query: str, **requests_kwargs) -> List[Tuple[str, str]]:
    """Search Wikivoyage pages, limited to 10 results.
    
    Args:
        query (str): The query.
        **requests_kwargs: Keyword-only arguments for `requests.get`.
    
    Returns:
        List[Tuple[str, str]]: Returns a list of ``(title, link)``'s.
    """
    r = requests.get(
        "https://en.wikivoyage.org/w/api.php",
        params={
            "action": "opensearch",
            "format": "json",
            "formatversion": "2",
            "search": query,
            "namespace": "0",
            "limit": 10
        }
    )
    data = r.json()
    return list(zip(data[1], data[3]))
