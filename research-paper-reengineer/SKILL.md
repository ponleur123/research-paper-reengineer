---
name: research-paper-reengineer
description: Evidence-driven reconstruction of machine-learning research papers into testable implementations. Use when asked to reverse engineer, reproduce, implement, audit, or extend a paper or method using PDFs, equations, figures, supplementary material, GitHub repositories, model checkpoints, datasets, or compiled artifacts. Integrates REA (Reverse Engineer Anything) only when shipped artifacts or runtime evidence require it; emphasizes architecture specifications, claim-evidence traceability, PyTorch shape contracts, and reproduction testing. Especially useful for multi-view vision, BEV, 3D reconstruction, detection, and tracking.
compatibility: Requires an agent able to read files and run Python. REA MCP/CLI is optional; PyTorch/NumPy and hardware are optional and needed only for implementation or numerical tests. Internet access may be needed to retrieve public papers or repositories.
metadata:
  version: "1.0.0"
  author: "Research Reconstruction Toolkit"
---

# Research Paper Reengineer

**Mission:** reconstruct the *scientific method* of a published work and validate a new implementation with explicit provenance. Do not mistake a plausible implementation for a verified reproduction. Treat original code as evidence rather than truth when it disagrees with the paper; report the discrepancy.

## Trigger and routing

Use for requests like "reverse engineer this paper", "recreate this BEV method", "infer missing implementation details", "implement this architecture in PyTorch", "compare paper and repo", or "reproduce reported results".

Choose the best available route, without installing tools unnecessarily:

| Evidence available | Path | Defensible outcome |
|---|---|---|
| Paper only | Paper/figures/equations + alternative hypotheses | Spec + prototype, **not** confirmed original implementation |
| Paper + source repository | Paper ↔ code ↔ config crosswalk | Source-grounded reconstruction + tests |
| Above + checkpoints | Add safe tensor/header inspections + module key/shape reconciliation | Stronger architecture/config attribution, not proof of training history |
| Packaged app/native binary/model artifact or runtime-only behavior | Use connected REA tools **where applicable** (see REA bridge) | Artifact-grounded findings + limitations |
| Dataset/eval available | Run comparable evaluation under controlled configuration | Reproduced metric, within documented tolerance if matched |

**Use REA conditionally:** For ordinary open-source Python/PyTorch repo analysis, inspect source with normal tools. REA is relevant to GGUF/safetensors metadata, shipped binaries, CUDA code objects, packaged applications, and warranted runtime investigations. REA's model-artifact inspector does **not** recover full network forward graphs, optimizer settings, or training data from tensor names alone. See [references/rea-bridge.md](references/rea-bridge.md).

## Operating rules

1. Work only with authorized accessible materials; respect code/model licenses and dataset restrictions. Never claim a result or execute untrusted model pickle code merely to inspect a checkpoint.
2. Capture exact sources: paper title/DOI/URL/version and page/figure/equation; repo URL and commit; config file/line; checkpoint name, digest when possible; dataset protocol and split. Record *negative evidence* and conflicts as carefully as positive evidence.
3. Classify claims: **observed** (direct artifact/source), **derived** (shown inference from observations), **hypothesis** (plausible but unverified), **contradicted**, or **unknown**. Do not transform assumptions into observations.
4. Distinguish **architecture parity**, **numerical parity**, and **benchmark reproducibility**. A unit test proving tensor shapes does not establish metric parity.
5. If only part of a paper can be reconstructed, deliver working partial results and name unresolved dependencies. Do not invent hidden implementation details or fabricated metrics.
6. Favor minimal, executable PyTorch modules and deterministic tests over writing a large speculative end-to-end system.
7. Never assert camera calibration is present/absent solely because a method uses BEV. Inspect actual projection operators and coordinate-frame contracts.

## Workflow

### Phase 0 — Scope and workspace

Identify the *target component* (e.g., multi-view feature aggregation), desired deliverable (analysis, prototype, reproduction), primary input artifacts, and compute/data constraints. Continue with explicit assumptions if something is missing; only ask if the missing input makes all useful work impossible.

Optionally scaffold a work area:

```bash
python scripts/init_case.py --title "Multi-view feature aggregation" --output ./recon/multiview-aggregation
```

The generator will not overwrite existing template files. Use the generated `case.json` and `evidence.csv` as living records; place source pointers in `sources/` instead of copying restricted materials.

### Phase 1 — Recover the scientific specification

Read the full methodology, figures, appendices, experiment settings, ablations, and supplementary materials. Extract:

- Inputs/outputs including axes, shapes, units, frames and sampling assumptions.
- Ordered modules and computational dependencies; equations and pseudocode.
- Losses, supervision, datasets/splits, preprocessing, augmentation, optimization, inference, postprocessing and metrics.
- Claims with page/figure/equation references, plus every omitted choice that affects outputs.

Build a table of **paper claim → evidence location → code counterpart → confidence → verification test**. Never infer operations from architecture diagrams alone when equations conflict. Follow [references/paper-protocol.md](references/paper-protocol.md).

### Phase 2 — Repository and artifact crosswalk

If source exists, locate entrypoints, config files, constructors, `forward` calls, registry lookup, transforms, CUDA extensions, dataloaders, loss functions, NMS/decoding, and evaluation code. Pin a commit before citing line numbers. Inspect actual code; don't use only README summaries. Draw a module-level DAG and produce `architecture-spec.md` with a per-stage contract:

`stage | input shape+frame | operation/equation | output shape+frame | parameters | evidence | open questions`.

When artifacts exist, inspect *headers first* and cross-reference parameter names/shapes. For `.safetensors`, use REA's model inspection (if connected) or the bundled safe header inspector:

```bash
python scripts/inspect_safetensors.py /path/to/model.safetensors --limit 100 --output tensors.json
```

For `.pt`/`.pth`/`.ckpt` files, do **not** run unrestricted pickle deserialization. If trusted and appropriate, use PyTorch `torch.load(..., weights_only=True, map_location='cpu')` and interpret reported limitations; checkpoints are often framework-specific. Run code only with user authorization and a suitable sandbox. For native or packaged artifacts, see REA bridge.

### Phase 3 — Resolve unknowns by minimal experiments

For each unresolved decision, write competing hypotheses and a **discriminating test**. Examples: sum vs concatenate features, mean vs attention, positional encoding placement, 3D→2D vs 2D→BEV projection, known vs learned calibration, temporal alignment order.

Record outcome and what it establishes; explicitly preserve uncertainty when available evidence cannot distinguish hypotheses. For BEV or multi-camera papers use [references/multiview-3d.md](references/multiview-3d.md).

### Phase 4 — Implement a testable model

Create modules incrementally. For every block, specify dtype/device, channel layout, tensor shape, coordinate convention, valid numerical range, and masks. Encode these as assertions/tests. A recommended implementation order:

1. Typed input/target contracts and deterministic fixtures.
2. Geometry/projections or tokenization/feature preparation.
3. Core aggregation module.
4. Decoder/heads and postprocessing.
5. Training and evaluation orchestration only when essential dependencies are verified.

**Do not silently substitute** an easier algorithm: label replacement as a deviation and explain its expected effect. If the reference contains unavailable ops, expose a documented fallback and comparison test.

### Phase 5 — Verification gates

Use [references/verification.md](references/verification.md) for the checklist and thresholds. Minimum gates:

- **G0 Source integrity:** exact source versions, licenses, and checkpoint identity documented.
- **G1 Structural:** module graph, parameters, key names and tensor shapes coherent.
- **G2 Mathematical:** toy analytical cases; dimensions, coordinate transforms and invariants pass.
- **G3 Numerical:** reference implementation or known intermediate output agrees within stated tolerance, if available.
- **G4 Experimental:** reproduced training/evaluation under matched data, splits, seeds, hardware-relevant numerics, and metric protocol, if possible.

Call success at *the highest gate actually passed*. Missing reference code or data means G3/G4 might be untestable, not automatically failed.

For paired `.npy` or `.npz` reference outputs, if NumPy is available:

```bash
python scripts/compare_arrays.py reference.npz candidate.npz --atol 1e-5 --rtol 1e-4
```

For evidence completeness:

```bash
python scripts/audit_evidence.py ./recon/multiview-aggregation/evidence.csv
```

### Phase 6 — Report and handoff

Complete `reconstruction-report.md` plus architecture spec, evidence CSV, runnable code, tests, environment/dependencies, and an experiment log. **Always** include:

1. Reconstructed pipeline with equations and parameterization.
2. Evidence table with paper locators and corresponding source/artifact locators.
3. Decisions, alternatives, mismatches, and unresolved assumptions.
4. Reproduction status by G0–G4 and actual test command + observed result.
5. Minimal next tests ranked by information gained and implementation cost.

Never say "exact replication" merely because it runs. If only paper-derived, report "provisional reconstruction". If training metrics are unmatched or unavailable, report "experimental reproduction not verified".

## Suggested activation prompt

> Use `research-paper-reengineer` to reconstruct the multi-view feature aggregation block in this paper. Cross-check paper, supplementary, repository and checkpoint if available. Create an evidence matrix, architecture spec, a minimal PyTorch implementation, geometry/shape tests, and a report separating verified behavior from assumptions. Use REA only if shipped model/binary artifacts require it.

## File map

- [references/paper-protocol.md](references/paper-protocol.md): extraction and provenance protocol.
- [references/rea-bridge.md](references/rea-bridge.md): conditional REA invocation and limitations.
- [references/multiview-3d.md](references/multiview-3d.md): camera geometry, BEV, fusion and tracking validation.
- [references/verification.md](references/verification.md): parity gates, numeric rigor, experiment protocol.
- `assets/`: case, evidence, architecture, test, and report templates.
- `scripts/`: scaffold, safetensors header inspection, array comparison, evidence auditing.
