# AGENTS.md

This is a fork of [papis/papis](https://github.com/papis/papis), a CLI bibliography manager. The fork makes papis predictable for agents and scripts (clean stdout, meaningful exit codes, no blocking prompts, machine-readable output), with general improvements possibly following later. Progress is tracked in #8. Proposing a change upstream is optional and decided by the maintainer.

This file exists only on the `integration` branch.

## Map

| What | Where |
|---|---|
| Main checkout (your working directory) | `~/projects/_fork/papis`, always on `integration` |
| Feature worktrees | `~/projects/_worktrees/papis/<branch-slug>` (`fix/foo` → `fix-foo`) |
| Tracker config and labels | `docs/issue-tracker.md` |
| Rejected ideas | `.out-of-scope/` |
| Decisions | `docs/adr/` |
| Upstream code, test and docs conventions | `HACKING.md` |

Never switch branches in the main checkout. The maintainer's installed `papis` is an editable install from it.

## Sessions

Each session is started by the maintainer in the main checkout and does one job: implementing an issue, or triaging. Sessions may change labels and comment on issues and PRs.

For triage, follow the triage skill (`~/.pi/agent/skills/prod/triage/SKILL.md`) with `docs/issue-tracker.md` as the tracker config. For glossary terms and ADRs, use `~/.pi/agent/skills/prod/domain-modeling/SKILL.md`.

## Implementing an issue

1. Work only on `ready-for-agent` issues. The agent brief comment is the contract, and its out-of-scope list is binding. If the brief is wrong or incomplete, comment on the issue and ask the maintainer instead of guessing.
2. Create a worktree from upstream:

   ```bash
   git fetch upstream
   git worktree add --no-track -b fix/foo ~/projects/_worktrees/papis/fix-foo upstream/main
   ```

   `--no-track` keeps a plain `git push` away from upstream.
3. Implement with tests using `papis.testing`. Use Conventional Commits. Do not edit `CHANGELOG.md`.
4. Run the checks (see below), then `git push -u origin <branch>` and open a PR against `integration` whose body contains `Closes #N`. Write the body with the `pr` skill.
5. Wait for CI with `gh pr checks --watch` (about 5 minutes; the Windows jobs are the slowest). The `PyPI Release` job is skipped on the fork; that is expected.
   - All green: `gh pr merge --merge` (no `--delete-branch`; merged branches are kept for upstream). Remove the worktree with `git worktree remove`, `git pull` in the main checkout, and tick the issue in #8.
   - Anything red, or no checks reported at all: do not merge and do not work around it. Comment on the PR with what happened and report to the maintainer.
   - Never start, rerun or cancel workflows yourself (`gh workflow run`, `gh run rerun`, `gh run cancel`).

## Git rules

- `main` mirrors `upstream/main`. Never commit to it. Sync with `gh repo sync Po1ynomial/papis --branch main`.
- Feature branches start from `upstream/main`, so they can go upstream without fork-only files.
- Never rebase a branch after it was merged into `integration`, and never rebase `integration`. Follow-up fixes go in a new branch.
- Keep branches independent. If one must stack on another, its PR targets the parent branch, and the parent merges first.
- Bring in upstream changes by syncing `main`, then `git merge main` on `integration`.
- Fork-only files (`AGENTS.md`, `docs/`, `.out-of-scope/`, `GLOSSARY.md`, `pyrightconfig.json`, `typings/`, and the fork tweaks in `.github/workflows/main.yml`) are committed directly to `integration`, without an issue or PR.
- Never push to `upstream`, and never open issues or PRs on `papis/papis`.
- Push branches only. Never push tags (`--tags`, `--follow-tags`); the local tags come from upstream.

## Dev environment and checks

Set up once per worktree:

```bash
uv venv
uv pip install -e '.[develop,docs,optional]'
cp ~/projects/_fork/papis/pyrightconfig.json .
ln -s ~/projects/_fork/papis/typings typings
basedpyright --writebaseline
```

The extras match CI. With `develop` alone, pytest fails to import `papis/sphinx_ext.py` and mypy reports errors. Do not use `uv run` or `uv sync`; they create a `uv.lock`, which is not gitignored.

The last three lines set up basedpyright for the maintainer's editor: the config, stubs that make `dominate` untyped (as mypy treats it), and a baseline that hides existing errors so only new ones show. These files are listed in `.git/info/exclude` and must never be committed on a feature branch. basedpyright is not a check; mypy is the type checker of record. If old errors resurface after moving code, rerun `basedpyright --writebaseline`.

Checks, matching CI, from the worktree root:

```bash
export PATH="$PWD/.venv/bin:$PATH"
ruff check
python -m mypy
python -m pytest papis tests   # about 70 s
uvx typos --sort
```

Put the venv first on `PATH`: other `ruff` installs on the system may be a different version.

## Running papis safely

- The `papis` on `PATH` runs the `integration` code. To exercise your branch, use the worktree's `.venv/bin/papis`.
- Never touch the maintainer's real library or config. Use a sandbox:

  ```bash
  SBX=$(mktemp -d)
  export PAPIS_CONFIG_DIR="$SBX/config" XDG_CACHE_HOME="$SBX/cache"
  mkdir -p "$PAPIS_CONFIG_DIR" "$SBX/lib"
  printf '[settings]\ndefault-library = sandbox\n\n[sandbox]\ndir = %s/lib\n' "$SBX" > "$PAPIS_CONFIG_DIR/config"
  ```

- papis can block on editors, the document picker and confirmations. Run every papis call with `</dev/null` and a bash tool timeout (macOS has no `timeout` command).
- Use long flags only; short flags mean different things across commands. Prefer `--batch`, `--all`, `--force`, and target documents with `papis_id:<id>`.
- Until #1 is merged, a notice about a deprecated config folder may appear on stdout in sandboxes.

## Skills

Besides the triage and domain-modeling skills above:

- `pr`: every PR body.
- `kitty-use`: reproducing picker and other TUI behavior in a real terminal.
- `diagnosing-bugs`: hard bugs.
- `python`: any Python work.
