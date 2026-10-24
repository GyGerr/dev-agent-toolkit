# Parser fixture

This small module uses Python's standard library and unittest. Review parse_count in
parse_count.py and the existing tests before proposing changes. Run focused tests with
`python3 -m unittest discover -s tests -v` from this directory.

The intended domain is non-negative decimal counts; negative and malformed inputs
should raise ValueError. Existing coverage is incomplete. This fixture intentionally
contains a defect for advisory review and scenario-based test-writing evaluation.
