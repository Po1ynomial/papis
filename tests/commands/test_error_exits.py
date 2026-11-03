from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from papis.testing import PapisRunner

if TYPE_CHECKING:
    from click.testing import Result

    from papis.testing import TemporaryLibrary


def _invoke(*args: str) -> Result:
    from papis.commands.default import run

    return PapisRunner().invoke(run, list(args))


def _assert_error(result: Result, exit_code: int, message: str) -> None:
    assert result.exit_code == exit_code
    assert not result.stdout
    assert message in result.stderr


def test_usage_errors(tmp_library: TemporaryLibrary) -> None:
    missing_template = f"{tmp_library.tmpdir}/missing.template"

    result = _invoke("export", "--all", "--format", "nosuch")
    _assert_error(result, 2, "Supported formats are:")

    result = _invoke(
        "explore", "lib", "krishnamurti", "export", "--format", "nosuch")
    _assert_error(result, 2, "Supported formats are:")

    result = _invoke("doctor", "--all", "--checks", "nosuch")
    _assert_error(result, 2, "Supported checks are:")

    result = _invoke("update", "--all", "--from", "nosuch", "unused")
    _assert_error(result, 2, "Supported importers are:")

    result = _invoke("list", "--all", "--template", missing_template)
    _assert_error(result, 2, "Template file")

    result = _invoke("config", "a.b.c")
    _assert_error(result, 2, "Options should be in a")


def test_config_without_value_exits_nonzero(tmp_library: TemporaryLibrary) -> None:
    result = _invoke("config", "nosuch.key")

    _assert_error(result, 1, "No value for setting")


def test_merge_requires_two_documents(
        tmp_library: TemporaryLibrary, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("papis.pick.pick_doc", lambda documents: documents)

    result = _invoke("merge", "krishnamurti")

    _assert_error(result, 1, "exactly two documents")


def test_addto_requires_valid_files(
        tmp_library: TemporaryLibrary, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("papis.api.pick_doc", lambda documents: documents)

    result = _invoke("addto", "--files", "/missing.pdf", "krishnamurti")

    _assert_error(result, 1, "No valid files provided")


@pytest.mark.parametrize("fails_to_load", [True, False])
def test_exporter_failure_exits_nonzero(
        tmp_library: TemporaryLibrary,
        monkeypatch: pytest.MonkeyPatch,
        fails_to_load: bool) -> None:
    from papis.plugin import PluginError

    if fails_to_load:
        def get_exporter_by_name(_name: str) -> Any:
            raise PluginError("failed to load")
    else:
        def get_exporter_by_name(_name: str) -> Any:
            def exporter(_documents: list[Any]) -> str:
                raise RuntimeError("export failed")

            return exporter

    monkeypatch.setattr("papis.exporters.get_exporter_by_name", get_exporter_by_name)

    result = _invoke("export", "--format", "bibtex", "krishnamurti")

    message = "Could not load exporter" if fails_to_load else "Failed to export"
    _assert_error(result, 1, message)


def test_bibtex_rm_exits_nonzero(tmp_library: TemporaryLibrary) -> None:
    result = _invoke("bibtex", "rm")

    _assert_error(result, 1, "not implemented")


def test_unknown_command_is_usage_error(tmp_library: TemporaryLibrary) -> None:
    result = _invoke("l" + "sit")

    _assert_error(result, 2, "Did you mean 'list'?")
