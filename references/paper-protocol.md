# Paper-to-implementation extraction protocol

## Source inventory

Capture primary paper exact title, year, version (arXiv version or published DOI), URL, retrieved date, PDF page numbering convention; appendices, supplement, source repository pinned commit, issues/PRs relevant to discrepancies, released checkpoints, benchmark/evaluation definitions and datasets. Distinguish an author's claim from an independent observation. If you cannot access a referenced document, mark it not inspected.

## Read order

1. Abstract and high-level claim (for scope, not implementation evidence).
2. Method overview + figure legend and algorithm boxes.
3. Each mathematical definition, with all variable definitions and dimensionality.
4. Appendix and supplementary implementation details.
5. Experiments: dataset version, splits, labels, sample sizes, preprocessing, training duration, optimizer, LR schedule, augmentations, model selection and loss weights.
6. Ablations: identify what was measured versus what was argued, and which variants correspond to the released checkpoint.
7. Repository and configuration crosswalk if available.

## Equation inventory

For each equation: ID, exact mathematical relationship, variable semantics, shape/unit/frame, assumptions, location, mapped method/function, and a toy verification case. Clarify conventions for softmax axis, aggregation normalization, attention dimensions and interpolation alignment.

## Claim-evidence matrix

In the case's `evidence.csv`, maintain each nontrivial claim and its strongest evidence. Fields:

- `claim_id`: unique stable ID (`C001`).
- `claim`: one falsifiable assertion.
- `source_kind`: `paper`, `supplement`, `code`, `config`, `checkpoint`, `REA`, `experiment`, etc.
- `source_locator`: e.g. "paper v2 p.5 Eq.4" or "repo commit abc123 path/file.py:120-140"; URLs plus line/page info.
- `artifact_path`: local file path of evidence where useful.
- `evidence`: direct quote **briefly** or careful numeric/code summary. Never invent content.
- `status`: `observed`, `derived`, `hypothesis`, `contradicted`, `unknown`.
- `test_id`: corresponding test or discriminating experiment ID.
- `notes`: caveats, conflicts, linked claim IDs, alternatives.

Use `audit_evidence.py` to catch structural omissions, **not** to prove scientific correctness.

## Ambiguity register

Every gap affecting reproducibility needs:

| Unknown | Options | Consequence | Minimal discriminating test | Evidence needed |
|---|---|---|---|---|
| Fusion operator | sum / concatenation / attention | channels, memory, attribution | examine forward or compare checkpoint projections | source or intermediate activations |

Prioritize choices that alter mathematical semantics, not minor packaging conventions.

## Recovered-spec rule

A complete block specification includes input shape, output shape, tensor order, units/frames, forward equation, parameter initialization, masks/boundaries, train/eval behavior, numerical precision, evidence and unresolved decisions. If one of these is unavailable, mark it explicitly unknown.
