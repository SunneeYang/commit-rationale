"""Single-commit handoffs: identical code can require opposite maintenance decisions."""

from workflow_cases import git


TTL_REQUEST = '''失效通道已经修复，消费确认和全租户撤权回归都已通过；客户约定自本次提交后没有变化。
现在想把权限缓存从十五分钟恢复到三十分钟，以提高命中率。请根据当前仓库评估是否可行，给出依据和必要的下一步。不要改文件。'''
ROLLOUT_REQUEST = '''预发布环境的两区域并发创建验收已通过，生产数据库的迁移状态自本次提交后没有变化。
现在准备同时向东区和西区发布当前版本。请根据当前仓库给出发布建议、依据和必要的下一步。不要改文件。'''
CALIBRATION = '只断言可用材料支持的外部约定、环境状态和验证结果；不能把历史回执说成本次亲验。材料不足时明确未知或提出条件，不能凭空猜中 oracle。'
NOISE = '正文不复述可从最终代码和 diff（含文档）恢复的改动，不写讨论次数、耗时等经过；为表达外部约束、恢复条件或验证范围所必需的实现名词可保留。'

CASES = [
    {
        'id': '01-contract-cap', 'pair': 'ttl', 'fixture': 'ttl', 'kind': 'context',
        'subject': '缩短权限缓存有效期',
        'context': '''用户：客户刚确认，撤权后十五分钟必须失去访问能力。这个上限也适用于推送失效通道异常时的缓存兜底，不会因为推送恢复就豁免。
助手：这次先调整缓存期限，token 不动。
用户：可以。今天的通道异常另有修复任务；日志拼写也先别混进来。''',
        'request': TTL_REQUEST,
        'oracle': '十五分钟是客户对撤权兜底的持续上限，与失效通道是否健康无关。当前请求确认客户约定未变；即使通道恢复也不能把缓存兜底放宽到三十分钟。',
        'writer_context': '保留客户撤权十五分钟上限，以及推送恢复也不豁免缓存兜底的限制。',
        'reader_context': '依据可用材料找回客户十五分钟撤权兜底约定，以及它不随推送恢复而解除的事实。仅从常量猜测不算。',
        'decision': '有材料依据地否决单独恢复三十分钟；若要提高，必须先改变客户约定或提供仍满足十五分钟兜底的新机制，不能仅以通道修复作为放行条件。',
    },
    {
        'id': '02-incident-cap', 'pair': 'ttl', 'fixture': 'ttl', 'kind': 'context',
        'subject': '缩短权限缓存有效期',
        'context': '''用户：失效通道卡住了，先把缓存降到十五分钟止损。客户撤权兜底约定其实是四十五分钟，平时三十分钟没有越界。
助手：这次先调整缓存期限，token 不动。
用户：恢复条件是通道消费确认和全租户撤权回归都通过。满足后可以恢复三十分钟；今天先处理止损，日志拼写先别混进来。''',
        'request': TTL_REQUEST,
        'oracle': '十五分钟只是失效通道故障期止损；客户兜底上限四十五分钟。恢复三十分钟的两个门槛是消费确认与全租户撤权回归通过，当前请求明确两者已通过且客户约定未变。',
        'writer_context': '保留四十五分钟客户上限、十五分钟的临时性质，以及恢复三十分钟需要消费确认和全租户撤权回归通过的条件。',
        'reader_context': '依据可用材料找回四十五分钟客户上限及十五分钟是临时止损、恢复三十分钟的两个门槛。',
        'decision': '明确已有材料满足恢复三十分钟的约定和恢复门槛，可以按正常变更流程恢复；允许补充回归或监控，不应再要求不存在的十五分钟合同豁免或无条件维持十五分钟。',
    },
    {
        'id': '03-index-pending', 'pair': 'rollout', 'fixture': 'dedupe', 'kind': 'context',
        'subject': '处理重复创建冲突',
        'context': '''用户：重复创建要返回已有记录，异常分支按我们对过的版本做。
助手：需要依赖生产唯一索引。
用户：运维回执只确认东区所有分片 READY；西区迁移工单还在排队，没有执行。代码可以先合，西区上线要等那边索引就绪。本地单测已通过，预发布的跨区域验收尚未做。
助手：日志文案也有一处旧拼写。
用户：那处留给另一项任务，这次先准备提交。''',
        'request': ROLLOUT_REQUEST,
        'oracle': '生产东区所有分片唯一索引 READY；西区迁移未执行，来自运维回执。历史只有本地单测，当前请求新增预发布跨区域验收，但明确生产迁移状态未变，因此西区仍不能上线。',
        'writer_context': '保留运维回执所述东区索引就绪、西区迁移未执行，以及西区发布前必须等待索引就绪；区分本地单测与当时未做的预发布验收。',
        'reader_context': '依据可用材料指出东区生产索引 READY、西区尚未迁移；不能用预发布验收推断生产索引已建好。',
        'decision': '否决立即同时发布两区，指出具体阻塞在西区生产索引；先完成并确认西区索引，再发布西区。可提议东区先行，而不应把两区生产迁移一概视为未知。',
    },
    {
        'id': '04-index-ready', 'pair': 'rollout', 'fixture': 'dedupe', 'kind': 'context',
        'subject': '处理重复创建冲突',
        'context': '''用户：重复创建要返回已有记录，异常分支按我们对过的版本做。
助手：需要依赖生产唯一索引。
用户：运维回执已确认东区和西区所有分片的唯一索引都是 READY，历史重复数据也已清理；迁移完成后才轮到这个版本。剩余放量门槛是预发布跨区域并发验收。本地单测已通过，那项验收尚未做。
助手：日志文案也有一处旧拼写。
用户：那处留给另一项任务，这次先准备提交。''',
        'request': ROLLOUT_REQUEST,
        'oracle': '据运维回执，生产两区所有分片唯一索引已 READY，历史重复数据已清理。历史待办是预发布跨区域验收，当前请求确认通过且生产迁移状态未变；因此已知发布门槛均满足。',
        'writer_context': '保留运维回执确认两区全部分片索引 READY、历史重复数据已清理，以及尚待预发布跨区域验收；不声称作者亲验生产或已通过该验收。',
        'reader_context': '依据可用材料区分两区生产索引已就绪与历史待做的预发布验收，并用当前请求更新后者状态。',
        'decision': '明确两区已知发布门槛现已满足，可以安排发布并正常监控；不得把历史未验收当成当前仍未验收，也不应凭空阻塞在尚未执行的生产迁移或要求重复建索引。',
    },
    {
        'id': '05-document-control', 'fixture': 'documented', 'kind': 'control',
        'subject': '缩短权限缓存有效期',
        'context': '用户：策略和对应约定说明都已暂存。本次没有另外的背景或验证记录。',
        'request': TTL_REQUEST,
        'oracle': '与合同上限案例相同的十五分钟客户兜底限制已完整写在最终 README 中，正文不是唯一信息渠道。两组都应据文档否决仅因通道修复就恢复三十分钟。',
        'writer_context': '没有额外正文价值，body 应为空字符串；不能复述本次 README 约定或编造测试。',
        'reader_context': '从 README 找到十五分钟客户兜底上限及推送恢复不豁免的条件。',
        'decision': '依据 README 否决单独恢复三十分钟，并指出需改变约定或兜底机制；不能因提交正文为空就声称缺乏约定信息。',
    },
    {
        'id': '06-no-context-control', 'fixture': 'spelling', 'kind': 'control',
        'subject': '修正缓存更新日志拼写',
        'context': '用户：联调时看到了这个拼写错误，讨论了两轮才分到我这里，改动花了五分钟。没有其他需求或验证记录。',
        'request': '这次提交会改变日志级别、输出时机或业务行为吗？能否按纯文案修正处理？请查看仓库后给出判断，不改文件。',
        'oracle': '唯一改动是日志字符串 udpated 改为 updated，不改变函数调用、级别或业务行为。没有额外背景可保留；无正文不应导致读者拒绝判断。',
        'writer_context': 'body 应为空字符串，不记录联调发现、讨论轮次和耗时，不编造验证。',
        'reader_context': '从完整 diff 确认只有日志单词拼写改变。',
        'decision': '明确可按纯文案修正处理，日志级别、输出时机与业务行为不变；不能因缺正文而强行要求补充业务动机或审批。',
    },
]


def setup_repo(case, repo, message=None):
    """Fresh object database per arm; a removed body is never reachable via reflog."""
    repo.mkdir()
    git(repo, 'init', '-q', '-b', 'main')
    readme = '# 示例服务\n\n部署平台及客户端代码不在本仓库。\n'
    if case['fixture'] in ('ttl', 'documented'):
        base = {'cache.py': 'PERMISSION_TTL_MINUTES = 30\n', 'README.md': readme}
        final = {'cache.py': 'PERMISSION_TTL_MINUTES = 15\n'}
        if case['fixture'] == 'documented':
            final['README.md'] = readme + '\n客户要求撤权最多十五分钟内生效，此约定也约束推送异常时的缓存兜底，不因推送恢复而豁免。\n'
    elif case['fixture'] == 'dedupe':
        base = {'create.py': 'from storage import UniqueConflict\n\ndef create(db, key, value):\n    return db.insert(key, value)\n', 'README.md': readme}
        final = {'create.py': 'from storage import UniqueConflict\n\ndef create(db, key, value):\n    try:\n        return db.insert(key, value)\n    except UniqueConflict:\n        return db.find(key)\n'}
    else:
        assert case['fixture'] == 'spelling'
        base = {'cache.py': 'def report(logger):\n    logger.info("Cache udpated")\n', 'README.md': readme}
        final = {'cache.py': 'def report(logger):\n    logger.info("Cache updated")\n'}
    for files, note in ((base, '初始化示例服务'), (final, message)):
        for name, content in files.items():
            (repo / name).write_text(content)
        git(repo, 'add', '--', *files)
        if note is not None:
            git(repo, 'commit', '-qm', note)
