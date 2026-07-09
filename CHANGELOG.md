# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-09

### Added
- Initial release of PromptTemplate with `{{var}}` substitution
- Built-in validation for required variables
- Guardrails: prompt injection detection, PII patterns, forbidden patterns, length limits
- `render()` and `render_messages()` for chat APIs (Claude/OpenAI compatible)
- Rough token estimation
- CLI (`promptkit` command)
- Full test suite
- Professional project scaffolding (pyproject.toml, CI, templates, docs)

### Notes
- Zero runtime dependencies
- MIT licensed
