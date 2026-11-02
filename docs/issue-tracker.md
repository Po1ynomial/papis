# Issue tracker

Tracker configuration for the fork, as expected by the triage skill.

## Tracker

- Issues and PRs live on GitHub in [Po1ynomial/papis](https://github.com/Po1ynomial/papis). Use `gh` with `-R Po1ynomial/papis`.
- A bare `#N` refers to the fork. Upstream references are written in full, e.g. `papis/papis#236`.
- There are no external PRs: every PR comes from the maintainer or an agent session. Triage covers issues only.

## Label mapping

Every triaged issue carries exactly one category label and one state label.

| Role | Label | Meaning |
|---|---|---|
| category | `bug` | Something is broken |
| category | `enhancement` | New feature or improvement |
| state | `needs-triage` | Waiting for evaluation or a grilling session |
| state | `needs-info` | Waiting on the reporter (rare: reporter and maintainer are the same person) |
| state | `ready-for-agent` | Fully specified; an agent brief is posted as a comment |
| state | `ready-for-human` | Specified, but needs human judgment or access to implement |
| state | `wontfix` | Will not be actioned |

Orthogonal labels:

| Label | Meaning |
|---|---|
| `upstream: candidate` | May be proposed upstream (default for new issues) |
| `upstream: pr-open` | An upstream PR is open |
| `upstream: merged` | Merged upstream |
| `upstream: fork-only` | Will stay in the fork |
| `theme: agent` | Makes papis easier to drive from agents and scripts |
| `tracking` | Tracking issue with a checklist; excluded from triage |
