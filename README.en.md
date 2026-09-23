<h1 align="center">Commit Rationale</h1>

<p align="center">
  <strong>Keep the why in Git.</strong><br />
  Preserve the constraints and decisions that code and diffs cannot explain, for Codex and Claude Code.
</p>

<p align="center">
  <a href="#codex"><img src="https://img.shields.io/badge/Codex-plugin-18181B?style=flat-square" alt="Codex plugin" /></a>
  <a href="#claude-code"><img src="https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square" alt="Claude Code plugin" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2563EB?style=flat-square" alt="MIT License" /></a>
</p>

<p align="center">
  English · <a href="README.md">简体中文</a>
</p>

<p align="center">
  <a href="#quick-install">Quick install</a> ·
  <a href="#scenarios">Scenarios</a> ·
  <a href="#everyday-use">Everyday use</a> ·
  <a href="#how-it-works">How it works</a>
</p>

---

- **Record the rationale** — Keep important constraints, tradeoffs, and verification limits from the task context.
- **Recover the context** — Consult full commit messages when they help with later development, debugging, or review.
- **Keep it concise** — Omit diff summaries and development diaries. When there is no useful extra context, write only a subject.

## Quick install

Install through your agent's native plugin system. Both hosts share the same skill and history-reading reminder.

### Codex

Run in your terminal:

```bash
codex plugin marketplace add SunneeYang/commit-rationale
codex plugin add commit-rationale@commit-rationale
```

> [!IMPORTANT]
> After installing, open `/hooks` in Codex, review and trust this plugin's `SessionStart` hook, then start a new task. If the plugin does not appear in the desktop app, restart the app.

### Claude Code

Send these as two separate commands in Claude Code:

```text
/plugin marketplace add SunneeYang/commit-rationale
```

```text
/plugin install commit-rationale@commit-rationale
```

Choose **User scope** to make the plugin available across your projects. Complete any plugin review required by the host, then start a new session.

<details>
<summary>Requirements and migration from a standalone skill</summary>

- Git must be able to access this repository.
- Your Codex or Claude Code version must support plugins and `SessionStart` hooks.
- The hook uses the shell command `cat` and targets macOS/Linux. Windows has not been verified.
- If you previously installed a standalone skill with the same name, remove that older copy once the plugin is working to avoid duplicate discovery.

</details>

## Scenarios

Start with an ordinary commit and see how its context changes the next decision. The examples below translate recorded Chinese outputs into English.

### A temporary change: when can we revert it?

While the permission-invalidation channel is broken, the cache lifetime is temporarily shortened. The diff only shows the numbers:

```diff
-PERMISSION_TTL_MINUTES = 30
+PERMISSION_TTL_MINUTES = 15
```

The customer agreement and recovery conditions are still in the task conversation. When preparing the commit with the skill, the agent preserves them:

```text
Shorten the permission cache lifetime

Temporarily shorten the cache lifetime to limit the impact of the blocked invalidation channel. The customer's fallback revocation limit is forty-five minutes, so the original thirty-minute lifetime is still within the agreement.

Restore thirty minutes once channel-consumption acknowledgments and revocation regression checks across all tenants have passed.
```

Later, in a new session without the original conversation, you ask:

> The invalidation channel is fixed, consumption acknowledgments and revocation regression checks across all tenants have passed, and the customer agreement has not changed. Can we restore the cache to thirty minutes now? Assess this first; do not modify files.

Here are the opening paragraphs from the two recorded answers:

| Commit body available | Only the subject remains |
| --- | --- |
| Yes, the cache can return to thirty minutes. The repository history and the regression results you confirmed show that the recovery conditions have been met. | **Conditionally feasible, but the current repository does not provide enough evidence to restore thirty minutes directly.** The fix and passing regression checks address the technical issues; we still need to confirm whether the customer agreement permits a thirty-minute fallback expiry. |

The body explains why the lifetime was shortened and when it can be restored. Deployment configuration and end-to-end timing still need checking, but the maintainer no longer needs to ask again about the customer's agreed limit.

<details>
<summary>Why might the same diff need a different answer?</summary>

In another scenario, fifteen minutes is an ongoing customer revocation limit, even after push invalidation recovers. With that constraint preserved in the body, the agent recommends keeping fifteen minutes unless the agreement changes or a new mechanism satisfies the limit.

</details>

### A release prerequisite: which region must wait?

The code now returns the existing record on a database unique-key conflict. That explains the implementation, but does not tell us whether the production index has been deployed. The commit records the operations team's migration confirmation and the scope of verification from the task.

<details>
<summary>See the commit message and release recommendations</summary>

```text
Handle duplicate-create conflicts

Conflict handling depends on a production unique index. Operations has confirmed READY status for all shards in the east region only; the west region's migration is still queued and has not run. The code can be merged now, but deployment to the west region must wait for its index to be ready.

According to earlier task records, local unit tests passed; cross-region acceptance testing in staging has not yet run.
```

Later, you ask:

> Concurrent acceptance tests across both regions have passed in staging. Production migration status has not changed. Can we release to the east and west regions together? Give a recommendation; do not deploy.

The recorded recommendations differ according to the history available:

| Information available in history | Recommendation |
| --- | --- |
| Only the subject, “Handle duplicate-create conflicts” | Insufficient evidence. Recheck production constraints and migration status in both regions. |
| The body records the east region as READY and the west region as not yet migrated | Release to the east region first; the west region must still wait for its production index. Staging acceptance does not replace production migration. |
| The body records both regions' indexes as READY, with only staging acceptance outstanding at the time | With the new passing acceptance results, the known prerequisites are met. Both regions can proceed through the release process. |

Recorded context identifies specific blockers and lets work proceed once they are resolved. A historical “not yet tested” is reassessed against new results, rather than becoming a permanent restriction.

</details>

### No extra context: a subject is enough

If the change only fixes a typo in a log message:

```diff
-logger.info("Cache udpated")
+logger.info("Cache updated")
```

Details such as “found during integration,” “discussed twice,” or “took five minutes” add no maintenance value. The generated commit message contains only:

```text
Fix typo in cache-update log message
```

If the reason is already added to project documentation in the same diff, it does not need copying into the commit body. In the corresponding example, the commit has only a subject, and the next agent still finds the fifteen-minute constraint in the documentation.

<details>
<summary>Where the examples come from and how to reproduce them</summary>

The commit messages and maintenance answers come from recorded Codex runs in synthetic repositories with this plugin's guidance loaded. The English examples are translations of those Chinese outputs, not additional English-language runs; the release recommendation table summarizes the answers. The “subject only” comparison deliberately removes the body from the same commit to show the effect of losing that information. It does not imply that agents without the plugin always omit commit bodies.

[Full generation records](benchmarks/handoffs-2026-09-23-regraded.json) · [Scenario setup and reproduction](benchmarks/handoffs.md)

</details>

## Everyday use

After installing, ask your agent directly:

| What you want | Example request |
| --- | --- |
| Draft a commit message | `Generate a commit message from the uncommitted changes.` |
| Create a commit | `Commit.` |
| Assess a later change | `Can we extend this timeout? Assess it first; do not modify files.` |

For commit tasks, the agent matches the skill to the request. For maintenance tasks, the reading reminder guides it to consult relevant history when useful. Asking only for a message produces a draft; creating commits, rewriting history, merging, or pushing still follows existing authorization and repository rules.

<details>
<summary>How do I explicitly invoke the skill?</summary>

In Codex, type `$` and select the plugin's `commit-rationale` skill. In Claude Code, use:

```text
/commit-rationale:commit-rationale Generate a commit message from the uncommitted changes.
```

</details>

## How it works

**Current task context → Select useful commit context → Read it when needed → Reassess against the current state**

| Component | Purpose |
| --- | --- |
| [Commit skill](plugins/commit-rationale/skills/commit-rationale/SKILL.md) | Selects context worth preserving; regenerates the explanation for the final changes during merge, squash, and amend. |
| [History-reading reminder](plugins/commit-rationale/context/read-commit-history.md) | Prompts the agent to read full messages for relevant commits and check whether historical constraints still apply. |
| [Session hook](plugins/commit-rationale/hooks/hooks.json) | Injects the reading reminder when a session starts, resumes, is cleared, or is compacted. |

<details>
<summary>Does the hook change global configuration or read all history automatically?</summary>

No. The hook reads a static reminder bundled with the plugin and prints it into the session context. It does not run Git queries or modify the global `AGENTS.md`. The agent decides whether to inspect relevant history for the task; it does not preload all commits, and reading history is not guaranteed for every task.

Installing the plugin does not automatically trust its hook. Without hook trust, the commit skill is still available, but the reading reminder is not injected.

</details>

The skill and reading reminder each have one shared source. Codex and Claude Code keep only their required marketplace entries and plugin metadata separately.

---

[Scenarios and records](benchmarks/handoffs.md) · [Report an issue](https://github.com/SunneeYang/commit-rationale/issues) · [MIT License](LICENSE)
