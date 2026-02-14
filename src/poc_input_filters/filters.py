from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass

import ftfy
import regex as re
from cleantext import clean

SAFE_CONTROL_CODEPOINTS = {0x09, 0x0A, 0x0D}
TAG_BLOCK_RANGE = range(0xE0000, 0xE0080)
ZERO_WIDTH_CODEPOINTS = {
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x2060,  # WORD JOINER
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE
}
BIDI_CONTROL_CODEPOINTS = {
    0x061C,  # ARABIC LETTER MARK
    0x200E,  # LEFT-TO-RIGHT MARK
    0x200F,  # RIGHT-TO-LEFT MARK
    *range(0x202A, 0x202F),  # BIDI EMBEDDING/OVERRIDE/POP
    *range(0x2066, 0x206A),  # BIDI ISOLATES
}
NON_BREAKING_SPACES = {
    0x00A0,  # NO-BREAK SPACE
    0x2007,  # FIGURE SPACE
    0x202F,  # NARROW NO-BREAK SPACE
}

GROUP_INFO: dict[str, str] = {
    "zero_width": "Zero-width or joiner characters",
    "bidi_control": "Bidirectional control characters",
    "tag_block": "Unicode tag characters",
    "control_or_format": "Control/format/private-use characters",
    "non_breaking_space": "Non-breaking or fixed-width spaces",
    "combining_mark": "Combining marks that can alter preceding glyphs",
    "non_ascii": "Non-ASCII characters",
}


@dataclass(frozen=True)
class Finding:
    index: int
    char: str
    codepoint: str
    name: str
    category: str
    group: str
    description: str


@dataclass(frozen=True)
class CleanTextOptions:
    fix_unicode: bool = True
    to_ascii: bool = False
    no_urls: bool = False
    no_emails: bool = False
    no_phone_numbers: bool = False
    no_numbers: bool = False
    no_digits: bool = False
    no_currency_symbols: bool = False
    no_punct: bool = False
    replace_with_url: str = "<URL>"
    replace_with_email: str = "<EMAIL>"
    replace_with_phone_number: str = "<PHONE>"
    replace_with_number: str = "<NUMBER>"
    replace_with_digit: str = "<DIGIT>"
    replace_with_currency_symbol: str = "<CUR>"
    lang: str = "en"


@dataclass(frozen=True)
class FilterOptions:
    use_ftfy: bool = True
    strip_invisible: bool = True
    use_clean_text: bool = False
    regex_enabled: bool = False
    regex_pattern: str = ""
    regex_replacement: str = ""
    regex_timeout_ms: int = 50


@dataclass(frozen=True)
class FilterResult:
    text: str
    warnings: list[str]


def _codepoint(ch: str) -> str:
    return f"U+{ord(ch):04X}"


def _describe_group(group: str) -> str:
    return GROUP_INFO.get(group, "Flagged character")


def analyze_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for index, ch in enumerate(text):
        codepoint = _codepoint(ch)
        category = unicodedata.category(ch)
        name = unicodedata.name(ch, "UNKNOWN")
        group: str | None = None

        cp = ord(ch)
        if cp in SAFE_CONTROL_CODEPOINTS:
            continue
        if cp in ZERO_WIDTH_CODEPOINTS:
            group = "zero_width"
        elif cp in BIDI_CONTROL_CODEPOINTS:
            group = "bidi_control"
        elif cp in TAG_BLOCK_RANGE:
            group = "tag_block"
        elif cp in NON_BREAKING_SPACES:
            group = "non_breaking_space"
        elif category.startswith("C"):
            group = "control_or_format"
        elif category in {"Mn", "Mc", "Me"}:
            group = "combining_mark"
        elif cp > 0x7F:
            group = "non_ascii"

        if group is None:
            continue

        findings.append(
            Finding(
                index=index,
                char=ch,
                codepoint=codepoint,
                name=name,
                category=category,
                group=group,
                description=_describe_group(group),
            ),
        )

    return findings


def _is_invisible(ch: str) -> bool:
    cp = ord(ch)
    if cp in SAFE_CONTROL_CODEPOINTS:
        return False
    if cp in TAG_BLOCK_RANGE:
        return True
    category = unicodedata.category(ch)
    return category.startswith("C")


def strip_invisible(text: str) -> str:
    return "".join(ch for ch in text if not _is_invisible(ch))


def _apply_regex(text: str, options: FilterOptions) -> tuple[str, list[str]]:
    if not options.regex_enabled or not options.regex_pattern:
        return text, []

    warnings: list[str] = []
    try:
        updated = re.sub(
            options.regex_pattern,
            options.regex_replacement,
            text,
            timeout=options.regex_timeout_ms / 1000.0,
        )
        return updated, warnings
    except re.TimeoutError:
        warnings.append("Custom regex timed out; input left unchanged.")
    except re.error as exc:
        warnings.append(f"Custom regex error: {exc}.")

    return text, warnings


def _clean_text(text: str, options: CleanTextOptions) -> str:
    clean_kwargs = asdict(options)
    return clean(text, **clean_kwargs)


def apply_filters(
    text: str,
    options: FilterOptions,
    clean_options: CleanTextOptions | None = None,
) -> FilterResult:
    warnings: list[str] = []
    output = text

    if options.use_ftfy:
        output = ftfy.fix_text(output)

    output, regex_warnings = _apply_regex(output, options)
    warnings.extend(regex_warnings)

    if options.strip_invisible:
        output = strip_invisible(output)

    if options.use_clean_text:
        output = _clean_text(output, clean_options or CleanTextOptions())

    return FilterResult(text=output, warnings=warnings)
