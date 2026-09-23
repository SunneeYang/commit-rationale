# Commit Rationale v0.1.0

Keep the why in Git. Commit Rationale is a native plugin for Codex and Claude Code that helps preserve important constraints and decisions in commit messages, then revisit them during maintenance.

## What it does

- Keeps useful context that code and diffs cannot reconstruct; omits redundant bodies when a subject is enough.
- Rebuilds explanations around the final changes for merge, squash, and amend.
- Adds a session reminder to read relevant commit messages and check whether historical constraints still apply.

For example, a cache changed from 30 to 15 minutes may be a temporary incident response or a lasting customer limit. The saved reason and recovery conditions help the next session distinguish those situations.

## Install

**Codex — run in your terminal:**

```bash
codex plugin marketplace add SunneeYang/commit-rationale
codex plugin add commit-rationale@commit-rationale
```

Open `/hooks`, review and trust the `SessionStart` hook, then start a new task.

**Claude Code — send these separately:**

```text
/plugin marketplace add SunneeYang/commit-rationale
```

```text
/plugin install commit-rationale@commit-rationale
```

Choose User scope, complete the host's plugin review, and start a new session.

## Documentation and scope

[English guide](https://github.com/SunneeYang/commit-rationale/blob/v0.1.0/README.en.md) · [中文说明](https://github.com/SunneeYang/commit-rationale/blob/v0.1.0/README.md) · [MIT License](https://github.com/SunneeYang/commit-rationale/blob/v0.1.0/LICENSE)

The documentation includes recorded Codex examples from synthetic repositories with the rules explicitly loaded. These show how preserved context affects later decisions; they do not measure native plugin activation rates or production outcomes. English examples translate the original Chinese outputs. The shell hook targets macOS/Linux; Windows has not been verified.

---

首个公开版本提供 Codex / Claude Code 原生插件、完整中英文使用说明及 MIT 授权。提交时保留有价值的背景，后续维护时按需读回；没有额外信息时只写标题。

欢迎分享真实项目中的使用反馈：哪些背景值得保留、哪些正文仍然多余，以及后来是否确实用到了这些记录。
