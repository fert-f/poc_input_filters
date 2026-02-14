from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .filters import Finding

GROUP_COLORS: dict[str, tuple[str, str]] = {
    "zero_width": ("#e85d5b", "#0b0b0b"),
    "bidi_control": ("#f28c4b", "#0b0b0b"),
    "tag_block": ("#f1b24a", "#0b0b0b"),
    "control_or_format": ("#e6c453", "#0b0b0b"),
    "non_breaking_space": ("#7fc985", "#0b0b0b"),
    "combining_mark": ("#5f7aa8", "#f6f6f6"),
    "non_ascii": ("#5aa7a0", "#0b0b0b"),
}

DISPLAY_REPLACEMENTS: dict[str, str] = {
    "zero_width": "[ZW]",
    "bidi_control": "[BIDI]",
    "tag_block": "[TAG]",
    "control_or_format": "[CTRL]",
    "non_breaking_space": "[NBSP]",
    "combining_mark": "[COMB]",
    "non_ascii": "[N-ASCII]",
}

DEFAULT_GROUPS = [
    "zero_width",
    "bidi_control",
    "tag_block",
    "control_or_format",
    "non_breaking_space",
    "combining_mark",
    "non_ascii",
]


def highlight_css() -> str:
    rules = [
        "<style>",
        ".highlight-box {",
        "  white-space: pre-wrap;",
        "  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,",
        '    "Liberation Mono", "Courier New", monospace;',
        "  background: var(--secondary-background-color, #f6f4ef);",
        "  border: 1px solid rgba(255, 255, 255, 0.08);",
        "  padding: 12px;",
        "  border-radius: 10px;",
        "  color: var(--text-color, #111111);",
        "}",
        ".flag {",
        "  border-radius: 4px;",
        "  padding: 0 2px;",
        "  margin: 0 1px;",
        "  border: 1px solid rgba(0, 0, 0, 0.25);",
        "}",
    ]

    for group, (bg, fg) in GROUP_COLORS.items():
        rules.append(
            f".group-{group} {{ background: {bg}; color: {fg}; }}",
        )

    rules.append("</style>")
    return "\n".join(rules)


def _display_char(finding: Finding) -> str:
    replacement = DISPLAY_REPLACEMENTS.get(finding.group)
    if replacement is not None:
        if finding.group == "non_ascii":
            return f"{finding.char}{replacement}"
        return replacement
    return finding.char


def render_highlight(
    text: str,
    findings: Iterable[Finding],
    enabled_groups: Iterable[str],
) -> str:
    index_map = {finding.index: finding for finding in findings}
    enabled = set(enabled_groups)
    rendered: list[str] = ['<div class="highlight-box">']

    for index, ch in enumerate(text):
        finding = index_map.get(index)
        if finding and finding.group in enabled:
            display = _display_char(finding)
            title = (
                f"{finding.group} | {finding.codepoint} | {finding.name} "
                f"({finding.category})"
            )
            rendered.append(
                f'<span class="flag group-{finding.group}" title="{escape(title)}">{escape(display)}</span>',
            )
        else:
            rendered.append(escape(ch))

    rendered.append("</div>")
    return "".join(rendered)
