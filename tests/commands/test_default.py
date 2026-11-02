from __future__ import annotations

import os
import shutil

import platformdirs
import pytest

from papis.testing import PapisRunner, TemporaryConfiguration, TemporaryLibrary


@pytest.mark.parametrize("with_library", [False, True])
def test_no_config_shows_init_hint(tmp_config: TemporaryConfiguration,
                                   monkeypatch: pytest.MonkeyPatch,
                                   with_library: bool) -> None:
    import papis.config
    from papis.commands.default import run as cli

    with monkeypatch.context() as m:
        # NOTE: this is the default directory set in
        #   papis.config::Configuration.__init__
        # See https://github.com/papis/papis/issues/1227
        m.setattr(platformdirs, "user_documents_dir",
                  lambda: os.path.join(tmp_config.tmpdir, "Documents"))
        libdir = os.path.join(platformdirs.user_documents_dir(), "papers")

        if with_library:
            os.makedirs(libdir)
        else:
            assert not os.path.isdir(libdir)

        shutil.rmtree(tmp_config.configdir)
        papis.config.reset_configuration()

        cli_runner = PapisRunner()
        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No configuration file exists at" in result.output
        assert "papis init" in result.output

        if with_library:
            os.rmdir(libdir)


def test_default_cli(tmp_library: TemporaryLibrary) -> None:
    from papis import __version__
    from papis.commands.default import run as cli

    cli_runner = PapisRunner()
    result = cli_runner.invoke(
        cli,
        ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output

    result = cli_runner.invoke(
        cli,
        ["--set", "something", "42"])
    # error missing command
    assert result.exit_code == 2


def test_debug_goes_to_stderr(capsys: pytest.CaptureFixture[str],
                              monkeypatch: pytest.MonkeyPatch) -> None:
    from papis.commands import debug

    with monkeypatch.context() as m:
        m.setenv("PAPIS_DEBUG", "1")
        debug("a debug message about %s", "plugins")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "a debug message about plugins" in captured.err


def test_deprecated_config_notice_stderr(
        tmp_library: TemporaryLibrary,
        monkeypatch: pytest.MonkeyPatch) -> None:
    import json

    from papis.commands.default import run as cli

    # NOTE: the deprecated folder is picked up from XDG_CONFIG_HOME, which
    # points to the fixture configuration, while PAPIS_CONFIG_DIR points to a
    # separate (existing) folder. Re-reading the configuration with --config
    # triggers the notice inside the command.
    configdir = os.path.join(tmp_library.tmpdir, "new-config")
    os.makedirs(configdir)

    cli_runner = PapisRunner()
    with monkeypatch.context() as m:
        m.setenv("PAPIS_CONFIG_DIR", configdir)

        result = cli_runner.invoke(
            cli,
            ["--config", tmp_library.configfile,
             "export", "--all", "--format", "json"])

    assert result.exit_code == 0
    assert "deprecated configuration folder" in result.stderr
    assert json.loads(result.stdout)


def test_duplicate_config_option_error(tmp_library: TemporaryLibrary) -> None:
    from papis.commands.default import run as cli

    configfile = os.path.join(tmp_library.tmpdir, "invalid-config")
    with open(configfile, "w", encoding="utf-8") as fd:
        fd.write("[settings]\ndefault-library = test\ndefault-library = test\n")

    cli_runner = PapisRunner()
    result = cli_runner.invoke(cli, ["--config", configfile, "list"])

    assert result.exit_code == 1
    assert not result.stdout
    assert "Duplicate option" in result.stderr
