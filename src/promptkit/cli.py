"""Simple CLI for promptkit."""

import argparse
import json
import sys

from .prompt import PromptTemplate, PromptValidationError, GuardrailViolation


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="promptkit",
        description="Render and validate LLM prompts with guardrails.",
    )
    parser.add_argument("template", help="Prompt template string or path to .txt file")
    parser.add_argument(
        "--vars", "-v", action="append", default=[],
        help="key=value pairs (repeatable). Example: -v name=Alice -v topic=OSS",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON messages")
    parser.add_argument("--estimate-tokens", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Use stricter default guardrails")

    args = parser.parse_args()

    template_str = args.template
    if template_str.endswith(".txt") or template_str.endswith(".md"):
        try:
            with open(template_str, "r", encoding="utf-8") as f:
                template_str = f.read()
        except Exception as e:
            print(f"Error reading template file: {e}", file=sys.stderr)
            sys.exit(1)

    guardrails = None
    if args.strict:
        from .prompt import Guardrails
        guardrails = Guardrails(
            block_prompt_injection=True,
            max_length=8000,
        )

    try:
        tmpl = PromptTemplate(template=template_str, guardrails=guardrails)
    except Exception as e:
        print(f"Invalid template: {e}", file=sys.stderr)
        sys.exit(1)

    variables = {}
    for pair in args.vars:
        if "=" not in pair:
            print(f"Invalid var format (use key=value): {pair}", file=sys.stderr)
            sys.exit(1)
        k, v = pair.split("=", 1)
        variables[k] = v

    try:
        if args.estimate_tokens:
            tokens = tmpl.estimate_tokens(**variables)
            print(tokens)
            return

        if args.json:
            msgs = tmpl.render_messages(**variables)
            print(json.dumps(msgs, indent=2))
        else:
            print(tmpl.render(**variables))
    except (PromptValidationError, GuardrailViolation) as e:
        print(f"Guardrail/Validation error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
