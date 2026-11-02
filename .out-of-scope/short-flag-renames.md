# Short flag renames

The fork does not rename or unify short command-line flags across papis commands.

## Why this is out of scope

The same short flag means different things in different commands:

| Flag | Meanings |
|---|---|
| `-n` | `--notes` in `list`, `edit` and `rm`; `--rename` in `tag` and `update` |
| `-f` | `--file` in `list`; `--format` in `export`; `--force` in `rm` |
| `-d` | `--dir` in `list`; `--drop` in `update`; `--subfolder` in `add` |
| `-p` | `--append` in `update`, `tag` and `export`; `--pick-subfolder` in `add` |

This is confusing, especially for agents that infer one command's flags from another's. But every one of these flags is part of the public interface used in shell history, scripts, and editor integrations such as papis.el and papis.nvim. Renaming any of them breaks those users silently or with confusing errors, and the cost lands on people who never asked for the change.

The long flags are unambiguous and stable. Agents and scripts should always use long flags, and agent-facing documentation should say so. That solves the problem without breaking anyone.

## Prior requests

- Raised during the initial agent-friendliness review of papis 0.16.1 (no issue opened).
