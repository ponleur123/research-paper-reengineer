# Research Paper Reengineer — Agent Skill

A portable Agent Skills-format extension for reproducing/reconstructing ML and computer-vision papers. It **complements**, rather than replaces, the separate [REA](https://github.com/morluto/rea) skill.

## Install

Copy the **entire** `research-paper-reengineer` directory to your project:

```bash
mkdir -p .agents/skills
cp -R research-paper-reengineer .agents/skills/
```

Or extract the downloadable archive from its parent directory:

```bash
unzip research-paper-reengineer.zip -d .agents/skills/
```

Restart/reload the coding agent if required. Use in an Antigravity workspace or another client following the Agent Skills directory convention. Installing this skill **does not install/configure REA**; it works without REA for paper + source work. For artifact inspection via REA, separately follow the official REA setup and review any permission or configuration changes.

## v1.1 — operating modes and short prompts

The installed skill now understands five modes. You only have to supply a paper reference and a mode, not a full reproduction protocol.

| Mode | Result |
|---|---|
| `analyze` | Extract architecture, equations, evidence and unknowns |
| `reconstruct` | Independently implement specified model/module and run tests |
| `reproduce` | Implement full trainable model, use real data, train/evaluate and compare to paper |
| `blind-reproduce` | Same as reproduce but *paper only*: do not inspect any original/third-party implementation or pretrained weights before final results are frozen |
| `audit` | Independent code/results review, new tests and fault-injection tests |

**Two-line paper-only experiment:**

```text
Use research-paper-reengineer in blind-reproduce mode.
Paper: https://arxiv.org/abs/1608.06037
```

**Full reproduction allowing author code comparison:**

```text
Use research-paper-reengineer in reproduce mode.
Paper: <paper URL or PDF>
```

For a narrower job: `Use research-paper-reengineer in reconstruct mode. Paper: <URL>. Focus on spatial cross-attention.`

`reproduce` and `blind-reproduce` require runnable model, dataset loader, train, validate, checkpoint/resume, evaluate and inference paths; verification should execute a real-data smoke test whenever accessible. Complete benchmark training/evaluation may be blocked by compute or dataset availability; the skill must report partial execution truthfully. Benchmark similarity alone does not prove source/architecture equivalence. No framework-independent guarantee of numerical parity is implied.

Full requirements and safeguards: [references/reproduction.md](references/reproduction.md).

## Example prompt

> Use the research-paper-reengineer skill to reverse-engineer the multi-view feature aggregation module from this paper. First extract equations and architecture, then compare the repository and checkpoint if available, generate a minimal PyTorch implementation with shape/projection tests, and report evidence-backed vs inferred decisions. Integrate REA only where compiled/model artifact inspection is required.

## Included tools

- `scripts/init_case.py`: non-destructive research-case scaffolding.
- `scripts/inspect_safetensors.py`: static header/tensor inventory; never loads model code.
- `scripts/audit_evidence.py`: verifies evidence CSV structure.
- `scripts/compare_arrays.py`: shape-aware `.npy`/`.npz` comparison with tolerances (requires NumPy).

## Limitations

This is an **agent workflow skill** and helper scripts, not an autonomous model-replication guarantee or a substitute for access to code, checkpoints, data and hardware. The scripts do not implement a paper's neural network automatically; the coding agent derives and writes the implementation from evidence.

## Upstream specifications

- Agent Skills spec: https://agentskills.io/specification
- REA original project: https://github.com/morluto/rea

## Tests

Run locally with `python -m pip install numpy && python -m unittest discover -s tests -v`. GitHub Actions runs these helper and mode-contract tests on push and pull requests. They test the **skill package**, not scientific correctness of any newly generated paper reproduction; independent benchmarks must be assessed separately.
