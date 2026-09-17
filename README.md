# Commit Rationale

让 Git 提交保留代码和 diff 无法表达、且对后续维护有用的背景。

- **写入**：根据当前任务上下文筛选正文，删除改动复述和无价值的经过；没有额外背景时只写标题。
- **读取**：在开发、排障和 Review 中提醒 Agent 按需读取相关提交的完整说明，并核实历史约束是否仍适用。

通过 Codex 或 Claude Code 的原生插件系统安装。两者共用一份技能和读取提醒。

## 安装前提

- Git 能够访问本仓库；私有仓库需要相应的 GitHub 读取权限。
- 使用支持插件和 `SessionStart` hooks 的 Codex 或 Claude Code。
- 当前钩子使用 shell 的 `cat`，面向 macOS/Linux；Windows 环境尚未验证。

## Codex

在终端执行：

```bash
codex plugin marketplace add SunneeYang/commit-rationale
codex plugin add commit-rationale@commit-rationale
```

进入 Codex，打开 `/hooks`，审阅并信任本插件的 `SessionStart` 钩子，然后新建任务。桌面端如未显示插件，可重启应用。

钩子只读取插件内的静态提醒并输出到会话上下文，不执行 Git 查询或修改全局 `AGENTS.md`。安装插件本身不等于已信任钩子；未信任时仍可使用提交技能，但不会注入读取提醒。

## Claude Code

在 Claude Code 中分两次发送：

```text
/plugin marketplace add SunneeYang/commit-rationale
```

```text
/plugin install commit-rationale@commit-rationale
```

安装到 User scope 可用于该用户的所有项目。按宿主要求完成插件审阅后，新建会话。

## 使用

可以直接提出与提交相关的请求，由 Agent 根据任务匹配技能：

```text
根据未提交改动生成提交信息
```

```text
提交
```

需要明确选用时，在 Codex 输入 `$` 并选择插件内的 `commit-rationale` 技能；在 Claude Code 使用：

```text
/commit-rationale:commit-rationale 根据未提交改动生成提交信息
```

请求提交信息只生成草稿。执行提交、改写历史、合并或推送仍遵循用户授权与仓库规则。

读取提醒在会话启动、恢复、清空及压缩后注入。它提示 Agent 按需查询历史，不会预先加载所有提交，也不保证每次任务都会读取历史。

若之前手动安装过同名独立技能，确认插件可用后移除旧副本，避免重复发现。

## 内容

- [提交技能](plugins/commit-rationale/skills/commit-rationale/SKILL.md)
- [读取提醒](plugins/commit-rationale/context/read-commit-history.md)
- [启动钩子](plugins/commit-rationale/hooks/hooks.json)

技能和读取提醒各维护一份，Codex 与 Claude Code 只保留各自必要的市场清单和插件元数据。
