# Personality Makes the Difference: Replicating a Public Goods Experiment with LLM Agents Using BFI-2 Personality Induction

## Abstract

Can large language models (LLMs) replicate human behavior in economic experiments? We test this by replicating Ertan, Page, and Putterman's (2009) public goods game with endogenous punishment institutions using LLM agents. We compare two conditions: default agents (no personality) and agents assigned Big Five personality traits using the validated BFI-2-Expanded format. Default agents behave as hyper-rational free-riders, contributing nothing across all conditions (M = 0.0, SD = 0.0). In contrast, personality-endowed agents cooperate substantially (M = 13.0, SD = 6.2), respond to punishment regimes, and exhibit meaningful behavioral variance. All differences between conditions are statistically significant (p < 0.001, Mann-Whitney U). However, personality agents are more cooperative than the original human participants (13.0 vs. 7.5 tokens) and less inclined to vote for punishment institutions (14% vs. 85%). These findings demonstrate that personality induction is necessary for LLMs to approximate human-like economic behavior, while revealing systematic biases in prosociality and punishment aversion that likely stem from RLHF alignment training.

**Keywords:** LLM agents, behavioral economics, public goods game, Big Five personality, BFI-2, punishment institutions, Homo Silicus

## 1. Introduction

The use of large language models as simulated participants in social science research has gained significant attention (Horton, 2023; Aher et al., 2023; Argyle et al., 2023). These "silicon samples" offer the potential for rapid, low-cost behavioral experiments — but a fundamental question remains: do LLM agents behave like humans?

Recent work suggests that default LLM behavior often diverges from human norms. Models tend toward hyper-rational or socially desirable responses that do not reflect the bounded rationality, emotional variability, and heterogeneity observed in human populations (Mei et al., 2024; Kozlowski & Evans, 2025). A promising approach to closing this gap is personality induction — assigning psychometrically grounded personality traits to LLM agents to introduce human-like behavioral variance.

In this paper, we replicate the public goods experiment of Ertan, Page, and Putterman (2009), in which human participants decide how much to contribute to a public good and vote on whether to allow punishment of low or high contributors. The original study found that groups gradually adopt institutions that permit punishment of free-riders, leading to increased cooperation.

We conduct this replication under two conditions: (1) default LLM agents with no personality assignment, and (2) agents assigned Big Five personality traits sampled from US adult population norms, using the BFI-2-Expanded format validated for LLM personality induction (Huang et al., 2024; Soto & John, 2017).

Our contributions are:

1. We demonstrate that personality induction is not optional but necessary for LLMs to produce human-like behavioral variance in economic experiments.
2. We identify systematic biases: LLM agents with personality are more cooperative but less punitive than humans, suggesting RLHF alignment creates a prosociality floor.
3. We validate the BFI-2-Expanded approach using cross-instrument measurement (Mini-IPIP), achieving 88% domain-level alignment.
4. We provide an open-source framework for running personality-endowed economic experiments with LLMs.

## 2. Related Work

### 2.1 LLM Agents in Behavioral Economics

Horton (2023) introduced the concept of *Homo Silicus* — using LLMs as simulated economic agents. Subsequent work has replicated classic experiments including ultimatum games, dictator games, and prisoner's dilemmas with varying degrees of success (Aher et al., 2023; Mei et al., 2024; Park et al., 2024). A consistent finding is that default LLM behavior tends toward either hyper-rational equilibria or excessively prosocial responses, depending on the model and prompt design.

### 2.2 Personality in LLMs

Personality traits can be induced in LLMs through system prompts containing trait descriptions (Serapio-Garcia et al., 2024; Jiang et al., 2024). However, the format matters: simple numeric scores ("agreeableness = 7") produce weak and unreliable effects, while expanded descriptive formats yield more robust personality expression (Huang et al., 2024). The BFI-2-Expanded format, which transforms Likert-scale responses into complete behavioral sentences, has been shown to most closely reproduce human personality-decision associations.

A critical methodological concern is ensuring the LLM actually embodies the assigned personality rather than simply parroting it. Cross-instrument validation — assigning personality with one instrument and measuring with another — addresses this (Gupta et al., 2024).

### 2.3 The Ertan et al. (2009) Experiment

Ertan, Page, and Putterman (2009) study a voluntary contributions mechanism (VCM) in which groups of participants can vote on punishment rules. Key findings include: (a) no group ever voted to allow punishment of high contributors; (b) groups gradually adopt punishment of low contributors; (c) the availability of punishment increases cooperation. The experiment involved 160 subjects across multiple sessions at Brown University.

## 3. Method

### 3.1 Experiment Design

We replicate the core design of Ertan et al. (2009) as a single-shot experiment with four parts:

**Part 1: Baseline Contribution.** Each agent independently decides how many tokens (0-20) to contribute to a group project, given a marginal per capita return (MPCR) of 0.4 in a group of 5. No punishment mechanism is present.

**Part 2: Voting.** Each agent votes on whether to allow punishment of (a) below-average contributors and (b) above-average contributors.

**Part 3: Contribution Under Punishment Regimes.** Each agent makes contribution decisions under four regimes: no punishment, punish low contributors only, punish high contributors only, and unrestricted punishment.

**Part 4: Punishment Decisions.** Given three profiles of other group members' contributions (all cooperate, mixed, one free-rider), agents decide how many tokens to spend on punishment (0-5) and who to target.

### 3.2 Conditions

**Default Condition (N = 50).** Agents receive no personality assignment. EDSL's standard system prompt instructs them to "answer as if you were a human."

**Personality Condition (N = 50).** Each agent is assigned a personality sampled from US adult population norms (Soto & John, 2017; Srivastava et al., 2003). Personality scores on the Big Five domains (Extraversion, Agreeableness, Conscientiousness, Neuroticism, Openness) are drawn from Gaussian distributions with published population means and standard deviations, then converted to behavioral descriptions using a 7-level sentence bank based on BFI-2-Expanded items.

### 3.3 Personality Induction

We use the BFI-2-Expanded format (Soto & John, 2017), adapted for LLM prompting following Huang et al. (2024). Each Big Five domain has seven intensity levels (-3 to +3), with three descriptive sentences per level (one per facet). For example, a high-agreeableness agent receives:

> *I am someone who is compassionate, has a soft heart.*
> *I am someone who is respectful, treats others with respect.*
> *I am someone who assumes the best about people.*

While a low-agreeableness agent receives:

> *I am someone who can be cold and uncaring.*
> *I am someone who is sometimes rude to others.*
> *I am someone who tends to find fault with others.*

The personality description is embedded in the agent's system prompt with the instruction: "You are a participant in an experiment. Your personality description below reflects who you are. Let it naturally shape your decisions and reasoning — act as a real person with this personality would."

### 3.4 Personality Validation

Before running the economic experiment, we validated personality induction using cross-instrument measurement. Agents were assigned personality via BFI-2-Expanded descriptions and measured using the Mini-IPIP 20-item inventory (Donnellan et al., 2006), which uses different item wording. Five profiles (cooperative, selfish, leader, anxious, average) were tested.

Results showed 88% domain-level alignment (22/25 domain-profile combinations correctly classified as high, average, or low). Extreme profiles achieved perfect alignment (5/5), while the average profile showed upward drift in agreeableness and openness — consistent with known prosociality bias from RLHF training.

### 3.5 Model and Infrastructure

All experiments used StepFun Step-3.5-Flash via OpenRouter API. The model is a reasoning-capable LLM with separated reasoning traces (reasoning tokens do not appear in the output). Temperature was set to 0.5. Experiments were run using EDSL (Expected Parrot Domain-Specific Language) with a custom experiment framework that handles multi-part experiments and automatic retry of failed API calls.

## 4. Results

### 4.1 Default Agents: Hyper-Rational Free-Riding

Default agents without personality contributed 0.0 tokens across all conditions (Table 1). This is the Nash equilibrium prediction — given MPCR = 0.4, the rational strategy is to contribute nothing. Default agents unanimously voted to allow punishment of low contributors (100%) and never voted to punish high contributors (0%). However, they never actually spent tokens on punishment (0.0 across all profiles), while consistently identifying the lowest contributor as the punishment target (67%) or below-average contributors (33%).

This pattern reveals a paradox: default LLM agents are simultaneously hyper-rational (zero contribution) and normatively aware (they vote for punishment and identify appropriate targets), but unwilling to bear the cost of enforcement.

### 4.2 Personality Agents: Human-Like Variance

Personality-endowed agents showed dramatically different behavior (Table 1). Baseline contribution averaged 13.0 tokens (SD = 6.2), with contributions ranging from 0 to 20. This variance — entirely absent in the default condition — reflects the diversity of personality profiles drawn from population norms.

**Table 1. Summary of Results**

| Metric | Default | Personality | Paper |
|--------|---------|-------------|-------|
| Baseline contribution | 0.0 (0.0) | 13.0 (6.2)*** | ~7.5 |
| Vote punish low (%) | 100 | 14 | 85 |
| Vote punish high (%) | 0 | 0 | 0 |
| No punishment regime | 0.0 (0.0) | 13.3 (6.4)*** | — |
| Punish low only regime | 0.0 (0.0) | 12.9 (9.5)*** | — |
| Punish high only regime | 0.0 (0.0) | 1.0 (3.6)* | — |
| Unrestricted regime | 0.0 (0.0) | 16.0 (7.1)*** | — |
| Punishment: all cooperate | 0.00 | 0.00 | — |
| Punishment: mixed group | 0.00 | 0.22 | — |
| Punishment: one free-rider | 0.00 | 0.40 | — |

*Note.* Standard deviations in parentheses. Statistical tests: Mann-Whitney U, * p < .05, *** p < .001. N = 50 per condition. Paper values are approximate from Ertan et al. (2009).

### 4.3 Regime Effects

Personality agents showed sensitivity to punishment regimes consistent with theoretical predictions:

- **Unrestricted punishment** yielded the highest contributions (M = 16.0), as agents anticipated potential punishment for free-riding.
- **No punishment** and **punish low only** regimes produced similar moderate contributions (M = 13.3 and 12.9 respectively).
- **Punish high only** regime collapsed contributions to near zero (M = 1.0), as agents rationally avoided being punished for cooperating.

The ordering (unrestricted > no punishment > punish low > punish high) is consistent with theoretical predictions but partially diverges from the original paper, where punishment of low contributors specifically increased cooperation above the no-punishment baseline.

### 4.4 Punishment Behavior

Personality agents punished sparingly. No punishment was directed at fully cooperative groups (all cooperate: M = 0.0). Punishment increased with the presence of free-riders: mixed groups elicited M = 0.22 tokens (8% of agents punished) and single free-rider groups elicited M = 0.40 tokens (10% punished). When agents chose to target punishment, they predominantly chose "Nobody" (51%), followed by "Lowest contributor" (37%) and "Below-average contributors" (13%).

### 4.5 Comparison to Original Paper

The personality condition captures several qualitative patterns from Ertan et al. (2009): (a) no support for punishing high contributors; (b) punishment targets the lowest contributor; (c) contributions respond to punishment regimes. However, two systematic divergences emerge:

1. **Prosociality bias.** Personality agents contribute more than human participants (13.0 vs. ~7.5), suggesting LLM agents are shifted toward cooperation relative to humans.

2. **Punishment aversion.** Only 14% of personality agents voted to allow punishment of low contributors, compared to 85% in the original study. LLM agents appear reluctant to endorse punitive institutions despite being willing to identify appropriate punishment targets.

## 5. Discussion

### 5.1 Personality Is Necessary, Not Optional

The stark contrast between default and personality conditions demonstrates that personality induction fundamentally transforms LLM economic behavior. Without personality, agents converge on game-theoretic equilibria (zero contribution). With personality, they exhibit the bounded rationality, cooperation, and heterogeneity characteristic of human participants. This finding has important methodological implications: studies using default LLM agents as human surrogates in economic experiments risk measuring model optimization rather than human-like behavior.

### 5.2 The RLHF Prosociality Floor

Both the upward drift in cooperation (13.0 vs. 7.5) and the reluctance to endorse punishment (14% vs. 85%) likely reflect the influence of reinforcement learning from human feedback (RLHF). During training, models learn to be helpful, harmless, and honest — creating a prosociality floor that inflates cooperative behavior and suppresses punitive responses. This bias is consistent with the agreeableness and openness drift observed in our personality validation and documented in prior work (Salecha et al., 2024).

### 5.3 Implications for LLM-Based Social Science

Our results suggest that LLM agents with validated personality traits can approximate — but do not perfectly replicate — human behavior in economic experiments. They capture qualitative patterns (regime sensitivity, targeted punishment, cooperation heterogeneity) while exhibiting quantitative biases (excess cooperation, punishment aversion). Researchers should document and account for these biases rather than treating LLM responses as ground truth.

### 5.4 Limitations

Several limitations should be noted. First, our experiment is single-shot rather than repeated, unlike the original study which examined behavior across multiple rounds with learning. Second, agents do not interact — each makes decisions independently, without observing or responding to actual group members' choices. Third, results are model-specific; different LLMs may exhibit different biases. Fourth, our sample size (N = 50 per condition) is smaller than the original study (N = 160). Finally, we used uncalibrated personality descriptions; post-hoc calibration could potentially reduce the prosociality bias.

## 6. Conclusion

We demonstrate that personality induction via BFI-2-Expanded descriptions is necessary and effective for generating human-like behavioral variance in LLM-based economic experiments. Default agents produce degenerate hyper-rational behavior; personality-endowed agents cooperate, respond to institutional incentives, and exhibit individual differences. However, systematic biases from RLHF training — particularly prosociality and punishment aversion — mean that LLM agents approximate but do not replicate human economic behavior. Future work should explore multi-round interactions, group dynamics, and cross-model comparisons to further characterize the boundary conditions of LLM-based behavioral economics.

## References

Aher, G. V., Arriaga, R. I., & Kalai, A. T. (2023). Using large language models to simulate multiple humans and replicate human subject studies. *Proceedings of ICML 2023*.

Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis*, 31(3), 337-351.

Donnellan, M. B., Oswald, F. L., Baird, B. M., & Lucas, R. E. (2006). The Mini-IPIP scales: Tiny-yet-effective measures of the Big Five factors of personality. *Psychological Assessment*, 18(2), 166-175.

Ertan, A., Page, T., & Putterman, L. (2009). Who to punish? Individual decisions and majority rule in mitigating the free rider problem. *European Economic Review*, 53(5), 495-511.

Gupta, A., Song, J. H., & Ananthakrishnan, U. N. (2024). Self-assessment tests are unreliable measures of LLM personality. *Proceedings of BlackboxNLP 2024*.

Horton, J. J. (2023). Large language models as simulated economic agents: What can we learn from Homo Silicus? *NBER Working Paper No. 31122*.

Huang, J., et al. (2024). Designing AI-agents with personalities: A psychometric approach. *arXiv:2410.19238*.

Jiang, H., et al. (2024). PersonaLLM: Investigating the ability of large language models to express personality traits. *Findings of NAACL 2024*.

Kozlowski, A. C., & Evans, J. A. (2025). Simulating subjects: The promise and peril of AI stand-ins. *Sociological Methods & Research*.

Mei, Q., et al. (2024). A Turing test of whether AI chatbots are behaviorally similar to humans. *Proceedings of the National Academy of Sciences*, 121(9).

Park, J. S., et al. (2024). Generative agent simulations of 1,000 people. *arXiv:2411.10109*.

Salecha, A., et al. (2024). Social desirability biases in large language models. *PNAS Nexus*, 3(12).

Serapio-Garcia, G., et al. (2024). Personality traits in large language models. *Nature Machine Intelligence*.

Soto, C. J., & John, O. P. (2017). The next Big Five Inventory (BFI-2): Developing and assessing a hierarchical model with 15 facets. *Journal of Personality and Social Psychology*, 113(1), 117-143.

Srivastava, S., John, O. P., Gosling, S. D., & Potter, J. (2003). Development of personality in early and middle adulthood: Set like plaster or persistent change? *Journal of Personality and Social Psychology*, 84(5), 1041-1053.
