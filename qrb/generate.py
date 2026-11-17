"""Generate original evidence and an author-only label manifest in separate files."""
import argparse
import hashlib
import json
from pathlib import Path
from random import Random

from .protocol import POLICY


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_pack(seed):
    rng = Random(seed)
    cases, labels = [], []
    for workflow in ("BATCH_RECORD", "QC_SUMMARY", "DEVIATION_PACKAGE"):
        clean_and_flips = [(False, False), (True, False), (False, True), (True, True)]
        for flag1, flag2 in clean_and_flips:
            case_id = f"C-{rng.getrandbits(40):010x}"
            subject = f"R-{rng.getrandbits(28):07x}"
            decoy = f"R-{rng.getrandbits(28):07x}"
            index = {"subject_id": subject}
            rows, findings = [], []

            def row(kind, entity, **values):
                evidence_id = f"E-{rng.getrandbits(36):09x}"
                rows.append(dict(evidence_id=evidence_id, kind=kind, entity=entity, **values))
                return evidence_id

            def defect(flag, code, evidence_id):
                if flag:
                    findings.append(dict(code=code, evidence_id=evidence_id))

            if workflow == "BATCH_RECORD":
                active = f"r{rng.randrange(3, 9)}"
                older = f"r{int(active[1:]) - 1}"
                index["active_revision"] = active
                defect(flag1, "BATCH_REVISION",
                       row("execution", subject, executed_revision=older if flag1 else active))
                preparer, alternate = rng.sample(["P17", "P31", "P49", "P62"], 2)
                defect(flag2, "BATCH_REVIEWER",
                       row("review", subject, preparer=preparer,
                           reviewer=preparer if flag2 else alternate))
                row("execution", decoy, executed_revision=older)
                row("review", decoy, preparer=alternate, reviewer=alternate)
            elif workflow == "QC_SUMMARY":
                current = f"x{rng.randrange(3, 8)}"
                previous = f"x{int(current[1:]) - 1}"
                index["current_source_revision"] = current
                counts = rng.sample(range(3, 17), 3)
                for count in counts:
                    row("tally", subject, count=count, state="active")
                row("tally", subject, count=rng.randrange(1, 6), state="void")
                row("tally", decoy, count=rng.randrange(5, 20), state="active")
                summary = row("summary", subject,
                              source_revision=previous if flag1 else current,
                              count=sum(counts) + (rng.choice([-2, 2, 3]) if flag2 else 0))
                defect(flag1, "QC_SOURCE_REVISION", summary)
                defect(flag2, "QC_COUNT", summary)
            else:
                date = f"2026-10-{rng.randrange(11, 25):02d}"
                row("action", subject, required=True, status="CLOSED",
                    closed_at=f"{date}T12:30:00Z" if flag2 else f"{date}T09:30:00Z")
                action = row("action", subject, required=True, status="OPEN" if flag1 else "CLOSED",
                             closed_at=None if flag1 else f"{date}T09:45:00Z")
                row("action", subject, required=False, status="OPEN", closed_at=None)
                row("action", decoy, required=True, status="OPEN", closed_at=None)
                closure = row("closure", subject, closed_at=f"{date}T11:00:00Z")
                defect(flag1, "DEV_OPEN_ACTION", action)
                defect(flag2, "DEV_EARLY_CLOSURE", closure)
            rng.shuffle(rows)
            cases.append(dict(case_id=case_id, workflow=workflow, index=index, evidence=rows))
            labels.append(dict(case_id=case_id, workflow=workflow,
                               decision="HOLD" if findings else "READY", findings=findings))
    rng.shuffle(cases)
    rng.shuffle(labels)
    return cases, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    a = parser.parse_args()
    if a.key.resolve().is_relative_to(a.solver.resolve()):
        parser.error("The grading key must be outside the solver directory.")
    if a.key.exists():
        parser.error("Use a new grading-key path.")
    a.solver.mkdir(parents=True, exist_ok=False)
    a.key.parent.mkdir(parents=True, exist_ok=True)
    cases, labels = make_pack(a.seed)
    (a.solver / "instructions.txt").write_text(POLICY, encoding="utf-8")
    dump(a.solver / "cases.json", {"cases": cases})
    digest = hashlib.sha256((a.solver / "cases.json").read_bytes()).hexdigest()
    dump(a.key, {"case_set_sha256": digest, "reviews": labels})


if __name__ == "__main__":
    main()
