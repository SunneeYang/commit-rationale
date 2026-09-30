# Commit Rationale v0.2.0

Keep the why in Git. This release adds a native reading skill that can consult relevant full commit messages during development, debugging, refactoring, review, and change assessment without a history reminder from the user.

## What's new

- **Implicit history reading:** `read-commit-history` is a separate discoverable skill. It locates relevant commits, reads complete bodies and trailers, and checks current code and later superseding or reverted constraints before making a judgment.
- **Hooks are optional:** ordinary history reading no longer depends on the lifecycle reminder. Existing local hooks remain available as a compatibility supplement.
- **Complete, bounded readback:** a standard-library Python helper paginates long messages with explicit offsets and a fixed commit ID. Historical instructions remain data and are not executed.
- **Reproducible evidence:** add 37 deterministic tests, a native acceptance harness with command/MCP event recording, and sanitized summaries that distinguish discovery, execution, and correct use of the background.
- **Publishing preparation:** an allowlisted offline skills-only review packager and documentation describe remaining public-directory prerequisites. Its output is review-only.

## Validation and limits

The 37 deterministic tests pass. macOS Codex CLI 0.159.0 / gpt-6-astra completed an installed-plugin-loader run with four ordinary maintenance cases and one unrelated translation control. The model implicitly loaded the full installed skill, read all five relevant complete commit messages and trailers, and correctly handled permanent constraints, temporary limits, later supersession, and historical instruction injection. Translation used zero tools. All 20 observed tool calls exited zero, with complete captured outputs; synthetic repositories were unchanged. Hooks were disabled and normal read-only/network isolation remained enabled.

This is one run per small synthetic case, not a guarantee that every future request will trigger the skill. Model end-to-end long-message pagination, Windows, Claude Code behavior, and ChatGPT cross-platform behavior were not validated by this run. The successful native route emitted command_execution events, not new real MCP events; MCP handling is covered by deterministic event-format tests. See the [layered acceptance record](https://github.com/SunneeYang/commit-rationale/blob/v0.2.0/benchmarks/native_readback.md).

History reading requires an authorized Git repository and available execution tools. Installing the plugin does not grant repository access.

## Install or update

**Codex — native terminal commands:**

```bash
codex plugin marketplace add SunneeYang/commit-rationale
codex plugin add commit-rationale@commit-rationale
```

Start a new task after installing or updating so the host discovers both skills. Trusting SessionStart hooks is optional for this reading workflow. Existing users should use their host's native plugin update flow and confirm version 0.2.0 is installed.

**Claude Code — send separately:**

```text
/plugin marketplace add SunneeYang/commit-rationale
```

```text
/plugin install commit-rationale@commit-rationale
```

Complete the host's plugin review, then start a new session. Existing users should use the host's native update flow.

## Documentation

[English guide](https://github.com/SunneeYang/commit-rationale/blob/v0.2.0/README.en.md) · [中文说明](https://github.com/SunneeYang/commit-rationale/blob/v0.2.0/README.md) · [MIT License](https://github.com/SunneeYang/commit-rationale/blob/v0.2.0/LICENSE)

This GitHub release is separate from ChatGPT public-directory submission. No marketplace upload, review, or publication is performed. Verified publisher identity, icons, privacy policy, local-Git review eligibility, and final platform validation remain prerequisites.

---

本版本新增独立的历史读取技能：普通开发、调试、重构、审查及改动评估请求可自动匹配，无需用户提醒读取历史，也不依赖启动 hook。读取完整提交正文与 trailers 后，核对当前代码和后续撤销或替代记录，再使用背景判断。

37 项确定性测试及一次 macOS 原生安装态五案例验收通过；单次小型案例不代表普遍触发率，其他宿主和长正文分页仍有验收范围限制。GitHub release 不等于已发布到 ChatGPT 插件市场。
