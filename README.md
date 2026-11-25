# Separation of Duties for Multi-Agent LLM Systems: code and data

This repository contains the code, the simulated environment, the policies, the prompts and the
results of the paper *Separation of Duties for Multi-Agent LLM Systems: Model, Enforcement and
Evaluation in Critical Infrastructures* (V. Bellandi, submitted to IEEE Transactions on Dependable
and Secure Computing). It does not contain the paper.

| Path | Content |
|---|---|
| `sodrm/` | Reference monitor **SoD-RM**: formal model (principals, delegations, events, provenance labels), **AgentSoD** parser and coverage checks, decision procedure, hash-chained ledger, and a from-scratch reference oracle used to test the monitor |
| `policies/energy_ops.sod` | The policy listing of the paper |
| `gridops/` | **GridOps-SoD**, the simulated energy operator: power flow on the MV Oberrhein network of pandapower, four workflows with truthful check tools, 28 agents, attacks A1-A6, baselines B0-B4, the enforcement proxy, scripted agents and LLM agents for any OpenAI-compatible endpoint |
| `bench/` | Stage 1 benchmark (`run.py`), scripted runs (`stage2.py`), LLM runs (`stage2_llm.py`), long-horizon pairing with LLM agents (`a5_llm.py`), cost estimate (`estimate_cost.py`) |
| `analysis/` | Metrics and tests reported in the paper (`analyze_llm.py`, `analyze_a5.py`) |
| `config/` | Model endpoints: local Ollama or hosted providers (keys are read only from environment variables) |
| `tests/` | 50 tests: monitor against the definitions and the oracle, and the environment |
| `results/` | All results reported in the paper (see below) |
| `run_mac.sh` | Every run on a Mac with Ollama, or on hosted providers |

## Requirements

Python 3.10 or later. `pip install pandapower pytest matplotlib`. LLM runs need either
[Ollama](https://ollama.com) with `gpt-oss:20b`, `qwen2.5:7b` and `mistral-small3.2:24b`
(`./run_mac.sh setup` installs a virtual environment and pulls them) or API keys for the
providers in `config/`.

```bash
python -m pytest -q tests      # 50 tests, about 10 s
```

## Results and how to reproduce them

| Paper | Results | Reproduce | Recompute the figures |
|---|---|---|---|
| Stage 1: agreement with the oracle, decision latency | `results/summary.json`, `results/latency_*.csv` | `python bench/run.py` (about 1 min) | written by the same command |
| Scripted agents (table and A5 figure) | `results/stage2/` | `python bench/stage2.py` (about 1 min) | written by the same command |
| LLM agents (main table, per-attack table, silent violations, level 3) | `results/stage2_llm_combined/` | see below | `python analysis/analyze_llm.py results/stage2_llm_combined` |
| Long-horizon pairing with LLM agents | `results/a5_llm_local_v2/` | `./run_mac.sh a5` | `python analysis/analyze_a5.py` |

**LLM runs.** Three seeds, 198 tasks per seed and configuration, models served by Ollama on
one Apple Silicon workstation (64 GB), temperature 0.2, at most eight turns per step.
`results/stage2_llm_combined/` merges two runs: B0, B1 and B2 from
`results/stage2_llm_local/`, and L2 and L3 from `results/stage2_llm_local_v2/`. The L2 and L3
rows in `results/stage2_llm_local/` come from an earlier version of the level-2 check (earlier
conflicting event only, without the other contributions of the earlier actor) and are kept only
for the record; they are not used in the paper. To repeat:

```bash
./run_mac.sh setup
CONFIGS=B0,B1,B2 OUT=results/stage2_llm_local ./run_mac.sh run      # about 3 h per run, 2 in parallel
CONFIGS=L2,L3 OUT=results/stage2_llm_local_v2 ./run_mac.sh run
OUT=results/stage2_llm_local_v2 ./run_mac.sh status
```

Runs are resumable: an interrupted run restarts from the missing (configuration, seed) pairs.

**Long-horizon pairing.** Four seeds per configuration, 30 episodes each, the same sequence of
work orders for L2 (fixed pair) and L3 (rotation with kappa = 10, H = 50). An agent that ends
its step by stating a decision in text without calling the tool that records it receives one
reminder (`--nudge 1`, the default of `./run_mac.sh a5`). `results/a5_llm_local/` is a first run
without the reminder, in which the model on M3 left about three quarters of its reviews
undecided; the paper reports the second run.

**Larger models.** `config/providers.large.json` and `./run_mac.sh cloud-smoke | cloud | a5-cloud`
repeat the LLM experiments with gpt-oss-120b, Qwen2.5-72B and Llama-3.3-70B on hosted providers;
`python bench/estimate_cost.py --providers config/providers.large.json` estimates cost and time
before spending.

## Logs

Each LLM run writes `rows.jsonl` (one row per task or episode), `decisions.jsonl` (every decision
of the monitor with the context it saw) and `turns.jsonl` (every model turn with model, provider,
token usage, latency, content and tool calls). The `turns.jsonl` files are large and are attached
to the releases of this repository.

## Scope of the prototype

The prototype implements the decision core, the parser, the ledger, the coverage checks and the
denial of unbound protected tools. The static SoD and satisfiability checks, credential isolation
and the isolation of agent runtimes are part of the design; in GridOps-SoD agents reach tools and
each other only through the proxy, but the monitor has not been tested with a production agent
runtime. Attacker-controlled agents (the A4 initiator and the A3a sub-agent) are scripted in every
configuration.

## License

MIT, see `LICENSE`.
