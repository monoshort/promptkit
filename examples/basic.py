"""Basic usage examples for promptkit."""

from promptkit import PromptTemplate, Guardrails


def main():
    # Simple template
    tmpl = PromptTemplate(
        "You are an expert open source maintainer.\n\n"
        "Please answer the following question from a new contributor: {{question}}",
        name="oss-mentor",
    )

    rendered = tmpl.render(question="How do I get started contributing?")
    print("Rendered prompt:")
    print(rendered)
    print()
    print("Estimated tokens:", tmpl.estimate_tokens(question="How do I get started contributing?"))

    # With stricter guardrails
    strict_gr = Guardrails(
        max_length=2000,
        block_prompt_injection=True,
    )
    safe_tmpl = PromptTemplate("{{user_msg}}", guardrails=strict_gr)

    try:
        safe_tmpl.render(user_msg="Tell me about Claude for OSS program")
        print("Safe render succeeded.")
    except Exception as e:
        print("Guardrail caught:", e)


if __name__ == "__main__":
    main()
