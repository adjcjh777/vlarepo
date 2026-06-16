# Loop Contract

这是一套最小可运行的 loop engineering contract。它不是生产自动化，而是把“类似 Codex/Claude loop 的控制结构”落成可以检查的规则。

## 目标

让 agent 在一个工程项目中周期性发现小任务，隔离执行，独立验证，并把完成、失败、阻塞状态写回可持续记忆。

## Loop 阶段

1. Trigger
   - 手动启动、定时任务、CI 失败、issue 更新、Slack/邮件事件都可以是触发器。
   - 原型里用 `[d] discover` 代替真实触发器。

2. Discover
   - 从 issue、CI、日志、最近 diff、TODO、用户输入里找候选任务。
   - 每个任务必须小到能被一次 maker/checker 循环验证。

3. Select
   - 只选择一个当前任务。
   - 并行时要使用独立 worktree，避免多个 agent 改同一份文件。

4. Make
   - maker agent 只做一个 coherent change。
   - 必须先找上下文，再改文件，再运行最小验证。

5. Check
   - checker agent 不能复用 maker 的“我觉得完成了”作为证据。
   - checker 看 diff、测试输出、日志、截图或真实运行结果。

6. Repair / Stop
   - 如果 checker 驳回，loop 回到 make，但受 retry budget 限制。
   - 如果预算耗尽、需求不清或权限不足，状态必须变成 blocked。

7. Persist
   - 记录 done、blocked、attempts、verification notes。
   - 真实系统中可以写入 Markdown、GitHub issue、Linear、数据库或 Codex memory。

## Stop Conditions

一个任务只有在满足以下条件时才算 done：

- 范围与原任务一致，没有顺手大改。
- 至少有一条可复核验证证据。
- checker 明确接受。
- 残余风险被写出。

整个 loop 在以下情况停止：

- 没有 open / needs_repair 任务。
- 迭代预算耗尽。
- 触发人工阻塞。
- 验证信号不可获得。

## 最小真实化路径

1. 把 `Discover` 接到 GitHub issue、CI logs 或 `TODO.md`。
2. 把 `Make` 接到 Codex/Claude 的一个 maker prompt。
3. 把 `Check` 接到独立 checker prompt 或 code review agent。
4. 把状态写入 `LOOP_STATE.md` 或 issue board。
5. 加上成本预算、最长运行时间、禁止命令列表和人工确认点。

## 不建议自动化的部分

- 模糊产品决策。
- 生产数据库写操作。
- 安全/权限边界不清的改动。
- 没有验证命令或验收标准的“大任务”。
