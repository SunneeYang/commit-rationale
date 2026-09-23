# 发布材料

以下文案可按渠道复制使用；尚未发布帖子或提交目录申请。仓库使用 MIT 许可证。

## GitHub About

Preserve the constraints and decisions behind Git changes for Codex and Claude Code. Keep useful context in commit messages and revisit it during maintenance.

## 中文发布稿

**AI 改完代码，下一次还能找到当时的依据吗？**

我做了一个 Codex / Claude Code 插件：Commit Rationale。它在准备提交时，从任务上下文里筛选代码和 diff 无法还原的重要背景，写进提交正文；后续维护时，提醒 Agent 按需读取相关历史，再结合现状判断。没有额外背景就只写标题。

例如缓存从三十分钟降到十五分钟：diff 看得出改了多少，却看不出这是故障期间的临时措施、客户允许四十五分钟，以及什么条件下可以恢复。把这些依据留下来，新会话就能判断恢复条件是否满足，减少重新追问。README 展示了这个合成场景中实际生成的提交和后续回答，也说明了对照方式。

支持两个 Agent 的原生插件安装，MIT 开源。欢迎拿真实项目试用，尤其想听听：哪些背景值得保留，哪些正文仍然多余，以及后来是否真的用到了这些记录。

仓库与安装说明：https://github.com/SunneeYang/commit-rationale

## English announcement

**Your AI changed the code. Will the next session know why?**

I built Commit Rationale, a plugin for Codex and Claude Code. It helps preserve important constraints and decisions from task context in Git commit messages, then reminds the agent to consult relevant history during maintenance. When there is no useful context beyond the diff, a subject line is enough.

Consider a cache TTL reduced from 30 to 15 minutes. The diff does not tell you whether this is a temporary incident response, what the customer’s deadline is, or when the old value can be restored. Keeping that context gives a fresh session evidence for the next change. The README shows generated messages and follow-up answers from synthetic scenarios, with the underlying records available.

It uses each agent’s native plugin system and is MIT licensed. I’d appreciate feedback from real projects: what context was worth saving, what felt redundant, and whether a later task used it.

Repository and installation: https://github.com/SunneeYang/commit-rationale

## 约四十秒录屏脚本

**状态：脚本已准备，视频尚未录制。** 重演 [README 的临时缓存场景](../README.md#临时调整什么时候可以恢复)，只在演示仓库操作。已有输出来自合成案例、显式加载规则的测试；原生插件的录屏需实际运行，不能将旧输出冒充本次运行。

录制前安装并审阅插件和钩子。在演示仓库准备 `PERMISSION_TTL_MINUTES = 30` 的初始提交，再将它改为 `15`。向当前会话提供以下背景，最后请求“根据未提交改动生成提交信息”：

> 失效通道卡住了，先把缓存降到十五分钟止损。客户撤权兜底约定是四十五分钟，平时三十分钟没有越界。恢复条件是通道消费确认和全租户撤权回归都通过；满足后可以恢复三十分钟。

| 时间 | 画面 | 旁白或字幕 |
| --- | --- | --- |
| 0–7 秒 | 标注“合成场景演示”，展示 `30 → 15` 的 diff | “这个改动很小，但下一次恢复配置，需要知道当时为什么改。” |
| 7–16 秒 | 展示任务背景和生成的提交草稿，突出四十五分钟上限与恢复条件 | “客户约定和恢复条件留在提交正文里，代码不用承担这些历史信息。” |
| 16–25 秒 | 在演示仓库提交后，切换到同一仓库的全新会话；展示下面的维护问题 | “换一个没有原始对话的会话，现在能恢复三十分钟吗？” |
| 25–36 秒 | 展示本次实际读取历史的命令与回答，突出判断依据 | “它能结合历史约定和新的回归结果判断，而不是只看十五这个数字。” |
| 36–43 秒 | 仓库地址、Codex / Claude Code、MIT | “把有用的原因留在 Git 里。安装和更多场景见 README。” |

新会话只提供下面的问题，不粘贴原始背景或提交正文：

> 失效通道已经修复，消费确认和全租户撤权回归都已通过；客户约定自本次提交后没有变化。现在想把权限缓存从十五分钟恢复到三十分钟，以提高命中率。请根据当前仓库评估是否可行，给出依据和必要的下一步。不要改文件。

已有记录中，正文保留了“客户上限四十五分钟”和两个恢复门槛，新会话据此判断可以恢复，并指出仍需核对上线配置和端到端时限。录制时使用实际结果，可剪去等待时间；若未读取历史，应先查明原因，再决定展示内容。

来源：[用例、正文及完整回答](../benchmarks/handoffs-2026-09-23-regraded.json)，案例 `02-incident-cap`。正文有无的对照展示信息传递的作用，不代表未安装插件就一定缺少正文，也不是插件胜率。

## 收录入口备忘

规则核对于 2026-09-23，投稿前再确认。对外材料以仓库链接、安装方式和具体使用场景为主。

| 入口 | 规则与下一步 |
| --- | --- |
| [Claude Code 官方目录](https://github.com/anthropics/claude-plugins-official#external-plugins) | 通过[官方表单](https://clau.de/plugin-directory-submission)申请，需审核。 |
| [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code/blob/main/CONTRIBUTING.md) | 首次提交满十四天且后续活跃，或已有一百 stars。本仓库首提交为 2026-09-16，尚未满足时间门槛。由作者本人使用网页 Issue 表单；不提交推荐 PR，也不让 Agent 或 `gh` 代投。 |
| [OpenAI 插件提交说明](https://developers.openai.com/plugins/guides/submit-claude-plugin) | [提交门户](https://platform.openai.com/plugins)要求 Apps Management 写权限、身份验证和审核；先确认本插件的本地 Git、shell hook 依赖是否适用于目标产品及审核路径。 |

首次分享可选 V2EX「分享创造」或一个相关开发者社区，先读所在板块的自推广规则，收集真实使用反馈后再扩展渠道。
