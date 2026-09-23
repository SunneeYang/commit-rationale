<h1 align="center">Commit Rationale</h1>

<p align="center">
  <strong>让提交留下原因，让维护有据可依。</strong><br />
  为 Codex 与 Claude Code 保留代码和 diff 无法还原的重要背景。
</p>

<p align="center">
  <a href="#codex"><img src="https://img.shields.io/badge/Codex-plugin-18181B?style=flat-square" alt="Codex 插件" /></a>
  <a href="#claude-code"><img src="https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square" alt="Claude Code 插件" /></a>
</p>

<p align="center">
  <a href="#快速安装">快速安装</a> ·
  <a href="#使用场景">使用场景</a> ·
  <a href="#日常使用">日常使用</a> ·
  <a href="#工作方式">工作方式</a>
</p>

---

- **写下依据** — 从任务上下文中保留重要约束、取舍和验证边界。
- **读回背景** — 在后续开发、排障和 Review 中，按需查阅完整提交说明。
- **保持简洁** — 删除改动复述和开发经过；没有额外背景时只写标题。

## 快速安装

通过所用 Agent 的原生插件系统安装，两者共用一份技能和读取提醒。

### Codex

在终端执行：

```bash
codex plugin marketplace add SunneeYang/commit-rationale
codex plugin add commit-rationale@commit-rationale
```

> [!IMPORTANT]
> 安装后在 Codex 打开 `/hooks`，审阅并信任本插件的 `SessionStart` 钩子，然后新建任务。桌面端如未显示插件，可重启应用。

### Claude Code

在 Claude Code 中分两次发送：

```text
/plugin marketplace add SunneeYang/commit-rationale
```

```text
/plugin install commit-rationale@commit-rationale
```

安装到 **User scope** 可用于该用户的所有项目。按宿主要求完成插件审阅后，新建会话。

<details>
<summary>安装前提与旧技能迁移</summary>

- Git 能够访问本仓库。
- 使用支持插件和 `SessionStart` hooks 的 Codex 或 Claude Code。
- 当前钩子使用 shell 的 `cat`，面向 macOS/Linux；Windows 环境尚未验证。
- 若之前手动安装过同名独立技能，确认插件可用后移除旧副本，避免重复发现。

</details>

## 使用场景

从一条普通提交开始，看背景如何影响下一次判断。

### 临时调整：什么时候可以恢复？

权限失效通道故障期间，缓存期限临时缩短。diff 只能看到数值变化：

```diff
-PERMISSION_TTL_MINUTES = 30
+PERMISSION_TTL_MINUTES = 15
```

客户约定和恢复条件还在任务对话里。使用技能准备提交时，这些信息被保留下来：

```text
缩短权限缓存有效期

失效通道阻塞期间临时缩短缓存期限以止损。客户撤权兜底约定为四十五分钟，原三十分钟期限仍在约定范围内。

待通道消费确认和全租户撤权回归均通过后，可恢复三十分钟。
```

后来换了一个没有原始对话的会话，你提出：

> 失效通道已经修复，消费确认和全租户撤权回归都已通过，客户约定没有变化。现在能把缓存恢复到三十分钟吗？请先评估，不修改文件。

两次实际回答的首段放在一起看：

| 能读到正文 | 历史中只剩标题 |
| --- | --- |
| 可以恢复到三十分钟，依据当前仓库历史及你已确认的回归结果，恢复条件已经满足。 | **有条件可行，但当前仓库不足以支持直接恢复到三十分钟。** 你确认的失效修复和回归通过解决了相关技术问题；仍需确认客户约定是否允许三十分钟的兜底过期时间。 |

正文让维护者找到了“为什么临时缩短”和“什么条件下可以恢复”。上线配置和端到端时限仍需核对，但无需重新追问客户允许的期限。

<details>
<summary>同样的 diff，为什么也可能不能恢复？</summary>

在另一个场景中，十五分钟是持续有效的客户撤权上限，推送恢复也不豁免。正文保留这一约束后，Agent 明确建议维持十五分钟，除非先变更约定或提供满足上限的新机制。

</details>

### 发布前提：哪个区域还不能上线？

代码改为在数据库唯一键冲突时返回已有记录。它能说明实现方式，却不能说明生产环境的索引是否已经部署。任务中收到的运维回执和验证范围被写入提交。

<details>
<summary>查看提交说明与不同发布建议</summary>

```text
处理重复创建冲突

重复创建的冲突处理依赖生产唯一索引。运维回执仅确认东区所有分片 READY；西区迁移工单仍在排队、尚未执行。代码可先合入，西区上线须等待当地索引就绪。

据此前任务记录，本地单测已通过；预发布跨区域验收尚未进行。
```

后来你提出：

> 预发布的两区域并发验收已经通过，生产迁移状态没有变化。现在可以同时发布东区和西区吗？请给出建议，不执行发布。

下面是不同历史信息下，Agent 实际建议的摘要：

| 历史中能找到的信息 | 后续建议 |
| --- | --- |
| 只有“处理重复创建冲突”的标题 | 依据不足，需要重新核实生产两区的约束和迁移状态。 |
| 正文记录东区已 READY，西区尚未迁移 | 东区可先发布；西区仍须等待生产索引就绪。预发布验收不能替代生产迁移。 |
| 正文记录两区索引均已 READY，当时只差预发布验收 | 结合这次验收通过的新信息，已知门槛满足，可以按发布流程安排两区上线。 |

留下背景既能指出具体阻塞，也能在条件满足后继续推进。历史中的“尚未验收”会结合新结果更新判断，不会成为永久限制。

</details>

### 没有额外背景：只写标题

如果改动只是修正日志拼写：

```diff
-logger.info("Cache udpated")
+logger.info("Cache updated")
```

即使对话提到“联调发现、讨论两轮、花了五分钟”，这些经过也没有额外维护价值。生成的提交说明只有：

```text
修正缓存更新日志拼写
```

如果原因已经随本次 diff 写进项目文档，也无需再复制一份到正文。在对应示例中，提交只保留标题，后续 Agent 仍能从文档找到十五分钟的约束并作出判断。

<details>
<summary>示例来源与复现</summary>

以上提交正文和维护回答来自 Codex 在合成仓库加载本插件规则后的实际输出；发布建议表为回答摘要。“只有标题”的对照主动移除了同一提交的正文，用于展示信息丢失的影响，不表示未安装插件就一定只写标题。

[完整生成记录](benchmarks/handoffs-2026-09-23-regraded.json) · [场景构造与复现说明](benchmarks/handoffs.md)

</details>

## 日常使用

安装后，直接向 Agent 提出请求即可：

| 你想做什么 | 可以这样说 |
| --- | --- |
| 准备提交说明 | `根据未提交改动生成提交信息` |
| 执行提交 | `提交` |
| 评估后续改动 | `这个期限还能延长吗？先评估，不修改文件。` |

提交相关请求由 Agent 按任务匹配技能；维护请求由读取提醒引导其按需查阅相关历史。仅请求说明时返回草稿；实际提交、改写历史、合并或推送仍遵循已有授权与仓库规则。

<details>
<summary>如何明确指定使用这个技能？</summary>

在 Codex 输入 `$` 并选择插件内的 `commit-rationale` 技能；在 Claude Code 使用：

```text
/commit-rationale:commit-rationale 根据未提交改动生成提交信息
```

</details>

## 工作方式

**当前任务上下文 → 筛选提交正文 → 后续按需读取 → 结合现状判断**

| 组成 | 作用 |
| --- | --- |
| [提交技能](plugins/commit-rationale/skills/commit-rationale/SKILL.md) | 决定哪些背景值得保留；merge、squash、amend 时根据最终改动重新组织说明。 |
| [读取提醒](plugins/commit-rationale/context/read-commit-history.md) | 提醒 Agent 读取相关提交的完整说明，核实历史约束是否仍适用。 |
| [启动钩子](plugins/commit-rationale/hooks/hooks.json) | 在会话启动、恢复、清空及压缩后注入读取提醒。 |

<details>
<summary>钩子会修改全局配置或自动查询所有历史吗？</summary>

不会。钩子只读取插件内的静态提醒并输出到会话上下文，不执行 Git 查询或修改全局 `AGENTS.md`。Agent 再根据任务决定是否查询相关历史，不会预先加载所有提交，也不保证每次任务都会读取历史。

安装插件本身不等于已信任钩子；未信任时仍可使用提交技能，但不会注入读取提醒。

</details>

技能和读取提醒各维护一份，Codex 与 Claude Code 只保留各自必要的市场清单和插件元数据。

---

[查看场景与记录](benchmarks/handoffs.md) · [报告问题](https://github.com/SunneeYang/commit-rationale/issues)
