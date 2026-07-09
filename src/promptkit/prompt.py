"""
PromptTemplate: Safe, validated, guardrailed prompt templating for LLMs.

Designed to reduce prompt injection risks, ensure completeness, and
produce consistent outputs across providers (Claude, OpenAI, etc).
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple


class PromptValidationError(ValueError):
    """Raised when prompt variables are missing or invalid."""
    pass


class GuardrailViolation(ValueError):
    """Raised when a guardrail check fails."""
    pass


@dataclass
class Guardrails:
    """Configurable safety and quality guardrails."""
    max_length: Optional[int] = None
    forbidden_patterns: List[str] = field(default_factory=list)
    require_vars: bool = True
    block_prompt_injection: bool = True
    max_var_length: Optional[int] = 2000
    pii_patterns: List[str] = field(default_factory=lambda: [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN-like
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email
    ])

    # Compiled for speed
    _compiled_forbidden: List[Pattern] = field(init=False, repr=False)
    _compiled_pii: List[Pattern] = field(init=False, repr=False)

    def __post_init__(self):
        self._compiled_forbidden = [re.compile(p, re.IGNORECASE) for p in self.forbidden_patterns]
        self._compiled_pii = [re.compile(p, re.IGNORECASE) for p in self.pii_patterns]


@dataclass
class PromptTemplate:
    """
    A safe prompt template with variable substitution, validation and guardrails.

    Example:
        >>> tmpl = PromptTemplate("You are helpful. User says: {{message}}")
        >>> tmpl.render(message="Hello!")
        'You are helpful. User says: Hello!'
    """

    template: str
    name: Optional[str] = None
    description: Optional[str] = None
    required_vars: Optional[Set[str]] = None
    guardrails: Guardrails = field(default_factory=Guardrails)

    # Internal
    _var_pattern: Pattern = field(init=False, repr=False)

    def __post_init__(self):
        if not self.template or not self.template.strip():
            raise ValueError("Template cannot be empty")
        self._var_pattern = re.compile(r"\{\{(\w+)\}\}")
        if self.required_vars is None:
            self.required_vars = set(self._extract_vars())

    def _extract_vars(self) -> List[str]:
        return self._var_pattern.findall(self.template)

    @property
    def variables(self) -> Set[str]:
        """Variables declared or found in the template."""
        return set(self._extract_vars())

    def validate(self, variables: Dict[str, Any]) -> None:
        """Validate that all required variables are provided and pass checks."""
        provided = set(variables.keys())
        missing = self.required_vars - provided if self.required_vars else set()

        if missing:
            raise PromptValidationError(
                f"Missing required variables: {', '.join(sorted(missing))}"
            )

        # Type and length checks
        for key, value in variables.items():
            if not isinstance(value, (str, int, float, bool)):
                # allow basic serializable
                try:
                    str(value)
                except Exception:
                    raise PromptValidationError(f"Variable '{key}' must be string-like")

            sval = str(value)
            if self.guardrails.max_var_length and len(sval) > self.guardrails.max_var_length:
                raise PromptValidationError(
                    f"Variable '{key}' exceeds max_var_length ({self.guardrails.max_var_length})"
                )

            # PII detection
            for p in self.guardrails._compiled_pii:
                if p.search(sval):
                    raise GuardrailViolation(f"Potential PII detected in variable '{key}'")

    def _check_injection(self, text: str) -> None:
        """Basic prompt injection / jailbreak guard."""
        if not self.guardrails.block_prompt_injection:
            return
        lower = text.lower()
        injection_signals = [
            "ignore previous", "ignore all previous", "disregard previous",
            "forget your instructions", "you are now", "new instructions:",
            "system prompt", "###", "<|im_start|>", "<|endoftext|>",
        ]
        for sig in injection_signals:
            if sig in lower:
                raise GuardrailViolation(f"Possible prompt injection detected: '{sig}'")

    def render(self, **variables: Any) -> str:
        """Render the template after validation and guardrail checks."""
        self.validate(variables)

        def replacer(match: re.Match) -> str:
            key = match.group(1)
            val = variables.get(key, "")
            return str(val)

        rendered = self._var_pattern.sub(replacer, self.template)

        # Length guardrail
        if self.guardrails.max_length and len(rendered) > self.guardrails.max_length:
            raise GuardrailViolation(
                f"Rendered prompt exceeds max_length ({self.guardrails.max_length})"
            )

        self._check_injection(rendered)

        # Forbidden patterns
        for pat in self.guardrails._compiled_forbidden:
            if pat.search(rendered):
                raise GuardrailViolation(f"Forbidden pattern matched in rendered prompt")

        return rendered

    def render_messages(self, role: str = "user", **variables: Any) -> List[Dict[str, str]]:
        """Render as chat messages list (works well for Claude / OpenAI)."""
        content = self.render(**variables)
        return [{"role": role, "content": content}]

    def estimate_tokens(self, **variables: Any) -> int:
        """Very rough token estimate ( ~4 chars per token for English )."""
        try:
            rendered = self.render(**variables)
        except Exception:
            rendered = self._var_pattern.sub(lambda m: str(variables.get(m.group(1), "")), self.template)
        return max(1, len(rendered) // 4)

    def __repr__(self) -> str:
        return f"<PromptTemplate name={self.name or 'unnamed'} vars={self.variables}>"


# Convenience factory

def create_prompt(
    template: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    guardrails: Optional[Guardrails] = None,
    **kwargs,
) -> PromptTemplate:
    """Quickly create a PromptTemplate."""
    gr = guardrails or Guardrails(**{k: v for k, v in kwargs.items() if k in Guardrails.__dataclass_fields__})
    return PromptTemplate(template=template, name=name, description=description, guardrails=gr)
