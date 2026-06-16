# Loop Engineering Kit

这是一个最小可玩的 loop engineering 原型，用来把“设计会 prompt agent 的系统”具象化。

它回答的问题是：一个 agent loop 至少需要哪些状态、动作、验收信号和停止条件，才不会变成无限烧 token 的长 prompt？

## 一条命令运行

在当前 workspace 根目录运行：

```bash
python3 outputs/loop_engineering_kit/loop_tui.py
```

进入后按：

- `d` 发现候选任务
- `s` 启动下一个任务
- `a` 模拟 maker agent 产出一轮
- `p` checker 通过
- `f` checker 驳回并触发修复或阻塞
- `b` 人工阻塞
- `r` 重置
- `q` 退出

每一步都会重画完整状态，包括当前任务、尝试次数、checker note、事件日志、maker prompt 和 checker prompt。

## 文件说明

- `loop_core.py`：纯状态机，不做 I/O，可以迁移进真实工具。
- `loop_tui.py`：一次性终端壳，只用来手动推动状态。
- `LOOP_CONTRACT.md`：真实 loop 的阶段、停止条件和迁移路径。
- `agent_prompts/maker.md`：maker agent 模板。
- `agent_prompts/checker.md`：checker agent 模板。
- `NOTES.md`：原型结论记录位。

## 它和真实 loop 的差距

这个原型故意不直接调用 Codex、Claude、GitHub 或 CI。它先把控制结构跑顺：任务怎么进队列、什么时候开始、谁负责产出、谁负责验收、失败怎么回环、什么时候阻塞。

要变成真实 loop，下一步是把四个点接上外部系统：

1. `discover` 接 GitHub issues、CI logs、TODO 或 cron。
2. `agent_step` 接 maker agent，比如 Codex thread / Claude Code session。
3. `verify_pass` / `verify_fail` 接 checker agent、测试命令、截图验收或 code review。
4. `events` 和 task state 写入 Markdown、issue board 或持久 memory。

## 我的建议

第一版真实 loop 不要自动改生产代码。先做一个只读 triage loop：每天扫描 issue、CI 和最近 diff，输出三个候选任务和建议验证命令。等这个 loop 的判断稳定后，再让 maker agent 在独立 worktree 里处理低风险任务。
