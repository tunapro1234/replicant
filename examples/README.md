# Examples

Runnable scripts demonstrating common `replicant` use cases.

| # | Script | What it does |
|---|--------|--------------|
| 01 | `01_basic_replication.py` | Replicate a paper with default LLM agents (no personality) |
| 02 | `02_random_personalities.py` | Same paper, agents sampled from US adult Big Five norms |
| 03 | `03_skewed_population.py` | Skewed population (e.g., all disagreeable agents) |
| 04 | `04_custom_traits.py` | Direct OCEAN trait input — exact control over personalities |
| 05 | `05_named_profiles.py` | Use predefined personality archetypes (cooperative, selfish, etc.) |
| 06 | `06_hybrid_humans_bots.py` | Mix LLM bots with human participants in an oTree session |
| 07 | `07_validate_personalities.py` | Validate personality induction with cross-instrument testing |

All scripts run from the **project root**:

```bash
python examples/01_basic_replication.py
```

## Prerequisites

```bash
export OPEN_ROUTER_API_KEY="your-key"
```

Examples 06 (hybrid) and 07 (validation) make real API calls and may take a few minutes.
The other examples either run experiments or just demonstrate the API without API calls.
