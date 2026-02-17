# Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [C4 Model Diagrams](#c4-model-diagrams)
  - [Level 1: System Context](#level-1-system-context)
  - [Level 2: Container](#level-2-container)
  - [Level 3: Component](#level-3-component)
  - [Level 4: Code](#level-4-code)
- [Architecture Decisions](#architecture-decisions)
- [Technology Stack](#technology-stack)
- [Security Considerations](#security-considerations)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)

---

## Overview

**Input Filter POC** is a security-focused Streamlit application designed to detect and filter potentially malicious Unicode characters in human-to-LLM messages. The system addresses the growing concern of invisible character smuggling and prompt injection attacks by providing:

1. **Analysis**: Deep inspection of text to identify risky Unicode character classes
2. **Filtering**: Configurable pipeline to remove or normalize suspicious content
3. **Visualization**: Side-by-side comparison with highlighted suspicious characters
4. **Education**: Preset examples demonstrating common attack vectors

---

## C4 Model Diagrams

### Level 1: System Context

The system context shows how the Input Filter POC fits into the broader ecosystem of LLM-based applications.

```mermaid
graph TB
    User[("👤 End User<br/>(Security Analyst,<br/>Developer,<br/>LLM Operator)")]

    System["🛡️ Input Filter POC<br/>[Streamlit Application]<br/><br/>Analyzes and filters<br/>suspicious Unicode characters<br/>in human-to-LLM messages"]

    LLM["🤖 LLM Systems<br/>[External System]<br/><br/>Large Language Model<br/>applications receiving<br/>filtered input"]

    User -->|"Pastes/types text<br/>for analysis"| System
    System -->|"Provides filtered<br/>and analyzed output"| User
    User -.->|"Uses filtered text<br/>for safe LLM input"| LLM

    style System fill:#1168bd,stroke:#0b4884,color:#ffffff
    style User fill:#08427b,stroke:#052e56,color:#ffffff
    style LLM fill:#999999,stroke:#6b6b6b,color:#ffffff
```

**Key Relationships:**
- **User → System**: Provides untrusted text input for security analysis
- **System → User**: Returns filtered output, findings table, and visual highlights
- **User → LLM Systems**: Uses filtered output for safer LLM interactions (out of scope)

---

### Level 2: Container

The container diagram shows the single runtime container that comprises the system.

```mermaid
graph TB
    User[("👤 End User")]

    subgraph boundary ["Input Filter POC [System Boundary]"]
        WebApp["📱 Streamlit Web Application<br/>[Python, Streamlit]<br/><br/>• Interactive web UI<br/>• Filter configuration<br/>• Real-time analysis<br/>• Visual highlighting<br/>• Findings reporting"]
    end

    ExternalLibs["📚 External Libraries<br/>[Python Packages]<br/><br/>• ftfy (encoding fixes)<br/>• clean-text (normalization)<br/>• regex (pattern matching)<br/>• pandas (data display)"]

    User -->|"HTTP/WebSocket<br/>(text input,<br/>filter config)"| WebApp
    WebApp -->|"HTML/JavaScript<br/>(rendered UI,<br/>highlights)"| User
    WebApp -->|"API calls"| ExternalLibs

    style WebApp fill:#1168bd,stroke:#0b4884,color:#ffffff
    style User fill:#08427b,stroke:#052e56,color:#ffffff
    style ExternalLibs fill:#999999,stroke:#6b6b6b,color:#ffffff
```

**Container Details:**

| Container | Technology | Responsibilities | Scaling Strategy |
|-----------|-----------|------------------|------------------|
| **Streamlit Web App** | Python 3.12+, Streamlit | UI rendering, filter orchestration, analysis execution | Single-user sessions; horizontal scaling via Streamlit Cloud |
| **External Libraries** | ftfy, clean-text, regex, pandas | Character normalization, pattern matching, data presentation | N/A (embedded) |

---

### Level 3: Component

The component diagram shows the internal architecture of the Streamlit Web Application.

```mermaid
graph TB
    subgraph boundary ["Streamlit Web Application"]
        UI["🎨 UI Layer<br/>[Streamlit Component]<br/><br/>app.py<br/>• Session state management<br/>• Sidebar controls<br/>• Column layout<br/>• Dataframe rendering"]

        Analyzer["🔍 Analysis Engine<br/>[Python Module]<br/><br/>filters.py:analyze_text()<br/>• Character inspection<br/>• Unicode category checking<br/>• Risk classification<br/>• Finding generation"]

        FilterPipeline["⚙️ Filter Pipeline<br/>[Python Module]<br/><br/>filters.py:apply_filters()<br/>• ftfy encoding fixes<br/>• Regex replacement<br/>• Invisible char stripping<br/>• clean-text normalization"]

        Highlighter["✨ Highlighter<br/>[Python Module]<br/><br/>highlight.py<br/>• CSS generation<br/>• HTML rendering<br/>• Color-coded spans<br/>• Tooltip injection"]

        PresetMgr["📋 Preset Manager<br/>[Python Module]<br/><br/>presets.py<br/>• Sample data storage<br/>• Attack vector examples<br/>• Test case library"]

        DataModel["📦 Data Models<br/>[Python Dataclasses]<br/><br/>• Finding<br/>• FilterOptions<br/>• CleanTextOptions<br/>• FilterResult"]
    end

    User[("👤 End User")]

    User -->|"Selects preset"| UI
    User -->|"Configures filters"| UI
    User -->|"Inputs text"| UI

    UI -->|"Loads sample text"| PresetMgr
    UI -->|"Requests analysis"| Analyzer
    UI -->|"Applies filtering"| FilterPipeline
    UI -->|"Renders highlights"| Highlighter

    Analyzer -->|"Returns findings<br/>(List[Finding])"| UI
    FilterPipeline -->|"Returns filtered text<br/>(FilterResult)"| UI
    Highlighter -->|"Returns HTML<br/>(str)"| UI

    Analyzer -.->|"Uses"| DataModel
    FilterPipeline -.->|"Uses"| DataModel

    style UI fill:#1168bd,stroke:#0b4884,color:#ffffff
    style Analyzer fill:#1168bd,stroke:#0b4884,color:#ffffff
    style FilterPipeline fill:#1168bd,stroke:#0b4884,color:#ffffff
    style Highlighter fill:#1168bd,stroke:#0b4884,color:#ffffff
    style PresetMgr fill:#1168bd,stroke:#0b4884,color:#ffffff
    style DataModel fill:#999999,stroke:#6b6b6b,color:#ffffff
    style User fill:#08427b,stroke:#052e56,color:#ffffff
```

**Component Responsibilities:**

| Component | File(s) | Key Functions | Dependencies |
|-----------|---------|---------------|--------------|
| **UI Layer** | `app.py` | `st.sidebar`, `st.columns`, session management | Streamlit, pandas |
| **Analysis Engine** | `filters.py` | `analyze_text()` | unicodedata, dataclasses |
| **Filter Pipeline** | `filters.py` | `apply_filters()`, `strip_invisible()`, `_apply_regex()` | ftfy, clean-text, regex |
| **Highlighter** | `highlight.py` | `render_highlight()`, `highlight_css()` | html.escape |
| **Preset Manager** | `presets.py` | `PRESETS` constant | dataclasses |
| **Data Models** | `filters.py` | `Finding`, `FilterOptions`, `CleanTextOptions`, `FilterResult` | dataclasses |

---

### Level 4: Code

The code diagram shows the key classes, functions, and their relationships at the implementation level.

```mermaid
classDiagram
    class Finding {
        +int index
        +str char
        +str codepoint
        +str name
        +str category
        +str group
        +str description
    }

    class FilterOptions {
        +bool use_ftfy
        +bool strip_invisible
        +bool use_clean_text
        +bool regex_enabled
        +str regex_pattern
        +str regex_replacement
        +int regex_timeout_ms
    }

    class CleanTextOptions {
        +bool fix_unicode
        +bool to_ascii
        +bool no_urls
        +bool no_emails
        +bool no_phone_numbers
        +bool no_numbers
        +bool no_digits
        +bool no_currency_symbols
        +bool no_punct
        +str replace_with_url
        +str replace_with_email
        +str replace_with_phone_number
        +str replace_with_number
        +str replace_with_digit
        +str replace_with_currency_symbol
        +str lang
    }

    class FilterResult {
        +str text
        +list~str~ warnings
    }

    class Preset {
        +str label
        +str text
        +str description
    }

    class AnalysisEngine {
        +analyze_text(text: str) list~Finding~
        -_codepoint(ch: str) str
        -_describe_group(group: str) str
    }

    class FilterPipeline {
        +apply_filters(text, options, clean_options) FilterResult
        +strip_invisible(text: str) str
        -_apply_regex(text, options) tuple
        -_clean_text(text, options) str
        -_is_invisible(ch: str) bool
    }

    class Highlighter {
        +render_highlight(text, findings, groups) str
        +highlight_css() str
        -_display_char(finding: Finding) str
    }

    class Constants {
        +SAFE_CONTROL_CODEPOINTS: set
        +TAG_BLOCK_RANGE: range
        +ZERO_WIDTH_CODEPOINTS: set
        +BIDI_CONTROL_CODEPOINTS: set
        +NON_BREAKING_SPACES: set
        +GROUP_INFO: dict
        +GROUP_COLORS: dict
        +DISPLAY_REPLACEMENTS: dict
    }

    AnalysisEngine --> Finding : creates
    AnalysisEngine --> Constants : uses
    FilterPipeline --> FilterOptions : uses
    FilterPipeline --> CleanTextOptions : uses
    FilterPipeline --> FilterResult : creates
    Highlighter --> Finding : consumes
    Highlighter --> Constants : uses

    note for Finding "Immutable frozen dataclass<br/>representing a single<br/>risky character detection"
    note for FilterOptions "User configuration for<br/>filter pipeline stages"
    note for FilterResult "Output of filter pipeline:<br/>processed text + warnings"
```

**Key Design Patterns:**

1. **Immutable Data Classes**: All data models use `@dataclass(frozen=True)` for thread safety and predictability
2. **Pipeline Pattern**: Filters applied in sequence: ftfy → regex → strip_invisible → clean-text
3. **Separation of Concerns**: Analysis (detection) is independent from filtering (transformation)
4. **Constants Module Pattern**: Centralized Unicode character sets for maintainability

**Critical Functions:**

```python
# Core analysis function
def analyze_text(text: str) -> list[Finding]:
    """
    Scans every character in text and returns findings for risky characters.
    Detection is independent of filtering configuration.
    """

# Core filtering function
def apply_filters(
    text: str,
    options: FilterOptions,
    clean_options: CleanTextOptions | None = None,
) -> FilterResult:
    """
    Applies filter pipeline in order:
    1. ftfy (if enabled)
    2. Custom regex (if enabled, with timeout protection)
    3. Strip invisible characters (if enabled)
    4. clean-text normalization (if enabled)
    """

# Core rendering function
def render_highlight(
    text: str,
    findings: Iterable[Finding],
    enabled_groups: Iterable[str],
) -> str:
    """
    Generates HTML with <span> elements for flagged characters.
    Each span includes color coding and tooltip with Unicode metadata.
    """
```

---

## Architecture Decisions

### ADR-001: Single-Container Streamlit Application

**Status**: Accepted

**Context**: Need to rapidly prototype a security tool for Unicode analysis while maintaining ease of deployment and iteration.

**Decision**: Use Streamlit as the single application framework, combining UI, business logic, and presentation in one Python codebase.

**Consequences**:
- ✅ **Pros**: Rapid development, easy deployment, low complexity, built-in session state
- ⚠️ **Cons**: Limited scalability, coupled architecture, Streamlit-specific patterns

**Alternatives Considered**: Flask/FastAPI + React (rejected: overkill for POC), Jupyter Notebook (rejected: poor UX for end users)

---

### ADR-002: Analysis Before Filtering

**Status**: Accepted

**Context**: Users need to understand what's in the original text regardless of filter settings.

**Decision**: Always analyze the original text first, then apply filters separately. The findings table always reflects the original input, even when filters are disabled.

**Consequences**:
- ✅ **Pros**: Consistent detection, educational value, no hidden risks
- ⚠️ **Cons**: Slight performance overhead (double scanning), potential user confusion

---

### ADR-003: Ordered Filter Pipeline

**Status**: Accepted

**Context**: Filter order affects results. For example, ftfy might introduce non-ASCII characters that need subsequent filtering.

**Decision**: Enforce strict pipeline order:
1. `ftfy` (fix encoding)
2. Custom regex (user-defined transformations)
3. `strip_invisible` (remove control/format characters)
4. `clean-text` (normalization and structured data removal)

**Consequences**:
- ✅ **Pros**: Predictable behavior, composable filters, handles edge cases (e.g., ftfy → non-ASCII)
- ⚠️ **Cons**: Order is non-negotiable, may not fit all use cases

---

### ADR-004: Regex Timeout Protection

**Status**: Accepted

**Context**: User-provided regex patterns could cause catastrophic backtracking (ReDoS attacks).

**Decision**: Enforce configurable timeout (default 50ms) on custom regex operations using the `regex` module's timeout feature.

**Consequences**:
- ✅ **Pros**: Prevents UI hangs, protects against ReDoS, user-configurable
- ⚠️ **Cons**: Requires `regex` module instead of stdlib `re`, timeout errors need handling

---

### ADR-005: Frozen Dataclasses for Data Models

**Status**: Accepted

**Context**: Need immutable, type-safe data structures for configuration and results.

**Decision**: Use `@dataclass(frozen=True)` for all data models (`Finding`, `FilterOptions`, `CleanTextOptions`, `FilterResult`, `Preset`).

**Consequences**:
- ✅ **Pros**: Immutability prevents accidental mutations, better IDE support, hashable types
- ⚠️ **Cons**: Slightly more verbose updates (requires `dataclasses.replace()`), Python 3.7+ required

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.12+ | Application language |
| **UI Framework** | Streamlit | Latest | Web interface |
| **Encoding Repair** | ftfy | Latest | Fix mojibake and Unicode corruption |
| **Text Cleaning** | clean-text | Latest | Remove URLs, emails, phones, normalize text |
| **Pattern Matching** | regex | Latest | Unicode-aware regex with timeout support |
| **Data Display** | pandas | Latest | Findings table rendering |
| **Package Manager** | uv | Latest | Fast, modern Python package management |

### Key Dependencies

```toml
[project]
name = "poc-input-filters"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "streamlit",
    "ftfy",
    "clean-text",
    "regex",
    "pandas",
]
```

### Development Tools

- **Formatter**: ruff (implicit via modern-python skill)
- **Type Checker**: pyright/mypy (recommended but not enforced in POC)
- **Test Framework**: pytest (not yet implemented)

---

## Security Considerations

### Input Validation

**Current State**: The application is designed to handle **untrusted input**, as its primary purpose is analyzing potentially malicious text.

**Protections**:
1. **HTML Escaping**: All user input is escaped using `html.escape()` before rendering
2. **Regex Timeout**: Custom regex has a configurable timeout to prevent ReDoS attacks
3. **No Code Execution**: No `eval()`, `exec()`, or dynamic imports of user data
4. **Streamlit Sandboxing**: Streamlit's `unsafe_allow_html` is only used for **trusted** spans generated by the application

### Known Limitations

1. **Client-Side Rendering**: Highlighting is rendered on the client; malicious Unicode could potentially affect user's browser rendering engine (XSS via Unicode exploits is unlikely but theoretically possible)
2. **No Rate Limiting**: As a POC, there's no rate limiting on analysis requests
3. **Session State**: Session state is ephemeral; no persistent storage or user authentication

### Recommended Mitigations for Production

1. **Content Security Policy (CSP)**: Deploy with strict CSP headers
2. **Rate Limiting**: Implement per-IP or per-session rate limiting
3. **Audit Logging**: Log all analysis requests for security monitoring
4. **Input Size Limits**: Enforce maximum text length (e.g., 100KB)
5. **Sandboxed Execution**: Run in isolated container (Docker/K8s)

### OWASP Top 10 for LLM Applications (2025)

This tool addresses several OWASP LLM risks:

| OWASP Risk | How This Tool Mitigates |
|------------|-------------------------|
| **LLM01: Prompt Injection** | Detects and filters invisible characters commonly used in prompt injection attacks (zero-width, bidi controls, tag blocks) |
| **LLM03: Training Data Poisoning** | N/A (no training data handling) |
| **LLM04: Model Denial of Service** | Helps prevent crafted inputs with invisible tokens that could inflate context length |
| **LLM06: Sensitive Information Disclosure** | Detects hidden characters that could exfiltrate data via invisible text |

---

## Data Flow

### Analysis Flow (No Filtering)

```mermaid
sequenceDiagram
    actor User
    participant UI as UI Layer
    participant Analyzer as Analysis Engine
    participant Highlighter as Highlighter

    User->>UI: Paste text + disable filters
    UI->>Analyzer: analyze_text(raw_text)

    loop For each character
        Analyzer->>Analyzer: Check Unicode category
        Analyzer->>Analyzer: Classify into risk group
    end

    Analyzer-->>UI: list[Finding]
    UI->>Highlighter: render_highlight(text, findings)
    Highlighter-->>UI: HTML with spans
    UI-->>User: Display highlighted text + findings table
```

### Filtering Flow (With Filters Enabled)

```mermaid
sequenceDiagram
    actor User
    participant UI as UI Layer
    participant Analyzer as Analysis Engine
    participant Pipeline as Filter Pipeline
    participant Highlighter as Highlighter

    User->>UI: Paste text + enable filters
    UI->>Analyzer: analyze_text(raw_text)
    Analyzer-->>UI: original_findings

    UI->>Pipeline: apply_filters(text, options)

    alt ftfy enabled
        Pipeline->>Pipeline: ftfy.fix_text()
    end

    alt regex enabled
        Pipeline->>Pipeline: regex.sub() with timeout
    end

    alt strip_invisible enabled
        Pipeline->>Pipeline: strip_invisible()
    end

    alt clean_text enabled
        Pipeline->>Pipeline: clean()
    end

    Pipeline-->>UI: FilterResult(filtered_text, warnings)
    UI->>Analyzer: analyze_text(filtered_text)
    Analyzer-->>UI: filtered_findings

    par Render both views
        UI->>Highlighter: render_highlight(raw_text, original_findings)
        Highlighter-->>UI: original_html
        UI->>Highlighter: render_highlight(filtered_text, filtered_findings)
        Highlighter-->>UI: filtered_html
    end

    UI-->>User: Display side-by-side + findings table
```

---

## Extension Points

### Adding New Character Groups

To detect a new category of risky characters:

1. **Update constants** in `filters.py`:
   ```python
   NEW_GROUP_CODEPOINTS = {0x1234, 0x5678}  # Add codepoints
   GROUP_INFO["new_group"] = "Description of new group"
   ```

2. **Update detection logic** in `analyze_text()`:
   ```python
   elif cp in NEW_GROUP_CODEPOINTS:
       group = "new_group"
   ```

3. **Update highlighting** in `highlight.py`:
   ```python
   GROUP_COLORS["new_group"] = ("#hexcolor", "#textcolor")
   DISPLAY_REPLACEMENTS["new_group"] = "[NEW]"
   DEFAULT_GROUPS.append("new_group")
   ```

### Adding New Filters

To add a new filter stage:

1. **Create filter function** in `filters.py`:
   ```python
   def new_filter(text: str, options: SomeOptions) -> str:
       # Transform text
       return transformed
   ```

2. **Update FilterOptions** dataclass:
   ```python
   @dataclass(frozen=True)
   class FilterOptions:
       # ... existing fields
       use_new_filter: bool = False
       new_filter_param: str = "default"
   ```

3. **Add to pipeline** in `apply_filters()`:
   ```python
   if options.use_new_filter:
       output = new_filter(output, options)
   ```

4. **Update UI** in `app.py`:
   ```python
   use_new_filter = st.sidebar.checkbox("Enable new filter", value=False)
   ```

### Adding New Presets

To add sample text for testing:

1. **Update `presets.py`**:
   ```python
   PRESETS.append(
       Preset(
           label="New Attack Vector",
           text="Sample text with suspicious characters",
           description="Description of the attack technique",
       )
   )
   ```

### API-ification

To convert this POC into an API service:

1. **Replace Streamlit** with FastAPI/Flask:
   ```python
   @app.post("/analyze")
   def analyze_endpoint(request: AnalyzeRequest):
       findings = analyze_text(request.text)
       return {"findings": [asdict(f) for f in findings]}

   @app.post("/filter")
   def filter_endpoint(request: FilterRequest):
       result = apply_filters(
           request.text,
           FilterOptions(**request.options),
       )
       return asdict(result)
   ```

2. **Add authentication** (JWT, API keys)
3. **Add rate limiting** (e.g., slowapi, Flask-Limiter)
4. **Containerize** with Docker
5. **Add OpenAPI documentation** (Swagger)

---

## Deployment Architecture (Future)

For production deployment, consider this evolution:

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["🌐 Web Browser"]
    end

    subgraph "Edge Layer"
        CDN["📡 CDN/CloudFlare"]
        WAF["🛡️ WAF"]
    end

    subgraph "Application Layer"
        LB["⚖️ Load Balancer"]
        App1["📱 Streamlit Instance 1"]
        App2["📱 Streamlit Instance 2"]
        AppN["📱 Streamlit Instance N"]
    end

    subgraph "Observability Layer"
        Logs["📋 Centralized Logging<br/>(ELK/Datadog)"]
        Metrics["📊 Metrics<br/>(Prometheus/Grafana)"]
        Traces["🔍 Tracing<br/>(Jaeger/Honeycomb)"]
    end

    Browser --> CDN
    CDN --> WAF
    WAF --> LB
    LB --> App1
    LB --> App2
    LB --> AppN

    App1 -.->|logs| Logs
    App2 -.->|logs| Logs
    AppN -.->|logs| Logs

    App1 -.->|metrics| Metrics
    App2 -.->|metrics| Metrics
    AppN -.->|metrics| Metrics

    App1 -.->|traces| Traces
    App2 -.->|traces| Traces
    AppN -.->|traces| Traces

    style Browser fill:#08427b,stroke:#052e56,color:#ffffff
    style CDN fill:#999999,stroke:#6b6b6b,color:#ffffff
    style WAF fill:#999999,stroke:#6b6b6b,color:#ffffff
    style LB fill:#999999,stroke:#6b6b6b,color:#ffffff
    style App1 fill:#1168bd,stroke:#0b4884,color:#ffffff
    style App2 fill:#1168bd,stroke:#0b4884,color:#ffffff
    style AppN fill:#1168bd,stroke:#0b4884,color:#ffffff
    style Logs fill:#999999,stroke:#6b6b6b,color:#ffffff
    style Metrics fill:#999999,stroke:#6b6b6b,color:#ffffff
    style Traces fill:#999999,stroke:#6b6b6b,color:#ffffff
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Bidi Controls** | Bidirectional text control characters (U+202A-202E, U+2066-2069) that change text rendering direction |
| **C4 Model** | Context, Containers, Components, Code - a hierarchical software architecture diagramming approach |
| **Clean-text** | Python library for text normalization (URL/email removal, Unicode fixes, etc.) |
| **Combining Mark** | Unicode characters (category Mn/Mc/Me) that modify preceding glyphs |
| **Finding** | A detected instance of a risky character in analyzed text |
| **ftfy** | "Fixes Text For You" - Python library for repairing broken Unicode and mojibake |
| **Mojibake** | Garbled text resulting from character encoding mismatch |
| **Non-breaking Space** | Whitespace characters (U+00A0, U+2007, U+202F) that prevent line breaks |
| **Prompt Injection** | Security attack where malicious instructions are embedded in LLM prompts |
| **ReDoS** | Regular Expression Denial of Service - attack using pathological regex patterns |
| **Tag Block** | Unicode range (U+E0000-E007F) for invisible tag characters |
| **Zero-width** | Invisible Unicode characters (U+200B-200D, U+2060, U+FEFF) with zero display width |

---

## References

- [C4 Model](https://c4model.com/) - Simon Brown's architecture diagramming approach
- [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Unicode Standard](https://unicode.org/standard/standard.html) - Character encoding reference
- [Streamlit Documentation](https://docs.streamlit.io/) - UI framework
- [ftfy Documentation](https://ftfy.readthedocs.io/) - Text repair library
- [clean-text PyPI](https://pypi.org/project/clean-text/) - Text normalization library

---

**Document Version**: 1.0
**Last Updated**: February 16, 2026
**Maintained By**: Development Team
