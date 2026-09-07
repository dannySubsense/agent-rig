"""Tests for scripts/signpost_checklist_probe.py — Slice 1 (data schemas + new verbatim parsers).

Spec: docs/specs/signpost-checklist-redesign/01-REQUIREMENTS.md (US-1 AC1/AC2) and
docs/specs/signpost-checklist-redesign/04-ROADMAP.md "## Slice 1" Tests section.

Scoped to Slice 1's three new parsing functions only — `extract_signpost_lines`,
`extract_pillar_rows`, `parse_checklist_row_line` — using hand-constructed markdown strings, no
transcript fixtures needed for this slice (per roadmap). Trigger-surface/tool-call-collection
(Slice 2) and evaluate_checklist/build_reason/run (Slices 3/4/5) are out of scope here.

Loads the copy the Stop hook is documented to execute (scripts/), matching this repo's existing
test convention (archive/first-turn-contract-enforcement/tests/test_first_turn_contract_probe.py).

Runnable two ways:
    pytest tests/test_signpost_checklist_probe.py
    python3 tests/test_signpost_checklist_probe.py   (falls back to a plain assert-based runner)
"""

import importlib.util
import os

try:
    import pytest  # noqa: F401
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "signpost_checklist_probe.py")


def _load_probe():
    spec = importlib.util.spec_from_file_location("signpost_checklist_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()


def _find_headings(text):
    """Helper mirroring find_signpost_pillar_positions()'s job for this slice's tests: locate
    the line indices of the Signpost/Pillar headings by the same label regexes the real
    implementation uses, without depending on Slice 2 (not yet built)."""
    lines = text.split("\n")
    signpost_idx = None
    pillar_idx = None
    for i, line in enumerate(lines):
        stripped = probe.strip_leading_markup(line)
        if signpost_idx is None and probe._SIGNPOST_LABEL_RE.match(stripped):
            signpost_idx = i
        if pillar_idx is None and probe._PILLAR_LABEL_RE.match(stripped):
            pillar_idx = i
    return signpost_idx, pillar_idx


# ---------------------------------------------------------------------------
# US-1 AC1/AC2 — N Signpost lines -> N verbatim rows; a Signpost line changing
# between turns -> new label matches verbatim.
# ---------------------------------------------------------------------------

def test_n_signpost_lines_produce_n_verbatim_lines():
    text = (
        "Signpost:\n"
        "- I read the config file.\n"
        "- I ran the test suite.\n"
        "- I updated the docs.\n"
        "\n"
        "Pillar:\n"
    )
    signpost_idx, pillar_idx = _find_headings(text)
    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert [l.text for l in lines] == [
        "I read the config file.",
        "I ran the test suite.",
        "I updated the docs.",
    ]


def test_signpost_line_change_between_turns_matches_verbatim():
    turn1 = "Signpost:\n- I read the config file.\n\nPillar:\n"
    turn2 = "Signpost:\n- I read the config file and the schema.\n\nPillar:\n"

    idx1 = _find_headings(turn1)
    idx2 = _find_headings(turn2)

    lines1 = probe.extract_signpost_lines(turn1, *idx1)
    lines2 = probe.extract_signpost_lines(turn2, *idx2)

    assert [l.text for l in lines1] == ["I read the config file."]
    assert [l.text for l in lines2] == ["I read the config file and the schema."]
    assert lines1[0].text != lines2[0].text


# ---------------------------------------------------------------------------
# parse_checklist_row_line
# ---------------------------------------------------------------------------

def test_parse_checklist_row_line_matches_unchecked_with_unverified_suffix():
    row = probe.parse_checklist_row_line("- [ ] I read the config file. (unverified)")
    assert row is not None
    assert row.label == "I read the config file."
    assert row.status == "unverified"
    assert row.tool_use_id is None


def test_parse_checklist_row_line_matches_lowercase_x_with_verified_suffix():
    row = probe.parse_checklist_row_line(
        "- [x] I ran the test suite. (verified: tool_use_id=toolu_abc123)"
    )
    assert row is not None
    assert row.label == "I ran the test suite."
    assert row.status == "verified"
    assert row.tool_use_id == "toolu_abc123"


def test_parse_checklist_row_line_matches_uppercase_x_with_verified_suffix():
    row = probe.parse_checklist_row_line(
        "- [X] I updated the docs. (verified: tool_use_id=toolu_def456)"
    )
    assert row is not None
    assert row.label == "I updated the docs."
    assert row.status == "verified"
    assert row.tool_use_id == "toolu_def456"


def test_parse_checklist_row_line_returns_none_for_missing_status_suffix():
    row = probe.parse_checklist_row_line("- [ ] I read the config file.")
    assert row is None


def test_parse_checklist_row_line_returns_none_for_non_matching_line():
    row = probe.parse_checklist_row_line("This is just prose, not a checklist row.")
    assert row is None


# ---------------------------------------------------------------------------
# Edge case: empty Signpost section -> extract_signpost_lines returns [].
# ---------------------------------------------------------------------------

def test_extract_signpost_lines_returns_empty_list_when_no_heading():
    text = "Some reply with no Signpost heading at all.\n"
    lines = probe.extract_signpost_lines(text, None, None)
    assert lines == []


def test_extract_signpost_lines_returns_empty_list_when_heading_present_but_no_content():
    text = "Signpost:\n\nPillar:\n"
    signpost_idx, pillar_idx = _find_headings(text)
    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert lines == []


# ---------------------------------------------------------------------------
# extract_pillar_rows: a non-conforming Pillar line is absent from PillarRow
# list and present in unparsed_lines.
# ---------------------------------------------------------------------------

def test_extract_pillar_rows_puts_non_conforming_line_in_unparsed_lines():
    text = (
        "Signpost:\n- I ran the tests.\n\n"
        "Pillar:\n"
        "- [ ] I ran the tests. (unverified)\n"
        "This is stray prose, not a valid row.\n"
    )
    lines = text.split("\n")
    pillar_idx = None
    for i, line in enumerate(lines):
        if probe._PILLAR_LABEL_RE.match(line):
            pillar_idx = i
            break
    rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))

    assert len(rows) == 1
    assert rows[0].label == "I ran the tests."
    assert "This is stray prose, not a valid row." in unparsed
    assert all(r.raw_line != "This is stray prose, not a valid row." for r in rows)


# ---------------------------------------------------------------------------
# extract_signpost_lines: heading-line-only trailing prose counts as content,
# not as a claim line — signpost_section_has_content derivable True,
# signpost_lines == [].
#
# Per the implementation's own docstring (§4), extract_signpost_lines does NOT return a
# signpost_section_has_content bool itself — that flag is derived by the caller from whether the
# heading-line trailing text (plus any between-heading text) is non-blank. This test verifies
# both halves of that real contract: extract_signpost_lines returns [] for this input, and the
# caller-derivable content flag (computed the same way architecture §4 describes: non-blank text
# present) is True.
# ---------------------------------------------------------------------------

def test_extract_signpost_lines_heading_trailing_prose_is_content_not_a_claim_line():
    text = "Signpost: I verified the build and the tests.\n"
    signpost_idx, pillar_idx = _find_headings(text)
    assert signpost_idx == 0
    assert pillar_idx is None

    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert lines == []

    # Caller-derived signpost_section_has_content, per §4: non-blank trailing content on the
    # heading line itself (after the "Signpost:" label is stripped) counts as content.
    heading_raw = text.split("\n")[signpost_idx]
    label_match = probe._SIGNPOST_LABEL_RE.match(heading_raw)
    trailing = label_match.group(1) if label_match else ""
    signpost_section_has_content = bool(trailing.strip())
    assert signpost_section_has_content is True


# ---------------------------------------------------------------------------
# extract_pillar_rows: bare "Pillar:" heading does not self-flag; heading line
# with trailing content IS evaluated as a normal line.
# ---------------------------------------------------------------------------

def test_extract_pillar_rows_bare_heading_does_not_self_flag():
    text = "Signpost:\n- I ran the tests.\n\nPillar:\n- [ ] I ran the tests. (unverified)\n"
    lines = text.split("\n")
    pillar_idx = None
    for i, line in enumerate(lines):
        if probe._PILLAR_LABEL_RE.match(line):
            pillar_idx = i
            break
    rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))

    assert "Pillar:" not in unparsed
    assert all("Pillar:" not in r.raw_line for r in rows)
    assert len(rows) == 1


def test_extract_pillar_rows_heading_trailing_content_is_evaluated_as_normal_line():
    text = "Signpost:\n- I ran the tests.\n\nPillar: all verified, trust me\n"
    lines = text.split("\n")
    pillar_idx = None
    for i, line in enumerate(lines):
        if probe._PILLAR_LABEL_RE.match(line):
            pillar_idx = i
            break
    rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))

    # "all verified, trust me" does not match the forced row syntax, so it must land in
    # unparsed_lines (stray prose) rather than being silently dropped or ignored.
    assert rows == []
    assert "all verified, trust me" in unparsed


# ---------------------------------------------------------------------------
# QC fix coverage: markdown-styled and qualified heading forms handled by
# strip_leading_markup() + the updated _SIGNPOST_LABEL_RE/_PILLAR_LABEL_RE.
# ---------------------------------------------------------------------------


def test_markdown_heading_prefix_trailing_prose_is_content_not_a_claim_line():
    text = "## Signpost: I verified the build and the tests.\n"
    signpost_idx, pillar_idx = _find_headings(text)
    assert signpost_idx == 0
    assert pillar_idx is None

    # extract_signpost_lines: no list items beneath, so the final result is [].
    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert lines == []

    # But the label strips correctly and the trailing prose is captured as candidate
    # content at the label-match stage, not silently dropped — confirms the `##` prefix
    # doesn't defeat the label match.
    heading_raw = text.split("\n")[signpost_idx]
    label_match = probe._SIGNPOST_LABEL_RE.match(probe.strip_leading_markup(heading_raw))
    assert label_match is not None
    assert label_match.group(1) == "I verified the build and the tests."


def test_bold_styled_signpost_label_alone_strips_to_valid_empty_heading():
    text = "**Signpost:**\n"
    heading_raw = text.split("\n")[0]
    label_match = probe._SIGNPOST_LABEL_RE.match(probe.strip_leading_markup(heading_raw))
    assert label_match is not None
    assert label_match.group(1) == ""

    signpost_idx, pillar_idx = _find_headings(text)
    assert signpost_idx == 0
    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert lines == []


def test_bold_styled_pillar_heading_trailing_content_lands_in_unparsed_lines():
    text = "Signpost:\n- I ran the tests.\n\n**Pillar:** all verified, trust me\n"
    lines = text.split("\n")
    signpost_idx, pillar_idx = _find_headings(text)
    assert pillar_idx is not None

    rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))

    # Before the fix, the bold `**Pillar:**` heading form was not recognized as a label
    # match, so this trailing prose was silently invisible to the probe (rule 1b evasion).
    # Now it must land in unparsed_lines, same as the unstyled form.
    assert rows == []
    assert "all verified, trust me" in unparsed


def test_qualified_signpost_heading_pre_colon_text_strips_correctly():
    text = "Signpost (this turn): I verified the build.\n"
    signpost_idx, pillar_idx = _find_headings(text)
    assert signpost_idx == 0
    assert pillar_idx is None

    heading_raw = text.split("\n")[signpost_idx]
    label_match = probe._SIGNPOST_LABEL_RE.match(probe.strip_leading_markup(heading_raw))
    assert label_match is not None
    assert label_match.group(1) == "I verified the build."

    lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    assert lines == []


# ---------------------------------------------------------------------------
# Slice 2 — reused trigger-surface / tool-call-collection functions (§5.1),
# copied from the archived probe, plus the one additive change (§5.1a) to
# collect_qualifying_tool_calls().
#
# No dedicated unit tests for these functions exist in
# archive/first-turn-contract-enforcement/tests/test_first_turn_contract_probe.py — that
# suite exercises them only indirectly through probe.run() end-to-end fixtures. Per the
# roadmap's fallback instruction, minimal smoke tests are written here against a
# representative transcript fixture built in the same real-record shape the archived
# suite's own fixture builders use (attachment-shaped queue marker, assistant text/tool_use/
# tool_result records) rather than a synthetic shape.
# ---------------------------------------------------------------------------

def _queue_marker_record():
    """Real SessionStart injection shape (§5.1) — mirrors the archived suite's own fixture
    builder (attachment-shaped, no `message` key)."""
    return {
        "parentUuid": None,
        "isSidechain": False,
        "attachment": {
            "type": "hook_additional_context",
            "content": [probe.QUEUE_MARKER + "\nSIGNPOST — from the queue.\n"],
            "hookName": "SessionStart",
            "toolUseID": "SessionStart",
            "hookEvent": "SessionStart",
        },
        "type": "attachment",
        "uuid": "test-attachment-uuid",
    }


def _assistant_text_record(text):
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {"content": [{"type": "text", "text": text}]},
    }


def _tool_use_record(name, tool_id, tool_input=None):
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {
            "content": [
                {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input or {}}
            ]
        },
    }


def _tool_result_record(tool_id):
    return {
        "type": "user",
        "isSidechain": False,
        "message": {"content": [{"type": "tool_result", "tool_use_id": tool_id}]},
    }


def test_smoke_heading_detection_finds_signpost_and_pillar_positions():
    text = "Signpost:\n- I ran the tests.\n\nPillar:\n- [ ] I ran the tests. (unverified)\n"
    signpost_idx, pillar_idx = probe.find_signpost_pillar_positions(text)
    assert signpost_idx == 0
    assert pillar_idx == 3
    assert probe.find_pillar_heading_line(text, pillar_idx) == "Pillar:"


def test_smoke_analyze_queue_injection_and_first_turn_on_real_shaped_transcript():
    records = [
        _queue_marker_record(),
        _assistant_text_record("Signpost:\n- I ran the tests.\n\nPillar:\n"),
    ]
    queue_injected, first_turn, current_turn_index = probe.analyze_queue_injection_and_first_turn(
        records
    )
    assert queue_injected is True
    assert first_turn is True
    assert current_turn_index == 1


def test_smoke_collect_qualifying_tool_calls_correlates_tool_use_and_result():
    records = [
        _tool_use_record("Read", "toolu_001"),
        _tool_result_record("toolu_001"),
        _tool_use_record("TodoWrite", "toolu_002"),
        _tool_result_record("toolu_002"),
    ]
    calls = probe.collect_qualifying_tool_calls(records)
    names = {c.name for c in calls}
    assert "Read" in names
    assert "TodoWrite" not in names  # excluded via EXCLUDED_TOOLS


def test_grep_no_deleted_c2_c3_machinery_symbols_in_new_file():
    deleted_symbols = [
        "_C2_LABEL_RE",
        "find_c2_heading_line",
        "_extract_claim_subjects",
        "_subject_matches_target",
        "_path_components_align",
        "_phrase_boundary_match",
        "_FILE_PATH_RE",
        "_PR_NUMBER_RE",
        "_IDENTIFIER_RE",
        "_QUOTED_QUERY_RE",
        "_GH_",
        "check_c3_violation",
    ]
    with open(PROBE_PATH) as fh:
        source = fh.read()
    for symbol in deleted_symbols:
        assert symbol not in source, f"deleted-machinery symbol {symbol!r} found in {PROBE_PATH}"


def test_collect_qualifying_tool_calls_tool_use_id_matches_real_tool_use_block_id():
    records = [
        _tool_use_record("Read", "toolu_real_id_123"),
        _tool_result_record("toolu_real_id_123"),
        _tool_use_record("Bash", "toolu_real_id_456"),
        _tool_result_record("toolu_real_id_456"),
    ]
    calls = probe.collect_qualifying_tool_calls(records)
    assert len(calls) == 2
    returned_ids = {c.tool_use_id for c in calls}
    real_ids = set()
    for r in records:
        for block in r.get("message", {}).get("content", []):
            if block.get("type") == "tool_use":
                real_ids.add(block["id"])
    assert returned_ids == real_ids


# ---------------------------------------------------------------------------
# Plain-assert fallback runner (matches archived probe's test file convention).
# ---------------------------------------------------------------------------

def _run_all():
    tests = [obj for name, obj in globals().items() if name.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__" and not HAVE_PYTEST:
    _run_all()
