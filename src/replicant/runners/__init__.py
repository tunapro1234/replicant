"""
Runner layer — perpendicular to provider/persona/sampling.

A runner takes (persona_string, model) and executes a behavioral-economics
experiment, returning the agent's decisions. Backends:

  otree/   — drive a live oTree experiment (rounds, groups, payoffs, WaitPages)
  (more to come — e.g. direct-prompt runners for paper replications that
   skip oTree and ask the LLM the scenario directly)
"""
