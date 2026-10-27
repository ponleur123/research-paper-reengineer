# Reproduction and operating-mode protocol (v1.1)

This reference applies when `SKILL.md` selects `reproduce` or `blind-reproduce`. Its requirements supersede source-code crosswalk steps when the selected mode forbids access to original implementations.

## Source-access policy

| Source | `reproduce` | `blind-reproduce` |
|---|---|---|
| Target paper, figures, appendix, author-supplied supplemental scientific text | Allowed | Allowed |
| Dataset from its official distribution | Allowed | Allowed |
| Framework, hardware and general mathematical documentation | Allowed | Allowed |
| Original author's repository, checkpoints, training scripts and configuration | Allowed when licensed | **Prohibited** until the blind result is frozen |
| Third-party implementations, weights and paper-specific reproduction tutorials | May compare with provenance | **Prohibited** |
| REA inspection of original compiled/model artifacts | Only when justified | **Prohibited** |
| Background cited scientific literature | Allowed; distinguish from target-paper evidence | Allowed for background only; document influence |

When a request explicitly asks for paper-only reconstruction, use `blind-reproduce` even if the original GitHub repository happens to exist. Do not search for implementation-specific sources merely to see whether they exist. Record excluded source categories in the manifest. After final outputs are frozen, an **optional separate unblinded audit** may compare against hidden original sources; do not feed its findings back into the blind reproduction.

## 1. Establish a locked research target

- Pin the target paper version and identify the exact task, model variant, dataset release, split, and metric.
- Build a claim–evidence table. Each material layer/training choice must be **observed**, **derived**, **hypothesis**, **contradicted**, or **unknown**, with a paper locator where available.
- Parse benchmark results into an exact target: model variant, evaluation protocol, top-1/error/AUROC/etc., and whether metrics are single run or aggregated.
- Freeze a `reproduction-plan.md` before the final test evaluation; include a deviation register and a compute budget.
- Never infer a missing optimizer, augmentation, kernel/padding convention, or training schedule from the paper's final metric alone.

## 2. Three execution stages (distinct statuses)

### A. Architecture and functional tests

Implement the model with explicit shape contracts and unit tests for module order, trainable parameters, gradients, shape/layout/dtype, and device behavior. Where original source is excluded, validate analytical identities and paper-stated characteristics; do not claim original-source or original-weight parity.

### B. Real-data training smoke test

Use actual dataset records obtained legally, not random or synthetic substitutes. Run at least one forward/backward/optimizer step, demonstrate nonzero parameter updates, save and restore a checkpoint, and evaluate on a validation batch. Log observed loss, sample counts, seed, hardware, time and exact commands. A passed smoke test proves the pipeline trains; it does **not** establish learning/convergence or benchmark reproduction.

### C. Full experimental reproduction

Use the training and evaluation protocol documented in the paper when recoverable. If development needs a validation subset not specified by the authors, mark this as an adaptation. Use development training/validation subsets for all architecture decisions and hyperparameter search. Lock configuration **before** final held-out test evaluation. When prescribed by the protocol, train a final fresh model on the full original training partition after development; do not silently use test labels or test accuracy for selection. Repeat predeclared seeds where feasible; report each run and distribution, not best-of-many cherry-picking. Calculate the metric with its exact direction, units, preprocessing and evaluation code.

**Do not claim full reproduction** if full training, final testing or comparable evaluation was not actually executed. Partial execution must remain a documented partial result with a runnable continuation/resume path.

## 3. Runnable project contract

Prefer an executable project with the following functionality (exact filenames can vary):

```text
src/model.py                   independent model implementation
src/dataset.py                 official dataset and transformations
src/train.py                   train/validate/checkpoint/resume
src/evaluate.py                one-time test evaluation
src/predict.py                 checkpoint-based inference
configs/smoke.yaml             inexpensive actual-data sanity run
configs/development.yaml       validation and hypothesis selection
configs/reproduction.yaml      locked final training/evaluation
tests/                         mathematical, structural and pipeline tests
experiments/                   executed run logs/config hashes
checkpoints/                   local artifacts; do not commit large weights
reproduction-plan.md           decisions, budget, baseline and target
reconstruction-report.md       observed facts and G0–G4 status
```

The README must give executable installation, dataset, smoke-test, resume, full training, test evaluation and inference commands. **Execute and verify commands** as far as the available environment permits; if unavailable, label them unverified. Avoid silent downloads of restricted material. A smoke mode must use actual examples when data is accessible; synthetic fixtures are permitted only for mathematical/shape tests.

## 4. Evidence, metrics and failure diagnostics

Capture:
- Dataset identity/license, exact numbers of training/validation/test examples, preprocess/augmentation and split provenance.
- Model graph/parameter count, initialization, loss, optimizer, scheduler, epochs/steps, global and worker seeds, batch size and precision/device.
- Versioned dependencies, training and evaluation commands, actual exit status and logs, run hashes/checkpoint locations.
- Learning curves, finite-gradient/parameter-update checks, evaluation metric and uncertainty from independent seeds when possible.
- Paper's reported metric **separately** from observed metric; report signed and absolute differences in percentage points for accuracy/error.
- Deviations categorized by source: missing specification, hardware budget, dataset version, evaluation convention or intentional safety/compatibility choice.

Diagnose failures in order: invalid sources/splits → dimensions/implementation → data preprocessing/augmentation → loss/optimizer → initialization/scheduler → numerical behavior → evaluation code → training dynamics. Do not tune against the final test partition.

## 5. Gates and acceptance

- **G0**: paper version, sources, dataset identity/licensing and inspected artifacts pinned.
- **G1**: model graph and shapes supported; paper-only architecture claims appropriately qualified.
- **G2**: operation/gradient and real-data smoke tests passed as applicable.
- **G3**: numerical parity only where a genuinely independent numerical oracle exists; **no original-reference parity is available in blind mode** without permitted author outputs.
- **G4**: real training + comparable evaluation actually executed, with deviations and uncertainty recorded. A G4 run may have **failed** to match the paper's target; report benchmark discrepancy separately from whether it executed.

For each gate state `passed`, `failed`, `blocked`, or `not tested` with observed supporting artifacts. Separately score **architecture fidelity**, **pipeline functionality**, **numerical parity**, and **benchmark comparability**. A similar score never proves architectural equivalence.

## 6. Insufficient resources

If data cannot be legally accessed or compute/time is insufficient, deliver all possible runnable files and partial smoke logs, plus an exact continuation command. Do not run background tasks without a scheduler, fabricate a checkpoint, invent future scores, or label G4 passed. Never promise that complete training will happen later automatically.
