"""Convert XML content to a human-readable markdown representation."""

import xml.etree.ElementTree as ET
from typing import Optional


def _local_tag(elem: ET.Element) -> str:
    """Return tag name without namespace (e.g. {http://...}item -> item)."""
    if elem.tag and "}" in elem.tag:
        return elem.tag.split("}", 1)[1]
    return elem.tag or ""


def _elem_to_markdown(
    elem: ET.Element,
    *,
    depth: int,
    max_heading_level: int,
) -> list[str]:
    """Recursively convert an element and its children to markdown lines."""
    lines: list[str] = []
    tag = _local_tag(elem)
    level = min(depth + 1, max_heading_level)
    heading = "#" * level

    # Heading for this element
    if tag:
        attrs = " ".join(f"_{k}_=`{v}`" for k, v in (elem.attrib or {}).items())
        heading_text = f"{tag}" if not attrs else f"{tag} {attrs}"
        lines.append(f"{heading} {heading_text}")
        lines.append("")

    # Direct text content
    if elem.text and elem.text.strip():
        lines.append(elem.text.strip())
        lines.append("")

    # Children
    for child in elem:
        lines.extend(
            _elem_to_markdown(
                child,
                depth=depth + 1,
                max_heading_level=max_heading_level,
            )
        )
        if child.tail and child.tail.strip():
            lines.append(child.tail.strip())
            lines.append("")

    # Tail after last child
    if len(elem) == 0 and elem.tail and elem.tail.strip():
        lines.append(elem.tail.strip())
        lines.append("")

    return lines


def xml_to_markdown(
    xml_content: str,
    *,
    root_title: Optional[str] = None,
    max_heading_level: int = 6,
) -> str:
    """
    Convert XML string to a human-readable markdown representation.

    Element tags become headings; text nodes become paragraphs. Attributes
    are shown next to the tag. Namespace prefixes are stripped from tag names.

    Args:
        xml_content: Raw XML string (e.g. from a file or RSS feed).
        root_title: Optional title for the document (written as first heading).
        max_heading_level: Maximum markdown heading level 1–6 (default: 6).

    Returns:
        Markdown string representing the XML structure.

    Raises:
        ET.ParseError: If xml_content is not valid XML.
    """
    root = ET.fromstring(xml_content)
    lines: list[str] = []

    if root_title:
        lines.append(f"# {root_title}")
        lines.append("")

    lines.extend(
        _elem_to_markdown(
            root,
            depth=0,
            max_heading_level=max_heading_level,
        )
    )

    return "\n".join(lines).strip() + "\n"
