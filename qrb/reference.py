"""Independent reference derived from evidence, not from the label manifest."""

def review(case):
    index = case["index"]
    evidence = [r for r in case["evidence"] if r["entity"] == index["subject_id"]]
    result = []

    def report(code, row):
        result.append({"code": code, "evidence_id": row["evidence_id"]})

    if case["workflow"] == "BATCH_RECORD":
        for item in evidence:
            if item["kind"] == "execution" and item["executed_revision"] != index["active_revision"]:
                report("BATCH_REVISION", item)
            if item["kind"] == "review" and item["reviewer"] == item["preparer"]:
                report("BATCH_REVIEWER", item)
    elif case["workflow"] == "QC_SUMMARY":
        total = sum(r["count"] for r in evidence if r["kind"] == "tally" and r["state"] == "active")
        for item in (r for r in evidence if r["kind"] == "summary"):
            if item["source_revision"] != index["current_source_revision"]:
                report("QC_SOURCE_REVISION", item)
            if item["count"] != total:
                report("QC_COUNT", item)
    elif case["workflow"] == "DEVIATION_PACKAGE":
        required = [r for r in evidence if r["kind"] == "action" and r["required"]]
        completed = [r["closed_at"] for r in required if r["status"] == "CLOSED"]
        for item in required:
            if item["status"] != "CLOSED":
                report("DEV_OPEN_ACTION", item)
        for item in (r for r in evidence if r["kind"] == "closure"):
            if any(when > item["closed_at"] for when in completed):
                report("DEV_EARLY_CLOSURE", item)
    else:
        raise ValueError(f"unknown workflow {case['workflow']!r}")
    return dict(case_id=case["case_id"], decision="HOLD" if result else "READY", findings=result)
