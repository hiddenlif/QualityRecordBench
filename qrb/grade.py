"""Score documentary decisions and evidence against a separately supplied key."""
import argparse
import json
from pathlib import Path

MAX_SUBMISSION_BYTES = 256 * 1024


class InvalidSubmission(ValueError):
    """The file violates the published response contract."""


def unique_object(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise InvalidSubmission(f"duplicate JSON key {key!r}")
        data[key] = value
    return data


def read_submission(path):
    with path.open("rb") as f:
        raw = f.read(MAX_SUBMISSION_BYTES + 1)
    if len(raw) > MAX_SUBMISSION_BYTES:
        raise InvalidSubmission("submission exceeds size limit")
    try:
        return json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, RecursionError) as e:
        raise InvalidSubmission(str(e)) from e


def findings(value):
    if not isinstance(value, list) or len(value) > 64:
        raise InvalidSubmission("invalid findings list")
    keys = set()
    for item in value:
        if (not isinstance(item, dict) or set(item) != {"code", "evidence_id"}
                or not all(isinstance(v, str) for v in item.values())):
            raise InvalidSubmission("invalid finding")
        key = (item["code"], item["evidence_id"])
        if key in keys:
            raise InvalidSubmission("duplicate finding")
        keys.add(key)
    return keys


def score(expected, candidate):
    if not isinstance(candidate, dict) or set(candidate) != {"reviews"}:
        raise InvalidSubmission("expected a reviews object")
    reviews = candidate["reviews"]
    gold = {r["case_id"]: r for r in expected["reviews"]}
    if not isinstance(reviews, list) or len(reviews) > len(gold):
        raise InvalidSubmission("invalid reviews list")
    found = {}
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {"case_id", "decision", "findings"}:
            raise InvalidSubmission("invalid review fields")
        identifier = review["case_id"]
        if not isinstance(identifier, str) or identifier not in gold or identifier in found:
            raise InvalidSubmission("unknown or duplicate case ID")
        if review["decision"] not in ("READY", "HOLD"):
            raise InvalidSubmission("invalid decision")
        found[identifier] = (review["decision"], findings(review["findings"]))
    details = []
    for identifier, item in sorted(gold.items()):
        target = (item["decision"], findings(item["findings"]))
        prediction = found.get(identifier)
        match = prediction == target
        details.append(dict(case_id=identifier, workflow=item["workflow"],
                            exact_match=match,
                            decision_match=prediction is not None and prediction[0] == target[0],
                            submitted=prediction is not None))
    total = len(details)
    return dict(case_set_sha256=expected["case_set_sha256"], total=total,
                exact_matches=sum(x["exact_match"] for x in details),
                decisions_correct=sum(x["decision_match"] for x in details),
                cases=details)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("key", type=Path)
    parser.add_argument("submission", type=Path)
    a = parser.parse_args()
    try:
        result = score(json.loads(a.key.read_text()), read_submission(a.submission))
    except (InvalidSubmission, OSError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
