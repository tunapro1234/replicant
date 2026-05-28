# Persona Injection Methods — Research Landscape

35 methods across 6 categories. Sorted by proven success within each category.

## Games / Economics

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 1 | General Social Agents | 2508.17407 | 2026 | Theory-grounded + calibrated mixture | Best: 54% more prob to human actions, beats Nash | Code+data: `benjaminmanning.io`, EDSL |
| 2 | Homo Silicus | 2301.07543 | 2023→2026 | One-sentence behavioral instruction | MSE halved out-of-sample | Code+data: `benjaminmanning.io`, EDSL |
| 3 | Bias-Adjusted LLM | 2508.18600 | 2025 | 21 behavioral indicators + CRT | Replicates ultimatum game | Paper only, no public code |
| 4 | Persona Vectors in Games | 2603.21398 | 2026 | Activation steering (altruism etc) | Shifts strategic choices, rhetoric≠strategy | Paper only, needs open-weight model |
| 5 | LLM Strategic Reasoning | 2502.20432 | 2025 | 22 LLMs × game theory | o3-mini/o1/R1 best; CoT not always helps | Paper only |
| 6 | Automated Social Science | 2404.11794 | 2024 | LLM scientist+subject, SCM | Signs correct, magnitude 13x off; fitted→6x better | Code+data: `benjaminmanning.io` |

## Surveys / Opinion

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 7 | Anthology (narrative) | 2407.06576 | 2024 | Base model + backstory + matching | +18% WD, +27% consistency | Code+data: `github.com/CannyLab/anthology` |
| 8 | Park 1000-People | 2411.10109 | 2024 | Interview transcript injection | 85% GSS, bias reduction | Code: `github.com/joonspk-research/genagents`, transcripts restricted |
| 9 | Twin-2K-500 | 2505.17479 | 2025 | 500-Q self-report calibration | 87% test-retest ceiling | Dataset: `huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500`, code: `github.com/tianyipeng-lab/Digital-Twin-Simulation` |
| 10 | Population-Scale Opinion | 2603.27056 | 2026 | Individual persona modeling | Beyond demographic correlation | Paper only |
| 11 | Digital Personas (LISS) | 2605.10659 | 2026 | RAG from survey history | RAG best for stable values | Paper only, LISS panel data requires application |
| 12 | Polypersona | 2512.14562 | 2025 | LoRA persona fine-tune | TinyLlama matches 7B | Paper only |

## Trait Injection (Prompt)

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 13 | Big5-Scaler | 2508.06149 | 2025 | Numeric scores in NL | r>0.85 correlation | Prompts in appendix, no repo |
| 14 | SAC (16PF) | 2506.20993 | 2025 | Adjective anchoring, 5 intensity dims | 16 traits, dynamic control | Paper only |
| 15 | Safdari/Serapio | 2307.00184 | 2023 | 9-level adjective descriptions | Nature MI, psychometric framework | Prompts in paper |
| 16 | P2 / MPI | 2206.07550 | 2022 | Paragraph descriptions (IPIP) | Early baseline | Items public (IPIP) |
| 17 | PersonaLLM | 2305.02547 | 2023 | Binary adjective pairs | Surface only, 80% human recognition | Code: `github.com/hjian42/PersonaLLM` |

## Activation / Vector

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 18 | Anthropic Persona Vectors | 2507.21509 | 2025 | Contrastive activation extraction | Runtime drift monitoring | Blog+method public, no code release, needs open-weight |
| 19 | PERSONA (vector algebra) | 2602.15669 | 2026 | Orthogonal vectors + arithmetic | ICLR 2026, near fine-tune upper bound | Code: linked in paper, needs open-weight |
| 20 | Personality Vector (merge) | 2509.19727 | 2025 | Weight diff → trait vector → merge | EMNLP 2025, cross-model transfer | Code+vectors: linked in paper |
| 21 | IRIS (situational) | 2604.13846 | 2026 | Neuron-level situational steering | Context-dependent, no training | Paper only, needs open-weight |
| 22 | Activation Hybrid Layer | 2511.03738 | 2025 | Hybrid layer selection | Stability focus | Paper only, needs open-weight |

## Training-Based

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 23 | BIG5-CHAT (SFT+DPO) | 2410.16491 | 2024 | Fine-tune 850K FB posts + SODA | Beats all prompt methods | Dataset: `huggingface.co/datasets/wenkai-li/big5_chat` |
| 24 | Multi-turn RL | 2511.00222 | 2025 | RL persona consistency reward | 55%+ drift reduction | Paper only |
| 25 | FinePE (MoE LoRA) | ScienceDirect | 2026 | Mixture LoRA per sub-trait | Sub-facet control | Paper only |

## Population Generation

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 26 | PersonaHub | 2406.20094 | 2024 | Text-to-Persona + P2P | 1B personas | Dataset: `huggingface.co/datasets/proj-persona/PersonaHub`, code: `github.com/tencent-ailab/persona-hub` |
| 27 | Population-Aligned Gen | 2509.10127 | 2025 | Joint distribution optimization | Panel-level metric | Paper only |
| 28 | Promise with a Catch | 2503.16527 | 2025 | LLM personas biased | More detail ≠ better | ~1M personas open-sourced |
| 29 | Persona Generators (Synthia) | 2602.03545 | 2026 | Social media grounded | Scalable from real data | Paper only |

## Critiques

| # | Method | ArXiv | Year | Type | Key Result | Open |
|---|---|---|---|---|---|---|
| 30 | Evaluation Drift | 2605.16996 | 2026 | Fine-tuned 5D accuracy ~chance | Variance↓ but accuracy↓ | Paper only |
| 31 | Gupta critique | 2309.08163 | 2023 | Prompt sensitivity | Small change → big shift | Paper only |
| 32 | Persona Reliability (WVS) | 2602.18462 | 2026 | 70K instances | Persona often degrades results | Paper only |
| 33 | Personality Illusion | 2509.03730 | 2025 | Self-report ≠ behavior | Trait scores ≠ decisions | Paper only |
| 34 | BFI factor-invalid | 2311.05297 | 2023 | Factor structure broken | Measurement doesn't transfer | Paper only |
| 35 | Pay What LLM Wants | 2508.03262 | 2025 | 522 personas × econ games | Individual <5% | Paper only |

## GitHub Resources

- `github.com/Persdre/awesome-llm-human-simulation` — ICLR 2025 curated list
- `github.com/Neph0s/awesome-llm-role-playing-with-persona` — persona role-playing papers
- `github.com/Nicolas99-9/llm-agent-simulation-papers` — daily auto-updated
- `github.com/VanillaCreamer/Awesome-Personalized-LLMs` — personalization benchmarks
