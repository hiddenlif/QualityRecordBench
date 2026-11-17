# Quality Record Bench pilot report

Kalif Shear • November 17, 2026

## Research question

Can a model reconstruct a quality-document decision from the governing record and cite the evidence for each exception? In this benchmark, a document can contain plausible but irrelevant rows, and a correct disposition can hide incompletely supported findings. The evaluator therefore reports disposition agreement and exact evidence-backed completion separately.

## Design

The generator creates 12 cases per seed. Each workflow has a clean control, one case for each of its two defects alone, and one case with both defects. Batch-record cases compare performed revisions and reviewer identities. QC summaries reconcile active document tally counts and verify source lineage. Deviation packages check required-action completion and closure ordering. Case and evidence IDs vary by seed. Active records, void rows, optional actions and off-subject records serve as distractors. The independent reference recomputes findings from visible inputs rather than reading generator labels.

The scoring process uses only an external key and the response JSON. Runtime Docker targets separate solver assets from the verifier. Both commands use read-only mounts, a non-root user and no container network. The original application-domain inspiration is data reliability and traceability. The task rules are benchmark-specific. [FDA data integrity guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers)

## Controls

| Control | Observed or expected diagnostic |
|---|---|
| Independent reference on 30 seeds | 360/360 exact cases |
| No work | 0/12 exact |
| Always hold, no findings | 9/12 correct dispositions, 0/12 exact |
| Always ready, no findings | 3/12 exact, all clean controls |
| Correct disposition with one decoy evidence ID | 12/12 dispositions, 11/12 exact |
| Extra unsupported finding in one otherwise correct review | 11/12 exact |
| Any one of three single-fact flips applied to a clean fixture | Changes the decision to HOLD and cites the changed record |
| Reordered submission and findings | 12/12 exact |
| Duplicate case IDs, duplicate finding pairs or JSON keys | Rejected as invalid |

## Pilot protocol

The pilot sends the same generated pack to each tested model as one closed-book prompt. The models receive the policy and record evidence only, with no grading key. The verifier scores emitted JSON afterward. It is a one-pass document-reasoning test, so it does not measure tool-use trajectories or performance over repeated independent runs. The test pack is kept separate from the public practice seed.

## Pilot results

| Model | Exact cases | Correct dispositions |
|---|---:|---:|
| Claude Opus 5.5 | 12/12 | 12/12 |
| Claude Sonnet 5.5 | 12/12 | 12/12 |
| GPT-6.1 Sol | 12/12 | 12/12 |

The private pilot pack and shared prompt are identified by SHA-256 digests in [pilot-results.json](pilot-results.json). Claude Code reported the resolved Opus and Sonnet versions. GPT-6.1 Sol was explicitly selected. Claude used one turn per run with tools disabled. The scored Codex trace records no tool calls. The candidate response did not receive verifier feedback before scoring. All three reached the ceiling. The useful measured result is that this first case mix did not separate the systems. The negative controls establish only that the grader rejected those tested incorrect responses.

## Limits

Twelve cases and six designed rule types are useful for checking the scoring contract and identifying issues in a pilot. They do not support a production QA claim, a frontier leaderboard, or a reliable estimate of differences between models. Important next comparisons are one-case-at-a-time evaluation, repeated samples, independent human review, and more document layouts and defect families. This release does not include client data, work for an employer, or any real decision or procedure.
