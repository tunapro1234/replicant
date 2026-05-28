"""
EDSL persona adapter — use Expected Parrot's Agent class as a persona builder.

EDSL builds the persona (traits dict -> rendered prompt text); our oTree
pipeline runs the experiment. We depend on the `edsl` pip package so their
trait tooling, codebooks, and Jinja persona templates flow in automatically
as they release updates.

Requires `edsl` (Python 3.12 — see project .venv). The import is lazy so the
rest of the repo runs without it.

Source: https://github.com/expectedparrot/edsl  (edsl.Agent)
"""


def build_prompt(traits: dict, instruction: str = None,
                 presentation_template: str = None) -> str:
    """Build a persona string from trait key-values via an EDSL Agent.

    Args:
        traits: dict of agent characteristics, e.g. {"persona": "...", "age": 30}
        instruction: optional directive (defaults to EDSL's standard one)
        presentation_template: optional Jinja2 template for rendering traits

    Returns: instruction + rendered trait presentation, joined.
    """
    from edsl import Agent  # lazy: only needed when EDSL persona is used

    kwargs = {"traits": traits}
    if instruction:
        kwargs["instruction"] = instruction
    if presentation_template:
        kwargs["traits_presentation_template"] = presentation_template

    agent = Agent(**kwargs)
    return f"{agent.instruction}\n{agent.prompt().text}"
