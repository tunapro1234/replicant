"""
Persona resolution for declarative configs.

A config refers to a persona by a small spec dict; resolve() dispatches it to
the right family builder. This is config glue, NOT a universal persona
interface — each family keeps its own native signature (see personas/__init__).

Spec shapes:
  {"family": "baseline"}
  {"family": "economics", "key": "self_interested"}        # homo_silicus
  {"family": "big5", "spec": {"E": 4, "A": 1, "C": 3, "N": 4, "O": 3}}  # personallm
  {"family": "edsl", "traits": {"persona": "..."}}
"""


def resolve(spec: dict) -> str:
    """Spec dict -> persona system-prompt string."""
    fam = spec.get("family")

    if fam == "baseline":
        from .baseline import build_prompt
        return build_prompt()

    if fam == "economics":
        from .economics.homo_silicus_2301_07543 import (
            ALLOCATION_PERSONAS, POLITICAL_PERSONAS,
        )
        key = spec["key"]
        if key in ALLOCATION_PERSONAS:
            return ALLOCATION_PERSONAS[key]
        if key in POLITICAL_PERSONAS:
            return POLITICAL_PERSONAS[key]
        raise ValueError(f"Unknown economics persona key '{key}'")

    if fam == "big5":
        from .big5 import personallm
        return personallm(**spec.get("spec", {}))

    if fam == "edsl":
        from .edsl import build_prompt
        return build_prompt(spec["traits"])

    raise ValueError(f"Unknown persona family '{fam}'")


def label(spec: dict) -> str:
    """Short human-readable label for a persona spec (for reports/filenames)."""
    fam = spec.get("family")
    if fam == "baseline":
        return "baseline"
    if fam == "economics":
        return spec["key"]
    if fam == "big5":
        s = spec.get("spec", {})
        return "big5_" + "".join(
            f"{k}{'+' if float(s.get(k, 3)) >= 3 else '-'}" for k in "EACNO"
        )
    if fam == "edsl":
        return "edsl"
    return "persona"
