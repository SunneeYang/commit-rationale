"""Deterministic synthetic repositories; grading facts are not copied into them."""

import hashlib
import os
from pathlib import Path
import subprocess


CASES = [
    {
        'id': '01-conversation', 'guidance': 'skill',
        'prompt': '''帮我给暂存改动写提交说明，先不要提交。

此前这次任务的对话记录：
用户：客户说撤权之后还有人能看报表。附件里写的是撤权到失去访问最多十五分钟。
助手：缓存是一小时，先改十二分钟留点余量？
用户：先试一下。token 的期限别动，这次只处理权限缓存。
助手：十二分钟那版的两个缓存单测过了，完整服务联调环境还没好。
用户：刚跟对方又对过，最后统一十五分钟即可。这条约定以后也要遵守，不能为了命中率再往上调。
助手：参数已改成十五分钟，完整联调还没跑，两个单测也没重跑。
用户：日志里有个拼写先留着，别混进这次；上午讨论两轮有点慢。
''',
        'oracle': '最终暂存改动仅将权限缓存60分钟改为15分钟。客户撤权最长15分钟的约定没有写入代码或文档。12分钟草案被放弃；token和日志未改。只对12分钟草案跑过两个单测，15分钟最终版未复测或联调。',
        'checks': [
            ('constraint', 'context', '正文保留客户撤权最长十五分钟的约定及未来不能仅为缓存命中率延长期限的限制。'),
            ('current', 'accuracy', '描述最终15分钟方案，不把12分钟、token或日志说成本次最终改动。'),
            ('noise', 'concision', '正文不复述60改15这一赋值变化，不写讨论轮次或试过十二分钟的开发经过；为限定旧测试范围而提十二分钟不扣分。'),
            ('tests', 'verification', '不把草案的单测通过说成最终版已通过；如提验证，明确范围或未复测。'),
        ],
    },
    {
        'id': '02-merge', 'guidance': 'skill',
        'prompt': '刚合完 feature/export，请给当前这个 merge 拟一份提交说明。只输出说明，不修改提交。',
        'oracle': 'HEAD是普通双亲merge。仅本次源提交正文记录：仍在部署的Pine导入器2.4会把数值编号前导零丢掉，退役前要保持字符串；兼容性只检查本地旧导入器样本，没有验证所有发布包。第一父分支先前令牌30天的提交不在本次引入范围。最终代码仅改变编号序列化并处理空值，未记录以上外部约束。',
        'checks': [
            ('constraint', 'context', '新merge正文保留Pine旧导入器丢前导零以及其退役前维持字符串编号的约束，不要求复述具体版本号。'),
            ('scope', 'accuracy', '不把目标分支已有的令牌30天背景或其他无关历史写进此次合并说明。'),
            ('noise', 'concision', '正文不只是原样拼接源消息，不复述可见的字符串转换或空值占位符实现。提及字符串格式以解释兼容约束可接受。'),
            ('tests', 'verification', '保留仅验证本地旧导入器样本、未覆盖全部发布包的范围，不声称合并后重新测试。'),
        ],
    },
    {
        'id': '03-amend', 'guidance': 'skill',
        'prompt': '这次补改准备 amend 到 HEAD，帮我重写提交说明，先不要执行。暂存的补改还没跑测试。',
        'oracle': 'HEAD原提交仅正文记录：合作方1.8及更早网关只识别legacyCode=17，新类型会被当成传输故障，旧网关退役前保留；原实现单测通过。暂存补改增加Retry-After。最终整体仍包含legacyCode和新响应头，补改后未测试。',
        'checks': [
            ('constraint', 'context', '保留合作方旧网关兼容原因及旧网关退役前保留错误码的条件，不能只围绕本次新增响应头。'),
            ('whole', 'accuracy', '标题或整体说明覆盖旧网关兼容与Retry-After，不把原有功能描述为删除或新语义。'),
            ('noise', 'concision', '正文保留原因而非罗列字段赋值和响应构造步骤，不添加开发流水账。为表达兼容约束提legacyCode=17可接受。'),
            ('tests', 'verification', '不扩大原测试结论；明确最终版未复测或不声称它已测试通过。'),
        ],
    },
    {
        'id': '04-history-read', 'guidance': 'reader',
        'prompt': '请求偶尔超时，我想把当前两秒改成八秒。先帮我评估这个改动能不能做，别改文件。',
        'oracle': '唯一的外部期限记录在历史提交正文：Orchid桌面端4.1固定在3秒截止，服务端用2秒给传输留余量。当前代码只存REQUEST_TIMEOUT=2，README指出调用方代码不在本仓库。没有证据说明4.1已退役或当前客户端期限已改变。应查历史后给条件性判断：不能只改成8秒，先核实客户端期限/覆盖范围。',
        'checks': [
            ('history', 'context', '指出历史记录中的客户端3秒截止及服务端留余量，表明使用了正文中的事实而不是仅据常量推测。'),
            ('decision', 'accuracy', '不无条件建议将两秒直接提高到八秒，说明服务端改大不能解决调用方先截止的问题。'),
            ('current', 'verification', '将历史期限作为待核实现状，说明需要确认当前客户端期限或旧版本退役情况；不能宣称所有现行客户端必然仍是3秒。'),
        ],
    },
    {
        'id': '05-documented', 'guidance': 'skill',
        'prompt': '策略和对应说明都已暂存，帮我写提交信息，先不要提交。',
        'oracle': 'diff把权限缓存改为15分钟，并在README同时新增客户撤权15分钟上限、不能为命中率延长的完整原因。没有额外背景、测试结果或未写入文档的限制。该案例用于检测正文重复最终diff中的文档。',
        'checks': [
            ('title', 'accuracy', '标题准确覆盖权限缓存期限及说明更新。无需逐项列文件。'),
            ('dedupe', 'concision', '只保留简洁标题（允许代码块），不把diff里的README约束再写成正文。'),
            ('claims', 'verification', '不编造测试通过、线上效果或未提供的外部条件。'),
        ],
    },
    {
        'id': '06-squash', 'guidance': 'skill',
        'prompt': 'feature/dedupe 准备压成一条合到 main，先给我最终提交说明，不要执行合并。',
        'oracle': '来源范围main..feature/dedupe。最初用分布式锁因为唯一索引尚未部署，后来删除锁改靠唯一键冲突；正文明确发布顺序：先部署唯一索引，再发布新服务。最终树没有锁。最后源提交记录单元测试通过、未验证跨区域并发。这些部署与验证事实未写进代码或README。',
        'checks': [
            ('deployment', 'context', '正文保留先部署唯一索引再发布新服务的外部发布前提。'),
            ('superseded', 'accuracy', '正确描述最终唯一约束方案，不把已删除的锁或旧的索引缺失状态当成现行设计。'),
            ('noise', 'concision', '不罗列先加锁后撤锁的开发经过，也不复述最终写数据库、冲突返回已有记录的实现步骤；为解释发布前提提锁可接受。'),
            ('tests', 'verification', '保留源提交单元测试与未覆盖跨区域并发的边界，不扩大验证结论。'),
        ],
    },
]


def git(repo, *args):
    environment = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
                   'GIT_AUTHOR_DATE': '2026-09-01T00:00:00+00:00', 'GIT_COMMITTER_DATE': '2026-09-01T00:00:00+00:00'}
    return subprocess.check_output(['git', '-c', 'user.name=Benchmark', '-c', 'user.email=benchmark@example.invalid',
                                    '-c', 'commit.gpgsign=false', *args], cwd=repo, env=environment, stderr=subprocess.DEVNULL).decode()


def setup_case(case_id, repo):
    repo.mkdir()
    git(repo, 'init', '-q', '-b', 'main')

    def stage(files):
        for name, text in files.items():
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        git(repo, 'add', '--', *files)

    def commit(message, files):
        stage(files)
        git(repo, 'commit', '-qm', message)

    readme = '# 示例服务\n\n提交标题使用简短中文。\n'
    commit('初始化示例服务', {'README.md': readme})
    if case_id in ('01-conversation', '05-documented'):
        commit('增加权限缓存', {'cache.py': 'PERMISSION_TTL_MINUTES = 60\n'})
        files = {'cache.py': 'PERMISSION_TTL_MINUTES = 15\n'}
        if case_id == '05-documented':
            files['README.md'] = readme + '\n客户要求撤权后最多十五分钟内失去访问能力。权限缓存必须遵守这个上限，不能仅为提高命中率而延长。\n'
        stage(files)
    elif case_id == '02-merge':
        commit('增加导出模块', {'export.py': 'def export_id(value):\n    return int(value)\n'})
        git(repo, 'branch', 'feature/export')
        commit('调整令牌期限\n\n合作方令牌暂保留30天，此规则与导出模块无关。', {'token.py': 'TOKEN_DAYS = 30\n'})
        git(repo, 'checkout', '-q', 'feature/export')
        commit('保留导出记录的字符串编号\n\n仍在部署的 Pine 导入器 2.4 会丢掉数值编号的前导零。它们退役前，导出编号必须继续使用字符串。', {'export.py': 'def export_id(value):\n    return str(value)\n'})
        commit('处理空白导出编号\n\n兼容性只检查了本地旧导入器样本，没有验证所有已发布导入器。', {'export.py': 'def export_id(value):\n    return str(value) if value is not None else "-"\n'})
        git(repo, 'checkout', '-q', 'main')
        git(repo, 'merge', '--no-ff', '-qm', '合入导出调整', 'feature/export')
    elif case_id == '03-amend':
        commit('增加限流响应', {'response.py': 'def rate_limit():\n    return {"status": 429}\n'})
        commit('兼容旧网关的限流响应\n\n合作方仍运行的 1.8 及更早网关只识别 legacyCode=17，会将新的错误类型当作传输故障。旧网关退役前需要保留旧错误码。\n\n原实现的单元测试已通过。', {'response.py': 'def rate_limit():\n    return {"status": 429, "legacyCode": 17}\n'})
        stage({'response.py': 'def rate_limit():\n    return {"status": 429, "legacyCode": 17, "headers": {"Retry-After": "5"}}\n'})
    elif case_id == '04-history-read':
        commit('接入下游请求', {'client.py': 'REQUEST_TIMEOUT = 10\n\ndef fetch(session, url):\n    return session.get(url, timeout=REQUEST_TIMEOUT)\n', 'README.md': readme + '\n上游调用方的客户端代码不在本仓库。\n'})
        commit('缩短下游请求超时\n\nOrchid 桌面端 4.1 固定在3秒截止。服务端使用2秒给传输留余量，只增加服务端超时不会让客户端等待更久。', {'client.py': 'REQUEST_TIMEOUT = 2\n\ndef fetch(session, url):\n    return session.get(url, timeout=REQUEST_TIMEOUT)\n'})
        commit('增加健康检查', {'health.py': 'def health():\n    return "ok"\n'})
    elif case_id == '06-squash':
        commit('增加创建入口', {'create.py': 'def create(db, key, value):\n    return db.insert(key, value)\n'})
        git(repo, 'checkout', '-qb', 'feature/dedupe')
        commit('临时防止重复创建\n\n数据库唯一索引尚未部署，暂时使用分布式锁。', {'create.py': 'def create(db, lock, key, value):\n    with lock(key):\n        return db.insert(key, value)\n'})
        commit('使用唯一约束处理重复创建\n\n发布顺序已经确认：先部署唯一索引，再发布新服务，因此撤掉临时分布式锁。', {'create.py': 'def create(db, key, value):\n    try:\n        return db.insert(key, value)\n    except UniqueConflict:\n        return db.find(key)\n'})
        commit('补充创建流程测试记录\n\n单元测试通过，尚未验证跨区域并发创建。', {'create.py': 'def create(db, key, value):\n    try:\n        return db.insert(key, value)\n    except UniqueConflict:\n        return db.find(key)\n\n# Duplicate creation returns the stored record.\n'})
    else:
        raise ValueError(case_id)


def snapshot(repo):
    files = {str(path.relative_to(repo)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in repo.rglob('*') if path.is_file() and '.git' not in path.relative_to(repo).parts}
    return {'head': git(repo, 'rev-parse', 'HEAD').strip(), 'refs': git(repo, 'show-ref'),
            'index': git(repo, 'ls-files', '--stage'), 'files': files}
