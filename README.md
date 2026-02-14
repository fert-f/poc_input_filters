# Input Filter POC

Streamlit demo for analyzing human-to-LLM messages, highlighting hidden or malformed
characters, and applying configurable filters.

## Run

```bash
uv run streamlit run app.py
```

## How It Works

The app has two main stages:

1. **Analyze (no filtering)**
	- Every character is scanned to detect risky classes such as zero-width, bidi
	  controls, tag block characters, control/format codes, non-breaking spaces,
	  combining marks, and non-ASCII characters.
	- The findings table is based on this scan, even when filters are disabled.

2. **Filter (optional, user-controlled)**
	- A pipeline is applied to the input using the toggles in the sidebar.
	- The filtered output is then re-scanned and rendered next to the original.

## Risky Character Classes

The analyzer flags characters that are commonly used to hide or manipulate
content in human-to-LLM messages:

- **Zero-width / joiners**: invisible characters that change tokenization orhide substrings.
-	Risk: can split or merge tokens, hide injected words, or bypass keyword	filters that look for exact substrings.
- **Bidi controls**: can reorder visible text to disguise filenames or content.
-	Risk: can make dangerous content appear harmless (for example, file.exe	looking like file.txt), or reorder prompt text in a way that misleads reviewers.
- **Unicode tag block**: invisible tag characters used for smuggling.
-	Risk: can embed hidden instructions that are not visible to humans but can be	preserved in copy/paste and processing pipelines.
- **Control/format characters**: non-printing characters that can alter parsing.
-	Risk: can break log parsing, alter segmentation, or create invisible paddingthat changes how a prompt is interpreted.
- **Non-breaking spaces**: visually similar to spaces but alter splitting.
-	Risk: can prevent expected token splits, hide extra tokens, or bypass checks that assume normal whitespace.
- **Combining marks**: modify preceding glyphs without being visible on their own.
-	Risk: can create lookalike text or unexpected rendering, complicating review and causing mismatch between what is seen and what is processed.
- **Non-ASCII characters**: can introduce lookalike or unexpected symbols.
-	Risk: can enable homograph tricks (lookalikes), encode hidden meaning, or confuse downstream systems that assume ASCII-only input.

## Filter Pipeline

Filters run in the following order:

1. **ftfy**: fixes broken encoding (mojibake) and some Unicode issues.
2. **regex**: optional custom replacement rule with a timeout guard.
3. **strip_invisible**: removes control/format and tag block characters.
4. **clean-text**: optional normalization and removal of URLs, emails, digits,
	currency symbols, and punctuation based on toggles.

## Features

- Side-by-side original and filtered views.
- Highlighting of suspicious characters with tooltips.
- Findings table with Unicode metadata.
- Preset samples for common smuggling techniques and clean-text testing.


## Presets

The preset list includes:

- Zero-width and word-joiner characters
- Bidi override tricks
- Unicode tag block smuggling
- Non-breaking spaces and combining marks
- Mojibake for `ftfy`
- Prompt injection sample with mixed smuggling techniques
- Clean-text toggle coverage for URLs/emails/phones/numbers/currency/punct

## Notes

- The highlight view escapes user input and only injects trusted spans.
- Filters are applied in this order: ftfy, regex, strip invisibles, clean-text.
- Preset samples include zero-width spaces, bidi controls, tag blocks, and mojibake.
