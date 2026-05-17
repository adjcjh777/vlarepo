## 语言规则
- 内部思考和对用户的回复统一使用中文。

## 工作边界
- 本目录是使用 Codex 全局 skill `academic-research-suite` 进行科研文献调研、综述、论文写作、审稿和定稿的工作区。
- 后续与科研文献自动写作相关的材料、草稿、审稿意见和输出都优先放在本目录内。
- 涉及引用、论文事实、作者、年份、DOI、实验数字和投稿规则时，必须核验来源，不要编造引用或补齐不确定信息。
- 如果用户只有宽泛主题，先使用 `$academic-research-suite` 的 deep-research socratic 路线收敛研究问题，不要直接写大纲或正文。
- 如果用户要求“一条龙”写作流程，优先使用 `$academic-research-suite` 的 academic-pipeline 路线，并按阶段停在明确检查点。

## 目录约定
- `inputs/`: 用户提供的原始材料、题目、要求、数据、截图或笔记。
- `literature/`: 文献矩阵、检索式、引用核验记录和阅读笔记。
- `drafts/`: 大纲、章节草稿、摘要、引言、相关工作等可修改文本。
- `reviews/`: 模拟审稿、人工审稿意见、修改路线图和 rebuttal 材料。
- `outputs/`: 最终交付版 Markdown、DOCX、LaTeX、PDF 或投稿包。
- `prompts/`: 可复用的 Codex/ARS 启动 prompt。
- `logs/`: 运行记录、阶段状态、人工覆盖说明和完整性检查记录。

## 推荐调用方式
- 新主题收敛：`Use $academic-research-suite. I want to write a paper on ... I do not yet have a clear research question.`
- 文献综述：`Use $academic-research-suite: ars-lit-review ...`
- 论文规划：`Use $academic-research-suite: ars-plan ...`
- 全流程：`Use $academic-research-suite: ars-full ... Begin with Stage 0 and stop after producing the dashboard.`
