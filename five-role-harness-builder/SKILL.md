---
name: five-role-harness-builder
description: 在当前仓库中基于仓库内的 `team/leader.md`、`team/pm.md`、`team/develop.md`、`team/designer.md`、`team/qa.md` 和 `team/workflow.md` 这六个文件，创建或恢复一个由五个协作角色驱动的长时间运行 harness 工程。当 Codex 需要一个可中断、可恢复的多代理交付工作流，并且要把各角色输出保存到 `docs/`、把进度持久化到 `.harness/`、在每完成一个需求或计划项后提交 git、并在对话中断后无缝继续时，使用这个 skill。
---

# 五角色 Harness 构建器

使用这个 skill 可以把当前项目从一次性任务模式转换成可持久运行的 harness 工作流。把仓库中的文件视为唯一事实来源，这样工作就可以暂停、恢复，并在聊天意外中断后继续推进。

## 快速开始

1. 除非用户明确指定其他根目录，否则将当前工作目录视为项目根目录。
2. 确认仓库中包含以下文件：
   - `team/workflow.md`
   - `team/leader.md`
   - `team/pm.md`
   - `team/develop.md`
   - `team/designer.md`
   - `team/qa.md`
3. 在第一个执行周期开始前，运行 `python3 /Users/Zhuanz/.codex/skills/five-role-harness-builder/scripts/init_team_harness.py --root "$PWD" --source-request "<user request>"`。
4. 按以下顺序读取可持久状态：
   - `team/workflow.md`
   - 五个 `team/*.md` 角色文件
   - `.harness/state/session-handoff.md`
   - `.harness/state/current-plan.md`
   - `.harness/state/project-brief.md`
   - `.harness/state/manifest.json`
   - `.harness/checkpoints/` 下最新的文件（如果存在）
   - `docs/` 下的角色文档
5. 检查仓库结构和 `git status`。
6. 根据团队工作流和已保存的计划判断下一个活跃阶段。

如果需要查看角色流转和职责归属规则，读取 [references/workflow-contract.md](./references/workflow-contract.md)。如果需要查看持久化文件契约和 checkpoint 的用法，读取 [references/state-files.md](./references/state-files.md)。

## 必需的仓库输入

- 将 `team/workflow.md` 视为阶段顺序的事实来源。
- 将每个 `team/*.md` 文件视为该角色职责、语气、输出格式和约束条件的事实来源。
- 保留用户已有的角色文件。除非用户明确要求，否则不要重写它们。
- 如果任何必需的角色文件缺失，先停下来询问用户，是要创建该文件，还是基于推断使用替代版本。

## 持久化布局

在目标项目中初始化并维护以下文件：

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

将仓库内的 `docs/` 作为五个角色的持久化输出面：

- 产品经理负责 `docs/pm/prd.md`。
- 组长负责 `docs/leader/plan.md`。
- 设计师负责 `docs/designer/design.md`。
- 开发负责 `docs/develop/implementation.md`。
- QA 负责 `docs/qa/report.md`。
- 编排者把跨角色的执行进度追加到 `docs/progress.md`。

使用 `.harness/` 保存恢复状态、机器可读指针和不可变 checkpoint。

## 核心规则

- 使用五个明确区分的角色视角：`leader`、`pm`、`develop`、`designer` 和 `qa`。
- 如果可以委派，则优先为每个角色使用一个子代理；如果无法委派，则按顺序模拟这些角色，但仍然要产出相同的制品。
- 主代理始终作为编排者，负责决定顺序、合并输出、更新持久状态并写出最终 checkpoint。
- 除非用户明确要求并行工作，否则始终只保留一个 `in_progress` 的活跃计划项。
- 每个需求或计划项都必须按 `team/workflow.md` 中适用的角色顺序流转；不要为了追求速度跳过角色评审。
- 在执行周期内就把有意义的角色产出写入 `docs/`，而不是等整个项目结束后一次性补写。
- 每完成一个需求或计划项，都必须在结束该周期前创建一次 git 提交。
- 每完成一个需求或计划项后，都要把进度保存到 `.harness/`；如果当前周期被阻塞或中断，也要在退出前保存。
- 恢复执行时，以磁盘上的状态为准，不要依赖聊天上下文记忆。
- 所有持久状态都使用 ISO 8601 时间戳。

## 角色归属

默认职责分工如下：

- `pm`：澄清需求，维护 `docs/pm/prd.md`，记录范围和验收标准。
- `leader`：把已确认需求转成执行顺序，更新 `docs/leader/plan.md`，并决定下一个活跃任务。
- `designer`：在 `docs/designer/design.md` 中产出 UX、UI、交互和评审说明。
- `develop`：实现当前活跃任务，更新 `docs/develop/implementation.md`，并报告改动文件。
- `qa`：验证验收标准，在 `docs/qa/report.md` 中记录证据，并给出通过或失败结论。

编排者负责：

- 决定下一个运行的角色
- 将角色输出与保存的计划对齐
- 确保文档、代码、提交记录和 checkpoint 保持一致
- 为下一次对话准备精确的交接信息

## 交付周期

每个计划项都按以下顺序推进：

1. 从 `.harness/state/current-plan.md` 读取当前活跃计划项及其验收标准。
2. 按 `team/workflow.md` 要求的角色顺序执行。常见情况下，这意味着：
   - `pm` 细化或确认需求。
   - `leader` 更新计划和角色分工。
   - 当该项涉及 UI、UX 或交互变化时，由 `designer` 更新设计说明。
   - `develop` 实现该项。
   - `qa` 验证该项。
3. 把当前周期中真正有持久价值的决定和结果写入 `docs/` 下对应的角色文档。
4. 如果验证失败，则将计划项保持为 `in_progress` 或移动到 `blocked`，记录阻塞原因，并写入 checkpoint，而不是错误地提交一个“完成”状态。
5. 如果验证通过，则在 `.harness/state/current-plan.md` 中把计划项标记为 `completed`。
6. 暂存实现文件，以及更新后的 `docs/` 和 `.harness/state/` 文件。
7. 为该已完成计划项创建 git 提交。
8. 记录 commit SHA。
9. 运行 `save_team_checkpoint.py`，追加进度日志、写入不可变 checkpoint，并刷新 `.harness/state/session-handoff.md`。
10. 只有在 checkpoint 写完后，才能把下一个计划项移动到 `in_progress`。

如果仓库还不是 git 仓库，则在第一个完成周期之前初始化 git，以满足“每项完成后必须提交”的规则。

## 恢复协议

当一个新的对话开始时，按以下顺序恢复：

1. 读取 `.harness/state/session-handoff.md`。
2. 读取 `.harness/state/current-plan.md`。
3. 读取 `.harness/state/manifest.json` 中记录的最新 checkpoint。
4. 读取 `docs/` 中与下一个阶段相关的角色文档。
5. 如果下一步依赖某个角色的判断，则重新读取 `team/workflow.md` 和对应的角色提示文件。
6. 在需要时检查 `git status`，并把当前工作区与上次记录的提交进行对比。
7. 从下一个未完成项或被阻塞项继续。

如果磁盘状态与聊天历史冲突，以磁盘状态为准，并明确指出不一致之处。

## 提交与进度规则

- 提交信息必须包含计划项 ID，例如 `feat(harness): complete P1-T2 landing page polish`。
- 相关的 `docs/` 文件和 `.harness/state/` 文件必须与代码改动一起进入同一个提交，以保持叙述状态与代码历史对齐。
- 如果一个周期在任何计划项完成前就被阻塞，可以只写 checkpoint，而不强行提交。
- 如果产品范围变化导致 PRD 或当前计划失效，应先刷新 `docs/pm/prd.md` 或 `docs/leader/plan.md`，再继续实现。
- `docs/progress.md` 必须保持事实化和只追加，不要回写历史。下一次对话应该能在一分钟内快速扫清上下文。

## Checkpoint 命令

每完成一个计划项，以及每次阻塞退出或中断退出时，都使用随 skill 提供的脚本：

```bash
python3 /Users/Zhuanz/.codex/skills/five-role-harness-builder/scripts/save_team_checkpoint.py \
  --root "$PWD" \
  --plan-id P1-T1 \
  --status completed \
  --role pm \
  --role leader \
  --role designer \
  --role develop \
  --role qa \
  --summary "Completed the first landing page slice with aligned PRD, plan, design notes, implementation notes, and QA sign-off." \
  --next-step "Move P1-T2 to in_progress and start the next requirement review." \
  --changed-file docs/pm/prd.md \
  --changed-file docs/leader/plan.md \
  --changed-file docs/designer/design.md \
  --changed-file docs/develop/implementation.md \
  --changed-file docs/qa/report.md \
  --changed-file src/app.tsx \
  --test "npm run build" \
  --test "Manual responsive check" \
  --commit-sha abc1234
```

如果总结内容较长，使用 `--summary-file` 代替 `--summary`。

## 退出条件

持续循环执行，直到满足以下任一条件：

- 所有计划项都已完成
- 用户暂停或改了方向
- 审批、凭据或外部依赖阻塞了进度
- 某个角色的签收缺失，且当前会话无法安全解决

在任何一次会话结束前，都要确保 `.harness/state/session-handoff.md` 精确写明下一步动作。
