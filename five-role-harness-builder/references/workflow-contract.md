# 五角色工作流契约

当你需要精确的角色顺序、文件归属或阻塞行为时，在读取完 `SKILL.md` 后继续使用这份参考。

## 启动决策树

1. 针对项目根目录运行 `init_team_harness.py`。
2. 读取 `team/workflow.md` 和全部五个 `team/*.md` 角色文件。
3. 读取持久化状态文件。
4. 检查仓库和 `git status`。
5. 决定进入哪个阶段：
   - 没有已批准需求，或者没有 PRD：从 `pm` 开始。
   - 已有 PRD，但执行计划缺失或已过期：从 `leader` 开始。
   - 当前活跃项包含 UI 或 UX 工作：在 `develop` 之前或并行经过 `designer`。
   - 代码已经准备好验证：流转到 `qa`。
   - 某个已完成项还没有 commit 或 checkpoint：先完成收尾流程，再开始新工作。

## 规范角色顺序

除非仓库内的 `team/workflow.md` 要求更严格的顺序，否则将以下顺序作为默认流程：

1. `pm`
2. `leader`
3. `designer`
4. `develop`
5. `qa`
6. `leader` 对下一项做最终同步

第二次 `leader` 介入应保持轻量。它的作用是让计划、风险和下一步归属在 QA 之后重新同步。

## 角色提示词

基于仓库内已有的角色文件来构造子代理提示，而不是重新发明角色人格。每条提示都应该把角色指向当前活跃计划项、相关文档以及它明确拥有的文件。

### PM

目标：
澄清需求，并让 PRD 保持为可持久使用的文档。

负责：
- `docs/pm/prd.md`
- `.harness/state/project-brief.md` 中相关的范围说明

最小提问方式：
`Use team/pm.md as the role definition. Review the current request, docs, and active plan item. Update docs/pm/prd.md with scope, user value, acceptance criteria, and requirement changes that matter for execution.`

### Leader

目标：
把需求转换为可执行的任务列表，并保持排期与顺序准确。

负责：
- `docs/leader/plan.md`
- `.harness/state/current-plan.md`

最小提问方式：
`Use team/leader.md and team/workflow.md as the operating rules. Update docs/leader/plan.md and .harness/state/current-plan.md so the next active item, dependencies, risks, and acceptance criteria are explicit.`

### Designer

目标：
把产品意图转化为对实现和 QA 都有长期价值的设计说明。

负责：
- `docs/designer/design.md`

最小提问方式：
`Use team/designer.md as the role definition. Read the PRD, plan, and current UI context. Update docs/designer/design.md with user flows, layout decisions, components, interaction notes, edge cases, and review feedback.`

### Develop

目标：
实现当前活跃项，并留下可长期使用的实现说明。

负责：
- 当前活跃计划项的代码改动
- `docs/develop/implementation.md`

最小提问方式：
`Use team/develop.md as the role definition. Implement the active plan item, update docs/develop/implementation.md with the chosen approach, changed files, verification notes, and follow-up risks, and report what still needs QA validation.`

### QA

目标：
根据已保存的验收标准验证当前项，并阻止不安全的完成状态。

负责：
- `docs/qa/report.md`

最小提问方式：
`Use team/qa.md as the role definition. Validate the active plan item against docs/pm/prd.md, docs/leader/plan.md, and the implementation diff. Update docs/qa/report.md with test evidence, defects, risk level, and pass/fail status.`

## 完成顺序

按以下顺序完成一个计划项的收尾：

1. 刷新 `docs/` 下的角色文档。
2. 更新 `.harness/state/current-plan.md`。
3. 验证变更。
4. 暂存实现文件和更新后的 harness 文件。
5. 提交已完成项。
6. 记录 commit SHA。
7. 运行 `save_team_checkpoint.py`。
8. 在 `.harness/state/session-handoff.md` 中写下精确的下一步动作。

## 阻塞规则

- 当必需的角色文件缺失时，停止并写 checkpoint。
- 当产品方向尚未明确时，停止并写 checkpoint。
- 当用户的改动与当前实现冲突时，停止并写 checkpoint。
- 当验证失败且当前会话无法安全修复问题时，停止并写 checkpoint。

## 自主执行规则

- 除非用户要求暂停，否则从一个已完成项自动继续到下一个。
- 保持角色文档精炼且可持久使用。不要把临时推理过程或一次性头脑风暴内容塞进 `docs/`。
- 优先依据仓库内的事实做判断，而不是依赖假设。若必须做假设，把它记录到 `.harness/state/project-brief.md`。
