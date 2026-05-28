"""
Load a declarative experiment config (DESIGN.md #5: experiments are data).

JSON works with zero dependencies. YAML works if pyyaml is installed (the
research norm, but kept optional so core stays dependency-light).
"""

import json


def load(path: str) -> dict:
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "YAML configs need pyyaml — `pip install pyyaml`, or use a .json config."
            )
        with open(path) as f:
            return yaml.safe_load(f)
    with open(path) as f:
        return json.load(f)
