# ChatGPT / Codex 公共插件目录发布准备

核对于 **2026-09-30**。本文记录公开文档与本仓库的准备状态，不代表 OpenAI 已接受、审核或发布此插件。没有执行公共目录上传、提交、发布、发布者身份认证或外部联系。用户为本地验收完成的官方 Codex 登录不等于公共目录发布身份认证。

## 结论与产品边界

建议保留当前 GitHub 原生插件分发，同时单独构建 **skills-only 公共目录包**。两者共用提交写作、历史读取技能；公共包不携带生命周期 hooks。无需为这个工作流增加 UI 或 MCP。

当前[提交说明](https://developers.openai.com/plugins/deploy/submission#automatically-provide-submission-and-review-information)明确禁止公共 ZIP 包包含生命周期 hooks，以及 `apps` / `.app.json` 引用。已经发布的 skills-only 插件目前也不能追加 MCP；因此不要仅为将来可能需要服务器而宣称当前支持服务器功能。

[技能文档](https://learn.chatgpt.com/docs/build-skills#how-chatgpt-and-codex-use-skills)支持隐式调用：任务符合 skill description 时，ChatGPT / Codex 可以自动选择技能，无需每次手动提及。Codex 的 `allow_implicit_invocation` 默认是 `true`。这不是“每个会话启动必定执行”的保证。

本插件的读取入口是独立的 `read-commit-history` skill。它按当前开发、调试、重构或审查任务定位相关提交，读取完整正文和 trailers，再核对当前证据。公开介绍应准确说明：

- 历史读取需要当前任务有权访问的 Git 仓库，以及可用的 Git / 执行工具
- 安装插件不会授予本机文件、连接器或私有仓库访问权；权限仍由宿主与数据源管理
- 没有仓库、Git 不可用或历史不完整时说明证据缺口，不虚构历史、不自行扩大权限
- 普通 Chat 中只有提供的文本或文件时，可以处理已有内容，不能承诺访问用户电脑上的仓库

插件技能可在支持的 ChatGPT Chat / Work 网页、桌面和移动端，以及桌面 Codex、Codex CLI 中使用；具体工具能力由运行环境决定。IDE 扩展目前不支持插件，独立 skills 是另一条安装路径。参见[插件说明](https://learn.chatgpt.com/docs/plugins)与[权限边界](https://learn.chatgpt.com/docs/enterprise/skills)。

## 已具备的验收材料

macOS Codex CLI `0.159.0` / `gpt-6-astra` 的**原生安装态插件 loader**已完成一次真实端到端验收：四个普通维护任务自动从安装缓存加载完整读取技能，读完相关五条提交正文及 trailers，并正确处理长期约束、临时限制、后续替代和历史指令注入；翻译负对照零工具调用。20 次工具调用退出码均为 0，无截断，合成仓库未变。hooks 关闭，正常只读/网络隔离保持启用，未使用 bypass。

完整分层结果与限制见[原生验收记录](../benchmarks/native_readback.md)。这验证了指定 CLI、模型及小型合成场景；不保证所有请求触发，也不等于 ChatGPT 全平台、最终 portable ZIP 或市场审核已通过。长正文分页没有模型端到端记录，本轮也没有新的真实 MCP 工具事件。

测试插件已官方卸载；独立登录目录保持私有，凭据与私有目录不得进入任何源码包或公共目录 ZIP。公开包只采用下述固定白名单。发布身份、图标、隐私政策、本地能力审核路径与最终平台扫描仍未完成，因此构建结果继续标记 `review-only` / `submission_ready: false`。

## 尚未解决的公开发布事项

1. **发布身份**：尚未检查 OpenAI Platform 中的已认证个人/企业身份。源码中的 `SunneeYang` 是仓库作者名，不是认证证据；不能擅自据此填充已认证发布者。
2. **图标**：仓库尚无最终的 `logo` / `composerIcon` 发布资产。需要作者认可且有使用权的图标，不使用虚构品牌或占位图冒充完成品。
3. **隐私与公开链接**：尚未准备并核实公开隐私政策。skills-only ZIP 的链接字段校验较宽松，但总体[发布准则](https://developers.openai.com/plugins/plugin-guidelines#privacy)仍要求清楚的公开隐私政策，不能把“上传字段可省略”等同于“无需遵守隐私要求”。
4. **本地能力审核**：[迁移指南](https://developers.openai.com/plugins/guides/submit-claude-plugin#complete-the-submission-requirements)要求核心价值依赖本地执行、本机文件访问等能力的插件，在提交前联系 OpenAI partner，可能需要产品专项审核。Commit Rationale 的本地 Git 使用场景需确认适用路径。本文没有发起联系，也不保证公共目录收录资格。
5. **宿主与平台检查**：本地测试不代表 ChatGPT 全平台可用、自动触发必定成功或已通过平台扫描。正式提交前须测试最终 ZIP，并完成适用的安全检查和审核。

隐私说明应准确描述处理的仓库/提交内容、用途、接收方、留存与用户控制；只有核实后才能宣称无遥测、无外传或某种保留时限。不要将原始聊天、敏感提交内容、密钥或真实客户资料放进发布包。

## 公共包布局

新公共包采用 [Agent Plugins 根 manifest 格式](https://developers.openai.com/plugins/build/plugins#plugin-manifest)，现有本地 `.codex-plugin/plugin.json` 与 Claude manifest 保持原有用途。当前平台仍接受 Codex 兼容格式，但本构建器不把本地 manifest 直接复制进 ZIP。

```text
plugin.json
LICENSE
skills/
  commit-rationale/
    SKILL.md
    agents/openai.yaml
  read-commit-history/
    SKILL.md
    agents/openai.yaml
    scripts/read_commit.py
```

待图标准备好后再扩展白名单，并加入 `assets/` 及对应 manifest 路径。

- 根 `$schema`：`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`
- 稳定包名：`commit-rationale`，显式 semantic version
- 展示字段：`extensions.com.openai.interface`
- portable 格式自动发现根 `skills/`；无需另加 Codex 专用的 `skills` 字段
- 如果使用 portable manifest 的 `extensions.com.openai`，平台不会与 `.codex-plugin/plugin.json` 的 OpenAI 设置合并
- 本地 `hooks/`、`context/`、marketplace 配置、`.git/`、benchmark 结果及缓存均不进入公共包
- 根 `LICENSE` 复制自仓库现有 MIT 许可证，保留版权与许可文字

## 离线 review-only 构建器

在仓库根运行（Python 3.9+，仅使用标准库）：

```bash
python3 scripts/package_marketplace.py --output /tmp/commit-rationale-review.zip
python3 -m unittest discover -s tests -p 'test_package_marketplace.py' -v
```

构建器使用固定白名单，不递归打包仓库；拒绝源文件或父目录中的符号链接、缺少必需文件及覆盖已有输出。相同源内容和版本生成相同 ZIP。可用 `--version 0.2.0` 明确指定拟发布版本，该选项不修改源码版本或创建 Git tag。

输出包含：

- 指定路径的 ZIP，只有上方列出的文件
- 同名 `.preflight.json`，包含文件清单、SHA-256、版本和未完成事项

**这只是本地审阅包，不能称为 submission-ready。** 构建器有意不填写未经验证的 publisher 字段、不生成假图标，并始终输出 `submission_ready: false`。它不是官方 schema 校验器、秘密扫描器或审批系统；没有联网，也不会上传、提交或发布。新增技能资源时必须明确更新白名单与测试，不能改成打包整个仓库。

## 最终 metadata 与资产检查

依据[字段说明与提交校验](https://developers.openai.com/plugins/deploy/submission-errors)：

- `displayName`、`shortDescription` 各不超过 30 字符；`longDescription` 不超过 4000；`developerName` 不超过 80
- 用真实已认证身份补齐 `author.name` 与 `developerName`，保持一致；不假定 GitHub 昵称可作为发布身份
- 推荐分类 `Developer Tools`；基础目录文案使用英文；最多 3 条不同 starter prompts，每条不超过 128 字符
- 推荐同时提供 `logo` 与 `composerIcon`，可引用同一张已授权图像；路径使用 `./` 前缀并指向包内文件
- 图像可用 PNG/JPEG/WebP/SVG，每个不超过 5 MiB；图标须正方形且至少 48×48，建议 512×512；光栅图最长边不超过 4096
- 不必为此工作流制作自定义 UI。截图不是上架必需资产，当前准则说目录不再展示截图
- ZIP 只有一个插件根；压缩不超过 100 MB，解压不超过 512 MiB，不超过 5000 项，无符号链接或路径穿越

对提交写作与读取分别测试正常、无效和边界输入。特别覆盖：无需用户提及历史的隐式匹配；完整正文/尾部 trailers；长消息分段；后续约束更新；没有历史/浅克隆；恶意提交文字；只读任务不得引入写操作。记录实际宿主、版本、权限与结果，不将显式加载测试描述为原生隐式触发证明。

## 正式上传、审核与发布

以下步骤只在作者明确决定提交后执行。当前 [Platform Plugins](https://platform.openai.com/plugins) 使用 ZIP 上传流程；搜索摘要或旧指南可能仍显示旧的 Create plugin / Skills only 表单，请以[当前提交说明](https://developers.openai.com/plugins/deploy/submission)及实际页面为准。

1. 在正确组织/项目中完成个人或企业身份验证。组织 owner 可提交；其他成员需要 [Apps Management Write](https://platform.openai.com/settings/organization/people/roles)
2. 先确认本地 Git 核心能力的审核路径，补齐上述身份、图标、隐私与测试事项
3. 选择 **Upload new or existing plugin**，选择已验证 Developer identity，再上传最终 ZIP
4. 在 **Metadata & Skills** 检查结果；修改源码包并重新上传来修复错误。技能扫描可能需要时间，成功上传不等于满足最终提交条件
5. 选择 **Submit for review**，完成适用的政策声明，跟踪 Review status；等待审核结果
6. 获批后由作者决定发布时间，再选 **Publish plugin**。审核通过不会自动替作者公开发布
7. 后续技能、文案或资产变更使用新的完整 ZIP 和版本，再走审核/发布流程

skills-only 不需要 MCP 专属的五条正例、三条反例和演示视频，也无需部署 HTTPS MCP 或验证服务器域名。仍应保留可复现测试，接受技能扫描与收录审核。审核耗时与是否获准不能预先保证。

## 参考资料

- [公开提交与完整 manifest 字段](https://developers.openai.com/plugins/deploy/submission)
- [包结构与兼容格式](https://developers.openai.com/plugins/build/plugins)
- [校验限制](https://developers.openai.com/plugins/deploy/submission-errors)
- [发布准则、隐私和技能资格](https://developers.openai.com/plugins/plugin-guidelines)
- [技能触发及 invocation policy](https://learn.chatgpt.com/docs/build-skills)
- [Claude 插件迁移与本地能力审核](https://developers.openai.com/plugins/guides/submit-claude-plugin)
