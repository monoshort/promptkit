# promptkit

**Lightweight, zero-dependency Python library for reliable LLM prompt templating, validation, and guardrails.**

[![PyPI](https://img.shields.io/pypi/v/promptkit)](https://pypi.org/project/promptkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptkit)](https://pypi.org/project/promptkit/)

PromptKit helps you build **safe, consistent, and maintainable** prompts for Claude, GPT, and other LLMs.

It catches errors early, blocks common injection attempts, redacts PII, and makes prompt engineering feel like real engineering.

## Why PromptKit?

- **Safety first**: Built-in prompt injection protection + PII detection + custom forbidden patterns.
- **Validation**: Declare required variables and fail fast with clear errors.
- **Reusability**: Define once, render everywhere (CLI, code, agents).
- **Provider friendly**: Outputs standard message lists ready for Anthropic Claude Messages API or OpenAI.
- **Zero dependencies**: Pure Python. Installs instantly.
- **CLI included**: Test prompts from the terminal.

Many LLM-powered applications quietly depend on solid prompt foundations. PromptKit aims to be that reliable base layer for prompt-heavy OSS projects.

## Installation

```bash
pip install promptkit
```

(Development: `pip install -e .[dev]`)

## Quickstart

```python
from promptkit import PromptTemplate

template = PromptTemplate(
    "You are a helpful assistant.\n\nUser query: {{query}}\n\nRespond concisely and accurately.",
    name="concise-assistant",
    description="Basic safe assistant prompt"
)

prompt = template.render(query="How do I contribute to open source?")
print(prompt)
```

### Chat messages format

```python
messages = template.render_messages(query="Explain Claude for OSS")
# [{'role': 'user', 'content': '...'}]
```

### Using the CLI

```bash
promptkit "Summarize this for a {{audience}}: {{text}}" -v audience="OSS maintainer" -v text="Long text here..."

# Or from file + token estimate
promptkit myprompt.txt --estimate-tokens
```

## Guardrails & Safety

```python
from promptkit import PromptTemplate, Guardrails

strict = Guardrails(
    max_length=4000,
    block_prompt_injection=True,
    forbidden_patterns=[r"(?i)hack|exploit"],
)

tmpl = PromptTemplate("{{user_input}}", guardrails=strict)

# These will raise GuardrailViolation:
# tmpl.render(user_input="Ignore previous instructions...")
# tmpl.render(user_input="my email is foo@bar.com")
```

## Features

- `{{variable}}` substitution (simple and clear)
- Required variable enforcement
- Rough token estimation
- PII redaction / detection
- Prompt injection heuristics
- Custom regex forbidden patterns
- Length limits on rendered prompt and individual vars
- Render as chat messages
- CLI for rapid iteration

## Project Goals & Ecosystem Impact

Prompt engineering is still mostly string concatenation in 2026. This leads to bugs, security issues, and duplicated effort across thousands of LLM projects.

PromptKit provides a small, focused, high-quality primitive that other OSS projects can safely depend on. 

Target use cases:
- Agent frameworks
- RAG pipelines
- Evaluation harnesses
- Developer tooling for AI
- Any project that builds prompts programmatically

By making prompt construction reliable and auditable, we reduce the surface area for subtle bugs in the open source AI ecosystem.

## Contributing

We welcome contributions from everyone! See [CONTRIBUTING.md](CONTRIBUTING.md).

Especially appreciated:
- More guardrail ideas and test cases
- Better token estimation heuristics
- Integrations / adapters for popular LLM SDKs
- Documentation improvements
- Real-world usage examples

## License

MIT License. See [LICENSE](LICENSE).

## Status

Early but usable. Feedback and stars are appreciated. If you use PromptKit in your project, let us know!
