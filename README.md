# Quality Record Bench

A small independent benchmark for evidence-based quality-document review by AI systems. It is an original portfolio project by Kalif Shear.

A reviewer reads fictional records, decides whether to return the package for correction, and identifies each defect with a specific supporting record. Cases cover batch-record version and reviewer independence, QC summary reconciliation, and deviation closure evidence. QA practice inspired the setting. All rules and records were created for this benchmark. The work evaluates documentary reasoning and does not involve biological procedures or real release decisions.

## Quick start

Requires Python 3.10+ and Docker. Use a fresh destination for each run.

```sh
python3 -m unittest discover -s tests -v
python3 -m qrb.generate --seed 34 --solver runs/demo/solver --key runs/demo/author/key.json
docker build --target solver -t quality-record-bench:solver .
docker build --target verifier -t quality-record-bench:verifier .
./run-container.sh show runs/demo
```

The evidence ends up in `runs/demo/solver/cases.json`, with the rules and format in `runs/demo/solver/instructions.txt`. Give only those two files to the system being evaluated. Save its JSON output to `runs/demo/submission.json`, then run:

```sh
./run-container.sh grade runs/demo
```

Seed 34 is a public practice seed. For an evaluation, choose an undisclosed seed, generate a fresh case set, and keep the key outside solver assets. Use the case-set digest in the scoring output to identify the run. The public reference and generator support independent inspection. An evaluator must use an isolated execution environment and never give an evaluated system access to the source repository, grading key, validator container, or holdout results.

## What is scored

A case earns one exact match when the decision and complete set of defect-code and evidence-ID pairs agree with the reference. Finding order does not matter. A matching decision by itself contributes only to the separate decision metric. Unsupported guesses or off-subject citations lose exact credit. Omitted cases earn zero, and invalid submissions are reported as invalid. The scorer interprets response data as JSON.

See [the technical report](REPORT.md) for the design, comparisons, pilot protocol, and limitations.
