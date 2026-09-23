---
max_turns: 4
allowed_tools: [Read, Skill]
---

根据以下全部已知信息，生成一条 Git 提交说明。只返回提交说明，可以使用代码块；不要执行提交或改动文件。无需查询仓库，以下材料完整。

仓库使用简短中文标题，没有强制正文格式。
本次 diff：
```diff
-const defaultPageSize = 20;
+const defaultPageSize = 30;
```
没有提供业务动机、兼容性约束或验证结果。
