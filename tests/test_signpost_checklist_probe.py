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
# Slice 3 — evaluate_checklist() + build_reason() evaluation core.
#
# Spec: docs/specs/signpost-checklist-redesign/01-REQUIREMENTS.md (US-2 AC1/AC2/AC3, US-3
# AC1/AC2/AC3/AC4) and docs/specs/signpost-checklist-redesign/04-ROADMAP.md "## Slice 3" Tests
# section. Per architecture §9's testability approach, these are pure-function tests against
# evaluate_checklist()'s inputs/outputs directly — no transcript fixtures needed.
# ---------------------------------------------------------------------------


def _row(label, status, tool_use_id=None, raw_line=None):
    return probe.PillarRow(
        label=label,
        status=status,
        tool_use_id=tool_use_id,
        raw_line=raw_line if raw_line is not None else f"- [{'x' if status == 'verified' else ' '}] {label}",
    )


def _line(text):
    return probe.SignpostLine(text=text, raw_line=f"- {text}")


def _call(tool_use_id, name="Read"):
    return probe.QualifyingToolCall(tool_use_id=tool_use_id, name=name, tool_input={})


# --- US-2 AC1: verified row must be backed by a real qualifying tool call -----------------

def test_us2_ac1_verified_row_backed_by_real_tool_call_produces_no_violation():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I read the config file.")],
        pillar_rows=[_row("I read the config file.", "verified", tool_use_id="toolu_1")],
        qualifying_calls=[_call("toolu_1")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "allow"
    assert result.violations == []


# --- US-2 AC2: claimed tool_use_id absent from transcript -> unbacked/false_claim ----------

def test_us2_ac2_verified_row_claiming_nonexistent_tool_call_is_false_claim():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I ran the tests.")],
        pillar_rows=[_row("I ran the tests.", "verified", tool_use_id="toolu_fake")],
        qualifying_calls=[_call("toolu_real")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert len(result.violations) == 1
    assert result.violations[0].kind == "false_claim"


# --- US-2 AC3: unverified row never penalized on its own -----------------------------------

def test_us2_ac3_unverified_row_never_penalized():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I have not checked this yet.")],
        pillar_rows=[_row("I have not checked this yet.", "unverified")],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "allow"
    assert result.violations == []


# --- US-3 AC1: Signpost row absent from Pillar checklist -> FAIL ---------------------------

def test_us3_ac1_missing_pillar_row_for_signpost_line_fails():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I updated the docs.")],
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert result.violations[0].kind == "missing"
    assert result.violations[0].signpost_text == "I updated the docs."


# --- US-3 AC2: verified row lacking tool-call-backed evidence -> FAIL ----------------------

def test_us3_ac2_verified_row_lacking_evidence_fails():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I fixed the bug.")],
        pillar_rows=[_row("I fixed the bug.", "verified", tool_use_id="toolu_none")],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert result.violations[0].kind == "false_claim"


# --- US-3 AC3: Pillar row matching no Signpost line is still evaluated + flagged -----------

def test_us3_ac3_unmatched_pillar_row_still_evaluated_and_flagged():
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[_row("I did something extra.", "unverified")],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    kinds = {v.kind for v in result.violations}
    assert "unmatched_row" in kinds


# --- US-3 AC4: all rows present/matched/valid -> PASS ---------------------------------------

def test_us3_ac4_all_rows_matched_and_valid_passes():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("Line A."), _line("Line B.")],
        pillar_rows=[
            _row("Line A.", "unverified"),
            _row("Line B.", "verified", tool_use_id="toolu_b"),
        ],
        qualifying_calls=[_call("toolu_b")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "allow"
    assert result.violations == []


# --- Rule 0: Signpost heading absent entirely -> fail-closed block, no per-line violations --

def test_rule0_signpost_heading_absent_blocks_with_no_violations():
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=False,
        signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert result.signpost_heading_absent is True
    assert result.violations == []


# --- Rule 0a: heading present, has content, zero parsed claim lines -> block -----------------

def test_rule0a_heading_present_with_content_but_no_parsed_lines_blocks():
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert len(result.violations) == 1
    assert result.violations[0].kind == "malformed_signpost"


def test_rule0a_heading_line_trailing_prose_path_blocks_with_malformed_signpost():
    # signpost_section_has_content derived specifically from trailing text on the heading line
    # itself (e.g. "Signpost: I verified the build."), not text between headings.
    text = "Signpost: I verified the build and the tests.\n"
    signpost_idx, pillar_idx = probe.find_signpost_pillar_positions(text)
    signpost_lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)
    heading_raw = text.split("\n")[signpost_idx]
    label_match = probe._SIGNPOST_LABEL_RE.match(probe.strip_leading_markup(heading_raw))
    signpost_section_has_content = bool((label_match.group(1) if label_match else "").strip())

    assert signpost_lines == []
    assert signpost_section_has_content is True

    result = probe.evaluate_checklist(
        signpost_lines=signpost_lines,
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=signpost_section_has_content,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert result.violations[0].kind == "malformed_signpost"


# --- Rule 1a: duplicate_label -----------------------------------------------------------------

def test_rule1a_two_rows_matching_same_signpost_line_both_flagged_duplicate_label():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("I ran the tests.")],
        pillar_rows=[
            _row("I ran the tests.", "unverified"),
            _row("I ran the tests.", "verified", tool_use_id="toolu_x"),
        ],
        qualifying_calls=[_call("toolu_x")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    dup_violations = [v for v in result.violations if v.kind == "duplicate_label"]
    assert len(dup_violations) == 2


# --- Rule 1b: stray_prose --------------------------------------------------------------------

def test_rule1b_non_conforming_pillar_line_flagged_stray_prose():
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=False,
        pillar_unparsed_lines=["This is stray prose, not a valid row."],
    )
    assert result.decision == "block"
    stray = [v for v in result.violations if v.kind == "stray_prose"]
    assert len(stray) == 1
    assert stray[0].line_text == "This is stray prose, not a valid row."


def test_rule1b_bare_pillar_heading_line_does_not_self_flag():
    text = "Signpost:\n- I ran the tests.\n\nPillar:\n- [ ] I ran the tests. (unverified)\n"
    lines = text.split("\n")
    signpost_idx, pillar_idx = probe.find_signpost_pillar_positions(text)
    pillar_rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))
    signpost_lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)

    result = probe.evaluate_checklist(
        signpost_lines=signpost_lines,
        pillar_rows=pillar_rows,
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=unparsed,
    )
    assert result.decision == "allow"
    assert result.violations == []


def test_rule1b_pillar_heading_with_trailing_content_flagged_stray_prose():
    text = "Signpost:\n- I ran the tests.\n\nPillar: all verified, trust me\n"
    lines = text.split("\n")
    signpost_idx, pillar_idx = probe.find_signpost_pillar_positions(text)
    pillar_rows, unparsed = probe.extract_pillar_rows(text, pillar_idx, len(lines))
    signpost_lines = probe.extract_signpost_lines(text, signpost_idx, pillar_idx)

    result = probe.evaluate_checklist(
        signpost_lines=signpost_lines,
        pillar_rows=pillar_rows,
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=unparsed,
    )
    assert result.decision == "block"
    stray = [v for v in result.violations if v.kind == "stray_prose"]
    assert len(stray) == 1
    assert stray[0].line_text == "all verified, trust me"


# --- Rule 5: duplicate_id -------------------------------------------------------------------

def test_rule5_second_row_reusing_tool_use_id_flagged_duplicate_id():
    result = probe.evaluate_checklist(
        signpost_lines=[_line("Line A."), _line("Line B.")],
        pillar_rows=[
            _row("Line A.", "verified", tool_use_id="toolu_shared"),
            _row("Line B.", "verified", tool_use_id="toolu_shared"),
        ],
        qualifying_calls=[_call("toolu_shared")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert len(result.violations) == 1
    assert result.violations[0].kind == "duplicate_id"
    assert result.violations[0].row.label == "Line B."


def test_rule5_evaluation_order_unmatched_row_evaluated_later_is_flagged_duplicate_id():
    # 2026-09-07 clarification: rule 5's "earlier" is resolved by evaluation order (main
    # per-Signpost-line pass, then the rule-7 residue pass over unmatched rows) — NOT by the
    # order rows appear in the agent's raw reply text. Here the unmatched row is placed FIRST
    # in pillar_rows (as it would be if it appeared first in the raw text), but since it has no
    # matching Signpost line it is evaluated in the later residue pass, so it — not the matched
    # row — must be the one flagged duplicate_id.
    unmatched = _row("Extra claim not in Signpost.", "verified", tool_use_id="toolu_shared")
    matched = _row("Line A.", "verified", tool_use_id="toolu_shared")

    result = probe.evaluate_checklist(
        signpost_lines=[_line("Line A.")],
        pillar_rows=[unmatched, matched],  # unmatched appears first in raw order
        qualifying_calls=[_call("toolu_shared")],
        signpost_heading_present=True,
        signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    dup_id_violations = [v for v in result.violations if v.kind == "duplicate_id"]
    assert len(dup_id_violations) == 1
    assert dup_id_violations[0].row is unmatched
    unmatched_row_violations = [v for v in result.violations if v.kind == "unmatched_row"]
    assert len(unmatched_row_violations) == 1
    assert unmatched_row_violations[0].row is unmatched


# --- Rule 7: unmatched_row -------------------------------------------------------------------

def test_rule7_unmatched_row_runs_through_rules_3_5_and_always_flagged_unmatched():
    unmatched = _row("Nothing in Signpost matches this.", "verified", tool_use_id="toolu_fake")
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[unmatched],
        qualifying_calls=[],  # no real tool call -> rule 4 false_claim
        signpost_heading_present=True,
        signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    kinds = [v.kind for v in result.violations]
    assert "false_claim" in kinds
    assert "unmatched_row" in kinds


def test_rule7_unmatched_row_always_flagged_regardless_of_status():
    unmatched = _row("Unverified extra claim.", "unverified")
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[unmatched],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "block"
    assert len(result.violations) == 1
    assert result.violations[0].kind == "unmatched_row"


# --- Edge case: empty Signpost section (no heading content anywhere) -> allow --------------

def test_edge_empty_signpost_section_with_no_pillar_content_allows():
    result = probe.evaluate_checklist(
        signpost_lines=[],
        pillar_rows=[],
        qualifying_calls=[],
        signpost_heading_present=True,
        signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    assert result.decision == "allow"
    assert result.violations == []


# --- Edge case: no cross-call state between independent evaluate_checklist() calls ---------

def test_edge_repeated_identical_signpost_line_across_two_calls_no_shared_state():
    def run_once():
        return probe.evaluate_checklist(
            signpost_lines=[_line("I ran the tests.")],
            pillar_rows=[_row("I ran the tests.", "verified", tool_use_id="toolu_shared")],
            qualifying_calls=[_call("toolu_shared")],
            signpost_heading_present=True,
            signpost_section_has_content=True,
            pillar_unparsed_lines=[],
        )

    result1 = run_once()
    result2 = run_once()

    # If claimed_tool_use_ids leaked across calls, the second call's use of "toolu_shared"
    # would be misflagged as duplicate_id. Both calls must independently allow.
    assert result1.decision == "allow"
    assert result2.decision == "allow"
    assert result1.violations == []
    assert result2.violations == []


# --- build_reason(): distinct, non-colliding strings per violation kind --------------------

def test_build_reason_rule0_string_distinct_from_rule0a_and_per_row_strings():
    rule0_result = probe.evaluate_checklist(
        signpost_lines=[], pillar_rows=[], qualifying_calls=[],
        signpost_heading_present=False, signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )
    rule0a_result = probe.evaluate_checklist(
        signpost_lines=[], pillar_rows=[], qualifying_calls=[],
        signpost_heading_present=True, signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    missing_result = probe.evaluate_checklist(
        signpost_lines=[_line("A claim.")], pillar_rows=[], qualifying_calls=[],
        signpost_heading_present=True, signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )

    reasons = {rule0_result.reason, rule0a_result.reason, missing_result.reason}
    assert len(reasons) == 3  # all distinct, no collisions
    assert "Signpost section" in rule0_result.reason
    assert "no lines were written as" in rule0a_result.reason
    assert "Missing Pillar row" in missing_result.reason


def test_build_reason_per_row_violation_kinds_produce_distinct_sentences():
    duplicate_label_row = _row("Dup line.", "unverified")
    dup_result = probe.evaluate_checklist(
        signpost_lines=[_line("Dup line.")],
        pillar_rows=[duplicate_label_row, _row("Dup line.", "unverified")],
        qualifying_calls=[],
        signpost_heading_present=True, signpost_section_has_content=True,
        pillar_unparsed_lines=[],
    )
    stray_result = probe.evaluate_checklist(
        signpost_lines=[], pillar_rows=[], qualifying_calls=[],
        signpost_heading_present=True, signpost_section_has_content=False,
        pillar_unparsed_lines=["stray text here"],
    )
    unmatched_result = probe.evaluate_checklist(
        signpost_lines=[], pillar_rows=[_row("Orphan.", "unverified")], qualifying_calls=[],
        signpost_heading_present=True, signpost_section_has_content=False,
        pillar_unparsed_lines=[],
    )

    assert "Duplicate Pillar row label" in dup_result.reason
    assert "Unrecognized line in Pillar section" in stray_result.reason
    assert "does not match any Signpost line" in unmatched_result.reason
    assert dup_result.reason != stray_result.reason != unmatched_result.reason


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
