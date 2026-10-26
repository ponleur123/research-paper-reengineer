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

## Development and tests

The project contains a portable `SKILL.md`, reference playbooks, templates, Python helper scripts and smoke tests. There is no runtime service or mandatory REA dependency.

```bash
python -m pip install numpy
python -m unittest discover -s tests -v
```

The bundled workflows include a GitHub Actions check that runs these tests on pushes and pull requests. Python standard-library scripts work without NumPy except array comparisons.

## Provenance and licensing

REA is a separate upstream project; this repository is not affiliated with or an official REA plugin. Check the upstream project's license and documentation before using its optional integrations. This skill does not redistribute REA source or compiled tools.