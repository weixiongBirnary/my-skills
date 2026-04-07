# 状态文件参考

当你需要为五角色 harness 工程创建或更新持久化文件时，使用这份参考。

## 目录布局

```text
docs/
  progress.md
  pm/
    prd.md
  leader/
    plan.md
  designer/
    design.md
  develop/
    implementation.md
  qa/
    report.md
.harness/
  checkpoints/
  state/
    current-plan.md
    manifest.json
    progress-log.md
    project-brief.md
    rules.md
    session-handoff.md
```

## 文件契约

### `docs/pm/prd.md`

保存可长期使用的产品需求文档。

推荐章节：
- 问题
- 用户
- 目标
- 范围
- 非目标
- 验收标准
- 风险与开放问题

### `docs/leader/plan.md`

保存便于人阅读的执行计划。

推荐章节：
- 当前阶段
- 里程碑
- 活跃项
- 依赖
- 风险与阻塞项
- 完成标准

### `docs/designer/design.md`

只保留那些在后续实现或 QA 中仍需要使用的设计决策。

推荐章节：
- 用户流
- 页面或界面说明
- 组件与状态
- 响应式或无障碍说明
- 未解决的设计问题

### `docs/develop/implementation.md`

总结当前活跃项是如何实现的。

推荐章节：
- 目标
- 技术方案
- 改动文件
- 验证说明
- 已知限制

### `docs/qa/report.md`

保存最新的 QA 证据和质量门禁结论。

推荐章节：
- 测试范围
- 测试用例
- 证据
- 缺陷
- 通过或失败
- 发布建议

### `docs/progress.md`

每次 checkpoint 后追加一条简洁记录。保持该文件可被人快速阅读和扫描。

推荐字段：
- 时间戳
- 计划项
- 状态
- 触达角色
- Commit SHA
- 总结
- 下一步

### `.harness/state/project-brief.md`

在这里保存可长期使用的源请求和仓库事实。

推荐章节：
- 源请求
- 仓库事实
- 团队文件映射
- 假设
- 范围说明

### `.harness/state/current-plan.md`

除非用户要求并行工作，否则始终只保留一个活跃计划项。

推荐结构：

```markdown
# Current Plan

## Item Format
- ID:
- Title:
- Stage:
- Owner:
- Status:
- Depends on:
- Deliverables:
- Acceptance:

## Plan Items
### P1-T1
- Title: ...
- Stage: requirement-analysis
- Owner: pm
- Status: pending
- Depends on: none
- Deliverables: docs/pm/prd.md, docs/leader/plan.md
- Acceptance: ...
```

### `.harness/state/progress-log.md`

每次 checkpoint 追加一条带日期的记录。除非只是修正明显的格式问题，否则不要改写历史。

### `.harness/state/session-handoff.md`

每次 checkpoint 都重写这个文件，让下一次对话可以快速恢复。

推荐字段：
- 最后更新时间
- 计划项
- 状态
- 触达角色
- Commit SHA
- 最新 checkpoint
- 总结
- 改动文件
- 验证
- 风险
- 下一步

### `.harness/state/manifest.json`

在这里保存机器可读的元数据：
- `project_root`
- `created_at`
- `updated_at`
- `last_plan_id`
- `last_status`
- `last_roles`
- `last_commit_sha`
- `latest_checkpoint`
- `required_team_files`

## 初始化命令

当 harness 状态尚不存在时，使用随 skill 提供的初始化脚本：

```bash
python3 /Users/Zhuanz/.codex/skills/five-role-harness-builder/scripts/init_team_harness.py \
  --root "$PWD" \
  --source-request "<user request>"
```

## Checkpoint 命令

每完成一个计划项，以及每次阻塞退出或中断退出时，使用随 skill 提供的脚本：

```bash
python3 /Users/Zhuanz/.codex/skills/five-role-harness-builder/scripts/save_team_checkpoint.py \
  --root "$PWD" \
  --plan-id P1-T1 \
  --status completed \
  --role pm \
  --role leader \
  --role develop \
  --summary "Completed the first requirement slice and aligned docs, code, and QA evidence." \
  --next-step "Start the next plan item." \
  --changed-file docs/pm/prd.md \
  --changed-file docs/leader/plan.md \
  --changed-file src/app.tsx \
  --test "npm run build" \
  --commit-sha abc1234
```

如果总结内容较长，使用 `--summary-file`。
