"""
Verifies scripts/adr/generate_index.py: parsing ADR frontmatter, regenerating
docs/adr/INDEX.md, and looking up the decisions that scope a path.
"""

from pathlib import Path
from typing import Any

import pytest

from scripts.adr.generate_index import (
    ADR_INDEX_FILENAME,
    EMPTY_NOTE,
    HIDDEN_STATUSES,
    INDEX_HEADER,
    REVISIT_DISCHARGED_BY_FIELD,
    REVISIT_WHEN_FIELD,
    SCOPE_FIELD,
    STATUS_FIELDS,
    TABLE_HEADER,
    TAGS_FIELD,
    cell,
    generate,
    main,
    parse_adr,
    relative_to_repo,
    report_scoped_to,
    scope_matches,
    scope_problems,
)

SCOPED_FILE = "README.md"
TRIGGER = "A second plugin joins the marketplace."


def adr(
    status: str | None = "Accepted",
    title: str = "1: Do the thing",
    fields: dict[str, Any] | None = None,
) -> str:
    """Build ADR file text with the given frontmatter; a `None` field is omitted."""
    merged: dict[str, Any] = {"status": status} | (fields or {})
    lines = ["date: 2026-08-01", f"scope: [{SCOPED_FILE}]", "summary: A summary."]
    for key, value in merged.items():
        lines = [line for line in lines if not line.startswith(f"{key}:")]
        if value is not None:
            lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {title}\n\nBody.\n"


@pytest.fixture(name="repo_root")
def fixture_repo_root(tmp_path: Path) -> Path:
    """A temp repo root with the file `SCOPED_FILE` names, for scope entries to resolve."""
    (tmp_path / SCOPED_FILE).write_text("", encoding="utf-8")
    return tmp_path


@pytest.fixture(name="adr_dir")
def fixture_adr_dir(repo_root: Path) -> Path:
    """A temp docs/adr directory beneath `repo_root`."""
    directory = repo_root / "docs" / "adr"
    directory.mkdir(parents=True)
    return directory


def write(adr_dir: Path, name: str, content: str) -> None:
    """Place one ADR file in `adr_dir`."""
    (adr_dir / name).write_text(content, encoding="utf-8")


def index_text(adr_dir: Path) -> str:
    """Read the generated index back."""
    return (adr_dir / ADR_INDEX_FILENAME).read_text(encoding="utf-8")


class TestParseAdr:
    """Unit tests for `parse_adr()`: every rule an ADR document must satisfy."""

    def test_returns_no_problems_for_a_valid_adr(self) -> None:
        """A well-formed ADR parses clean, with its status and title extracted."""
        fields, title, problems = parse_adr(adr())
        assert problems == []
        assert title == "Do the thing"
        assert fields["status"] == "Accepted"

    def test_reports_a_missing_frontmatter_block(self) -> None:
        """A file with no frontmatter is reported, not silently omitted from the index."""
        _, _, problems = parse_adr("# 1: Title\n\nBody.\n")
        assert problems == ["has no frontmatter block"]

    def test_reports_a_missing_title(self) -> None:
        """A file with no level-one heading has no title to put in the index."""
        content = "---\nstatus: Accepted\nscope: []\n---\n\nBody with no heading.\n"
        assert "has no level-one title heading" in parse_adr(content)[2]

    def test_strips_the_number_prefix_from_the_title(self) -> None:
        """The index column carries the title alone; the number is already its own column."""
        _, title, _ = parse_adr(adr(title="7: Keep it simple"))
        assert title == "Keep it simple"

    def test_keeps_a_title_that_has_no_number_prefix(self) -> None:
        """A title written without a number is left as it stands."""
        _, title, _ = parse_adr(adr(title="Keep it simple"))
        assert title == "Keep it simple"

    def test_reports_invalid_yaml(self) -> None:
        """Broken YAML is reported by name rather than raising out of the generator."""
        content = "---\nstatus: [unterminated\n---\n\n# 1: Title\n\nBody.\n"
        assert any("invalid YAML" in problem for problem in parse_adr(content)[2])

    def test_rejects_an_unrecognised_status(self) -> None:
        """A status outside the vocabulary must not reach the index as a literal."""
        problem = parse_adr(adr(status="Draft"))[2][0]
        assert "'Draft'" in problem
        assert "Accepted, Archived, Superseded" in problem

    def test_rejects_a_status_in_the_wrong_case(self) -> None:
        """Matching is exact, so `archived` cannot quietly hide an ADR."""
        assert "'archived'" in parse_adr(adr(status="archived"))[2][0]

    def test_rejects_a_missing_status(self) -> None:
        """An ADR with no status has no place in the index either way."""
        assert "None" in parse_adr(adr(status=None))[2][0]

    @pytest.mark.parametrize("status, field", STATUS_FIELDS.items())
    def test_requires_the_field_each_status_owns(self, status: str, field: str) -> None:
        """Archived and Superseded each carry a field saying why; neither is optional."""
        assert (
            f"is {status} but declares no `{field}`" in parse_adr(adr(status=status))[2]
        )

    def test_rejects_a_status_field_its_status_does_not_own(self) -> None:
        """A field left behind by a status change would otherwise read as current."""
        problems = parse_adr(adr(fields={"archived-because": "A comment."}))[2]
        assert (
            "declares `archived-because` but its status is 'Accepted', not Archived"
            in problems
        )

    def test_accepts_a_status_carrying_its_own_field(self) -> None:
        """The pairing is required, so the valid combination must pass cleanly."""
        assert (
            parse_adr(adr(status="Superseded", fields={"superseded-by": 12}))[2] == []
        )

    def test_accepts_a_revisit_trigger_on_its_own(self) -> None:
        """A live trigger is the ordinary case: it needs no discharge until one arrives."""
        assert parse_adr(adr(fields={REVISIT_WHEN_FIELD: TRIGGER}))[2] == []

    def test_accepts_a_discharge_paired_with_the_trigger_it_spent(self) -> None:
        """The pairing is required, so the valid combination must pass cleanly."""
        fields = {REVISIT_WHEN_FIELD: TRIGGER, REVISIT_DISCHARGED_BY_FIELD: 12}
        assert parse_adr(adr(fields=fields))[2] == []

    def test_rejects_a_discharge_with_no_trigger(self) -> None:
        """A discharge alone records that something was spent without saying what."""
        problems = parse_adr(adr(fields={REVISIT_DISCHARGED_BY_FIELD: 12}))[2]
        assert (
            f"declares `{REVISIT_DISCHARGED_BY_FIELD}` but no `{REVISIT_WHEN_FIELD}` to spend"
            in problems
        )

    def test_rejects_the_field_scope_replaced(self) -> None:
        """A stale `tags` must fail, or a half-finished migration passes unnoticed."""
        problem = parse_adr(adr(fields={TAGS_FIELD: "[alpha, beta]"}))[2][0]
        assert f"declares `{TAGS_FIELD}`" in problem
        assert f"`{SCOPE_FIELD}` replaced" in problem

    def test_rejects_a_missing_scope(self) -> None:
        """Required, so that an absent field cannot pass for a decision binding no path."""
        problems = parse_adr(adr(fields={SCOPE_FIELD: None}))[2]
        assert (
            f"declares no `{SCOPE_FIELD}`; list the paths it binds, or `[]` where it binds none"
            in problems
        )

    def test_accepts_a_scope_binding_no_path(self) -> None:
        """`[]` is the answer for a decision whose subject has no file, not an omission."""
        assert parse_adr(adr(fields={SCOPE_FIELD: "[]"}))[2] == []

    def test_rejects_a_scope_written_as_a_scalar(self) -> None:
        """One bare path parses as a string, which would iterate character by character."""
        problem = parse_adr(adr(fields={SCOPE_FIELD: "scripts/"}))[2][0]
        assert f"declares `{SCOPE_FIELD}` as a scalar" in problem

    def test_collects_every_problem_in_one_pass(self) -> None:
        """One fix must not be the thing that reveals the next."""
        content = "---\nstatus: Draft\n---\n\nNo heading.\n"
        # Bad status, missing scope, missing title: three problems from one file.
        assert len(parse_adr(content)[2]) == 3


class TestScopeProblems:
    """Unit tests for `scope_problems()`: the one rule needing the filesystem."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path) -> None:
        self.root = tmp_path
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "versions.py").write_text("", encoding="utf-8")

    def test_accepts_entries_that_resolve(self) -> None:
        """A file and a directory prefix both name something; neither is a problem."""
        assert scope_problems(["scripts/versions.py", "scripts/"], self.root) == []

    def test_reports_an_entry_matching_nothing(self) -> None:
        """A path that moved leaves a scope naming code that is no longer there."""
        problem = scope_problems(["scripts/gone.py"], self.root)[0]
        assert "scopes `scripts/gone.py`, which nothing matches" in problem

    def test_reports_a_directory_written_without_its_slash(self) -> None:
        """Without the slash, nothing beneath the directory matches, so it silently binds one path."""
        problems = scope_problems(["scripts"], self.root)
        assert "scopes `scripts`, a directory; write it as `scripts/`" in problems

    def test_reports_an_entry_written_as_a_glob(self) -> None:
        """A glob is the natural thing to reach for, and "nothing matches" would misdiagnose it."""
        problem = scope_problems(["scripts/**/*.py"], self.root)[0]
        assert "which reads as a glob" in problem

    def test_reports_every_bad_entry(self) -> None:
        """One scope may hold several paths, and one fix must not reveal the next."""
        assert len(scope_problems(["a.py", "b.py"], self.root)) == 2


class TestRelativeToRepo:
    """Unit tests for `relative_to_repo()`."""

    def test_leaves_a_relative_path_alone(self, tmp_path: Path) -> None:
        """Scope entries are written repo-relative, so that form is already the answer."""
        assert (
            relative_to_repo("src/class_registry/base.py", tmp_path)
            == "src/class_registry/base.py"
        )

    def test_converts_an_absolute_path_inside_the_repo(self, tmp_path: Path) -> None:
        """An editor or an agent hands you an absolute path, which matches no scope entry."""
        absolute = str(tmp_path / "src" / "class_registry" / "base.py")
        assert relative_to_repo(absolute, tmp_path) == "src/class_registry/base.py"

    def test_rejects_a_path_outside_the_repo(self, tmp_path: Path) -> None:
        """Answering "nothing binds this" for a file we cannot even see is a false negative."""
        with pytest.raises(SystemExit, match="is outside"):
            relative_to_repo("/etc/hosts", tmp_path)


class TestScopeMatches:
    """Unit tests for `scope_matches()`."""

    def test_matches_the_file_itself(self) -> None:
        """An entry naming one file covers that file."""
        assert scope_matches("scripts/versions.py", "scripts/versions.py")

    def test_matches_anything_beneath_a_directory(self) -> None:
        """A trailing slash is what makes an entry cover a subtree rather than one path."""
        assert scope_matches("scripts/", "scripts/ci/versions.py")

    def test_does_not_match_a_sibling_sharing_a_prefix(self) -> None:
        """`scripts/` must not reach `scripts-old/`, which shares its opening characters."""
        assert not scope_matches("scripts/", "scripts-old/versions.py")

    def test_opens_a_subtree_only_for_an_entry_ending_in_a_slash(self) -> None:
        """Bare string prefixing would let `scripts` swallow `scripts-old/`; the slash is the guard."""
        assert not scope_matches("scripts", "scripts-old/versions.py")

    def test_does_not_match_an_unrelated_path(self) -> None:
        """The common case: most decisions bind nothing the file in hand touches."""
        assert not scope_matches("scripts/", "docs/adr/001-first.md")


class TestCell:
    """Unit tests for `cell()`."""

    def test_joins_a_list_with_commas(self) -> None:
        """A scope naming several paths renders as one comma-separated cell."""
        assert cell(["scripts/", "pyproject.toml"]) == "scripts/, pyproject.toml"

    def test_escapes_pipes_in_a_scalar(self) -> None:
        """An unescaped pipe would silently split the row into extra columns."""
        assert cell("Use mypy | not ty") == "Use mypy \\| not ty"

    def test_escapes_pipes_inside_a_list(self) -> None:
        """Escaping happens after joining, so a pipe in one item is caught too."""
        assert cell(["a|b", "c"]) == "a\\|b, c"


class TestGenerate:
    """Integration tests: the index file `generate()` writes for a directory that validates."""

    def test_writes_a_row_for_each_accepted_adr(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """Two ADRs prove the loop covers the directory rather than stopping at the first."""
        write(adr_dir, "001-first.md", adr(title="1: Do the thing"))
        write(adr_dir, "002-second.md", adr(title="2: Do another thing"))
        assert generate(adr_dir, repo_root) == 0
        assert index_text(adr_dir) == (
            f"{INDEX_HEADER}\n{TABLE_HEADER}"
            f"| [001](001-first.md) | Accepted | Do the thing | {SCOPED_FILE} | A summary. |  |\n"
            f"| [002](002-second.md) | Accepted | Do another thing | {SCOPED_FILE} | A summary. |  |\n"
        )

    @pytest.mark.parametrize("status", HIDDEN_STATUSES)
    def test_excludes_hidden_statuses_but_keeps_their_neighbours(
        self, status: str, adr_dir: Path, repo_root: Path
    ) -> None:
        """A hidden ADR leaves the index while an accepted sibling stays in it."""
        write(adr_dir, "001-first.md", adr())
        write(
            adr_dir,
            "002-hidden.md",
            adr(status=status, fields={STATUS_FIELDS[status]: 12}),
        )
        assert generate(adr_dir, repo_root) == 0
        assert "002-hidden.md" not in index_text(adr_dir)
        assert "001-first.md" in index_text(adr_dir)

    def test_orders_rows_by_file_number(self, adr_dir: Path, repo_root: Path) -> None:
        """Zero-padded numbers sort as strings, so 009 must precede 010."""
        write(adr_dir, "010-later.md", adr())
        write(adr_dir, "009-earlier.md", adr())
        generate(adr_dir, repo_root)
        rows = [
            line for line in index_text(adr_dir).splitlines() if line.startswith("| [")
        ]
        assert [row.split("]")[0] for row in rows] == ["| [009", "| [010"]

    def test_ignores_the_index_and_dot_files(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """The index must not list itself, and tooling debris is not a misfiled document."""
        write(adr_dir, "001-first.md", adr())
        write(adr_dir, ADR_INDEX_FILENAME, "untouched\n")
        write(adr_dir, ".DS_Store", "")
        assert generate(adr_dir, repo_root) == 0
        assert "001-first.md" in index_text(adr_dir)

    def test_says_so_when_there_are_no_adrs(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """An empty table reads as a truncated file, so the empty state is spelt out."""
        assert generate(adr_dir, repo_root) == 0
        assert index_text(adr_dir) == f"{INDEX_HEADER}\n{EMPTY_NOTE}"

    def test_carries_a_revisit_trigger_into_its_own_column(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """The index is where a trigger reaches someone who never opens the ADR."""
        write(adr_dir, "001-first.md", adr(fields={REVISIT_WHEN_FIELD: TRIGGER}))
        generate(adr_dir, repo_root)
        assert f"| {TRIGGER} |" in index_text(adr_dir)

    def test_omits_a_discharged_trigger_from_its_column(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """A spent condition stops costing context, there being nothing left to act on."""
        fields = {REVISIT_WHEN_FIELD: TRIGGER, REVISIT_DISCHARGED_BY_FIELD: 12}
        write(adr_dir, "001-first.md", adr(fields=fields))
        generate(adr_dir, repo_root)
        assert TRIGGER not in index_text(adr_dir)

    def test_leaves_the_scope_cell_empty_for_a_decision_binding_no_path(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """An empty cell is a statement — nothing you edit will surface this decision."""
        write(adr_dir, "001-first.md", adr(fields={SCOPE_FIELD: "[]"}))
        generate(adr_dir, repo_root)
        assert "| Do the thing |  | A summary. |  |" in index_text(adr_dir)

    def test_is_idempotent(self, adr_dir: Path, repo_root: Path) -> None:
        """The CI check diffs this file, so a second run must reproduce it exactly."""
        write(adr_dir, "001-first.md", adr())
        generate(adr_dir, repo_root)
        first = index_text(adr_dir)
        generate(adr_dir, repo_root)
        assert index_text(adr_dir) == first

    def test_rejects_a_file_that_is_not_an_adr(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The directory holds ADRs and the index only; anything else is misfiled."""
        write(adr_dir, "001-first.md", adr())
        write(adr_dir, "notes.md", "# Notes\n")
        write(adr_dir, ADR_INDEX_FILENAME, "untouched\n")
        assert generate(adr_dir, repo_root) == 1
        assert (
            f"notes.md is neither an ADR nor {ADR_INDEX_FILENAME}"
            in capsys.readouterr().err
        )
        assert index_text(adr_dir) == "untouched\n"

    def test_reports_every_bad_file(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Two broken ADRs produce two errors, so one fix does not reveal the next."""
        write(adr_dir, "001-bad.md", adr(status="Draft"))
        write(adr_dir, "002-bad.md", adr(status="Nope"))
        assert generate(adr_dir, repo_root) == 1
        err = capsys.readouterr().err
        assert "001-bad.md" in err
        assert "002-bad.md" in err

    def test_rejects_a_scope_naming_something_that_is_gone(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A path that moved must fail here rather than rot unnoticed in the index."""
        write(adr_dir, "001-first.md", adr(fields={SCOPE_FIELD: "[scripts/gone.py]"}))
        assert generate(adr_dir, repo_root) == 1
        assert (
            "scopes `scripts/gone.py`, which nothing matches" in capsys.readouterr().err
        )

    def test_checks_the_scope_of_an_archived_adr(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Archived means out of the index, not out of force; its paths rot the same way."""
        fields = {"archived-because": "A comment.", SCOPE_FIELD: "[scripts/gone.py]"}
        write(adr_dir, "001-first.md", adr(status="Archived", fields=fields))
        assert generate(adr_dir, repo_root) == 1
        assert "scopes `scripts/gone.py`" in capsys.readouterr().err

    def test_leaves_the_scope_of_a_superseded_adr_unchecked(
        self, adr_dir: Path, repo_root: Path
    ) -> None:
        """Editing a superseded ADR is forbidden, so checking one could only deadlock the build."""
        fields = {"superseded-by": 12, SCOPE_FIELD: "[scripts/gone.py]"}
        write(adr_dir, "001-superseded.md", adr(status="Superseded", fields=fields))
        assert generate(adr_dir, repo_root) == 0


class TestReportScopedTo:
    """Integration tests: the `--for` lookup from a path back to the decisions binding it."""

    def test_warns_that_an_unreadable_adr_binds_nothing(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """This is the only place the lookup speaks, so a silent gap reads as "nothing binds it"."""
        write(adr_dir, "001-bad.md", adr(status="Draft"))
        report_scoped_to(["scripts/versions.py"], adr_dir, repo_root)
        assert (
            "001-bad.md could not be read, so it binds nothing here"
            in capsys.readouterr().err
        )

    def test_names_the_decision_binding_the_path(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The question a code author holds: what binds the file in front of me?"""
        (repo_root / "scripts").mkdir()
        (repo_root / "scripts" / "versions.py").write_text("", encoding="utf-8")
        write(adr_dir, "001-first.md", adr(fields={SCOPE_FIELD: "[scripts/]"}))
        assert report_scoped_to(["scripts/versions.py"], adr_dir, repo_root) == 0
        assert (
            capsys.readouterr().out
            == "001 (Accepted): Do the thing — docs/adr/001-first.md\n"
        )

    def test_stays_silent_for_a_path_nothing_binds(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Most files are bound by nothing, so the common case must not cry wolf."""
        write(adr_dir, "001-first.md", adr())
        report_scoped_to(["docs/unrelated.md"], adr_dir, repo_root)
        assert capsys.readouterr().out == ""

    def test_omits_a_superseded_decision(
        self, adr_dir: Path, repo_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A replaced decision binds nothing, so surfacing it would be noise."""
        (repo_root / "scripts").mkdir()
        (repo_root / "scripts" / "versions.py").write_text("", encoding="utf-8")
        fields = {"superseded-by": 12, SCOPE_FIELD: "[scripts/]"}
        write(adr_dir, "001-superseded.md", adr(status="Superseded", fields=fields))
        report_scoped_to(["scripts/versions.py"], adr_dir, repo_root)
        assert capsys.readouterr().out == ""


class TestMain:
    """Unit tests for `main()`: which mode each invocation selects."""

    def test_rejects_for_with_no_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """`--for` with nothing after it would otherwise report against an empty set."""
        assert main(["--for"], tmp_path, tmp_path) == 1
        assert "--for needs at least one path" in capsys.readouterr().err

    def test_rejects_an_unrecognised_argument(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A typo must fail rather than silently regenerating the index instead."""
        assert main(["--wat"], tmp_path, tmp_path) == 1
        assert "unrecognised arguments" in capsys.readouterr().err
