"""Solver-facing benchmark contract. All policies are fictional."""
POLICY = """You are reviewing synthetic quality-document packages for a fictional records team.
Use ONLY the local rules stated here. HOLD means return the documentation package for correction.
READY means the documentation checks pass. These decisions have no physical release meaning.

Each case has a case ID, a workflow, an index and a set of evidence rows.
Only the subject named in index.subject_id is in scope. Other entities are distractors.
Record identified defects and cite exactly the primary row ID specified below.
An OPEN case, incomplete form, or extra row is not a defect unless a rule explicitly says so.

BATCH_RECORD
- BATCH_REVISION: report the subject's executed revision if it differs from the active revision
  in the index. Cite the execution row.
- BATCH_REVIEWER: report the subject's signed review if the preparer and reviewer are
  the same person. Cite the review row.

QC_SUMMARY
- QC_SOURCE_REVISION: report a subject summary whose source_revision differs from the
  index's current source revision. Cite the summary row.
- QC_COUNT: report a subject summary whose count differs from the sum of the subject's
  active tally rows. Ignore void rows. Cite the summary row.

DEVIATION_PACKAGE
- DEV_OPEN_ACTION: report each subject action that is marked required and is not CLOSED.
  Cite the action row for each.
- DEV_EARLY_CLOSURE: report a subject closure timestamp that precedes the timestamp of a
  required CLOSED action. Cite the closure row once, even if several actions qualify.
  All timestamps are normalized UTC, ISO 8601.

Return a single JSON object with the key 'reviews'. Value is a list with one object per case,
each having 'case_id', 'decision' ('READY' or 'HOLD'), and 'findings'. Each finding must have
exactly 'code' and 'evidence_id'. A READY decision has an empty findings list.
Use HOLD when you found at least one rule violation. Do not include commentary or Markdown.
"""
