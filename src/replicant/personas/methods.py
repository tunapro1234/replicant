"""
Persona-injection methods — the selectable catalog of *ways* to turn parameters
into a persona system-prompt. The runner picks one with `--method`.

Each method is a builder: build_fn(**params) -> (prompt_string, label).
Adding a new injection method = add a builder here (that's tool development).
Selecting one at run time = `methods.build(name, **params)`.

  baseline      — no persona (control)
  homo_silicus  — Horton's theory / political one-liners (param: persona=<key>)
  personallm    — binary Big Five adjectives (params: E,A,C,N,O on 1-5)
"""


def _baseline(**_):
    return "", "baseline"


def _homo_silicus(persona="self_interested", **_):
    from .economics.homo_silicus_2301_07543 import (
        ALLOCATION_PERSONAS, POLITICAL_PERSONAS,
    )
    if persona in ALLOCATION_PERSONAS:
        return ALLOCATION_PERSONAS[persona], persona
    if persona in POLITICAL_PERSONAS:
        return POLITICAL_PERSONAS[persona], persona
    options = list(ALLOCATION_PERSONAS) + list(POLITICAL_PERSONAS)
    raise ValueError(f"homo_silicus persona '{persona}' unknown. Options: {options}")


def _personallm(E=3.0, A=3.0, C=3.0, N=3.0, O=3.0, **_):
    from .big5 import personallm
    return (personallm(E=E, A=A, C=C, N=N, O=O),
            f"big5_E{E:g}A{A:g}C{C:g}N{N:g}O{O:g}")


METHODS = {
    "baseline": _baseline,
    "homo_silicus": _homo_silicus,
    "personallm": _personallm,
}


def build(method: str, **params) -> tuple:
    """Build (persona_string, label) for the chosen injection method."""
    if method not in METHODS:
        raise ValueError(f"Unknown persona method '{method}'. Options: {list(METHODS)}")
    return METHODS[method](**params)
