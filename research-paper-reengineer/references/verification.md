# Reproduction verification and report gates

## Evidence-level quality ladder

- **G0 source integrity:** stable paper version, source commit, artifact identity and permissions documented.
- **G1 structural:** forward DAG and modules traced; representative parameter and tensor shapes validated; missing layers identified.
- **G2 mathematical:** unit tests on known small inputs, equivalence of formulas/implementations, mask/boundary checks, gradients where needed.
- **G3 numerical:** reference intermediate/output parity with defined `atol/rtol`; both paths use aligned preprocessing, parameters and numerical precision.
- **G4 benchmark:** matched data, evaluation protocol and preprocessing; actual run measured and reported, including deviations, multiple seeds and confidence/variation as feasible.

Gates are **not automatic**: explain what was tested and mark each `passed`, `failed`, `not tested` or `blocked`.

## Standard tests

- Deterministic seed and precision log, fixed input fixture and device info.
- Tensor rank/layout/contiguity, finite outputs, empty or all-masked cases, device/dtype support.
- Gradient existence and finite norm for trainable paths; numerical gradient spot-check for custom ops.
- Batch-size and variable-view robustness; avoid accidental behavior tied to a fixed number of cameras.
- Invariant tests: rigid transform round trip, projection agreement, permutation invariance *only if formulation intends it*.
- Numerical tests on equivalent intermediates, not just final predictions. Compare exact keys/shape and per-tensor `max_abs`, `mean_abs` and pass fraction.
- Data leakage safeguards: training/validation split integrity, no accidental reuse of test data in calibration/hyperparameter selection.

## Experimental reproduction

Document hardware, framework/dependency versions, commit+checkpoint hashes, dataset release/split and annotation versions, input resolution/augmentation, optimizer/scheduler, losses, mixed-precision settings, iterations/epochs, seed(s), evaluation command and metric implementation. Separate the original paper's reported values from **your** observed values; a number taken from the paper is not a reproduced result.

Suggested tolerance policies:

- Functional unit tests: absolute+relative tolerances based on operation/dtype and expected conditioning (not a universal hard-coded threshold).
- Benchmarks: predeclare metric acceptance criterion and report variability; don't retroactively relax targets.

## Failure triage

Order of diagnosis: source/version mismatch → input and preprocessing → coordinate transforms/masks → config/shape mismatch → checkpoint loading → numerical precision → postprocessing → evaluation protocol → training dynamics. An architecture diagram can be correct while its reported benchmark remains unreproduced.

## Deliverable standard

A useful handoff includes: diagram or DAG; module-by-module specification; claim-evidence CSV; runnable source; test commands/results; error/deviation log; reproduction gate summary; unresolved decision register. State what is **supported**, **inferred**, **untestable with provided material**, and **contradicted**.
