# ARS 科研文献写作工作区

这个目录用于后续通过 Codex 全局 skill `academic-research-suite` 自动化推进科研文献调研、综述、论文写作、审稿和定稿。

已安装的 Codex skill:

- 名称：`academic-research-suite`
- 安装位置：`/Users/junhaocheng/.codex/skills/academic-research-suite`
- 来源：`https://github.com/Imbad0202/academic-research-skills-codex`
- 文章提到的 Claude 插件源仓库：`https://github.com/Imbad0202/academic-research-skills`

## 快速开始

新开一个 Codex 对话后，先用下面这种格式启动：

```text
Use $academic-research-suite.

Goal: write a literature-review-based research paper.
Current materials: see /Users/junhaocheng/working-dir/ars-literature-workspace/inputs/.
Output needed now: Socratic research-question narrowing and a missing-evidence checklist.
Constraints: Chinese coordination, final academic artifacts can be Chinese or English depending on target venue.
```

如果已经有明确研究问题，可以改用：

```text
Use $academic-research-suite: ars-lit-review <你的研究问题或主题>
```

或：

```text
Use $academic-research-suite: ars-plan <你的论文题目、研究问题、目标期刊/会议和材料路径>
```

## 工作流建议

1. 把原始题目、导师要求、已有论文、笔记或数据放进 `inputs/`。
2. 用 `prompts/start_research_question_scoping.md` 先收敛研究问题。
3. 文献检索和阅读矩阵放进 `literature/`。
4. 大纲和章节草稿放进 `drafts/`。
5. 每轮审稿、修改意见和回应放进 `reviews/`。
6. 最终交付文件放进 `outputs/`。
7. 阶段状态、引用核验和人工覆盖说明放进 `logs/`。

## 重要提醒

Codex 当前会话可能还不能热加载刚安装的 skill。新开 Codex 对话后运行 `/skills`，应能看到 `academic-research-suite`。如果 slash 输入被客户端拦截，就使用普通文本别名，例如 `ars-plan ...`。
