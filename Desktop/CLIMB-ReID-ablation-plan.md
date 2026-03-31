# CLIMB-ReID Ablation Plan

## 1. 目标

本计划默认后续要做的两个主要数据集是：

- `Market1501`
- `MSMT17`

可选第三数据集（有余力时）：

- `DukeMTMC-reID`

目标不是把所有变量都扫一遍，而是用尽量少的实验回答 5 个核心问题：

1. `IRM` 是否有效，收益来自排序还是 Mamba 序列建模？
2. 排序准则本身是否关键（相比随机/反向排序）？
3. `MMC` 是否有效，memory 是否优于 FC classifier？
4. `MMC` 的收益是否真的来自 `mean + hard` 双 memory 协作，而非任意一支单独 memory？
5. 当前结果是否主要来自模型设计，而不是训练技巧或 batch 设置？

---

## 2. 实验编号与 baseline 关系说明

**重要约定，避免重复跑实验：**

| 实验编号 | 说明 | 等价关系 |
|---|---|---|
| A1 | Market1501 纯 baseline（IRM off, MMC off） | 与 M1（FC classifier）是同一个实验，结果复用 |
| A5 | MSMT17 纯 baseline（IRM off, MMC off） | 与 MSMT17 的 FC baseline 结果复用 |
| I1 | Market1501 关闭 IRM | 等价于 A1，不单独重跑，直接复用 A1 结果 |

凡有等价关系的实验，**结果直接复用，不重复消耗计算资源**。

---

## 3. 固定设置（写死具体值，不允许模糊引用）

除非该实验本身就在改这些项，否则以下配置固定不变：

| 配置项 | 固定值 |
|---|---|
| Backbone | ViT-S/16（与主实验一致，需在此处填写实际值） |
| 输入分辨率 | 256×128 |
| Optimizer | SGD，lr=0.008，momentum=0.9，weight_decay=1e-4 |
| Scheduler | Cosine decay，warmup 10 epoch |
| 总训练 epoch 数 | 120 |
| IMS_PER_BATCH（默认） | 64 |
| NUM_INSTANCE（默认） | 4 |
| MEMORY_MOMENTUM（默认） | 0.2 |
| Random seed | 3407 |
| 评价指标 | mAP、Rank-1（Rank-5 可选报出但非主指标） |

> 注意：上表中标注"需在此处填写实际值"的项，在正式开跑前必须确认并填写，不允许以"与主实验一致"代替。

**每个实验必须记录以下内容：**

| 记录项 | 说明 |
|---|---|
| 数据集 | Market1501 / MSMT17 |
| 实验编号 | 如 A1、M3 |
| 改动项 | 相比默认配置改了什么 |
| 保持不变项 | 明确声明哪些未动 |
| 最终 mAP | 最后一个 checkpoint 的结果 |
| 最终 Rank-1 | 同上 |
| 最优 checkpoint mAP | Best checkpoint 结果 |
| 单 epoch 耗时 | 分钟 |
| 总训练耗时 | 小时 |
| 峰值显存 | GB |
| 是否稳定训练 | 是/否，如否需附 loss 曲线截图 |

**多次运行策略：**

- P0 实验（A 系列、M 系列）：至少跑 3 次，报均值 ± 标准差。
- P1 实验（I 系列、MM 系列、W 系列、H 系列）：至少跑 2 次，如两次差异 > 0.3 mAP 需补第 3 次。
- P2 实验（T 系列、E 系列）：跑 1 次即可，作为补充材料。

### 3.1 结果填写说明（滚动更新）

本文件同时承担“实验计划 + 结果滚动记录”两项功能，后续所有消融结果直接补在对应章节，不再另起一份独立结果文档。

- 状态词统一使用：`已完成`、`评估中`、`待运行`、`结果待补`
- 已完成项目以最终评估日志为准，数值统一保留 1 位小数
- 可复用实验直接沿用等价实验结果，例如 `M1 = A1`、`I1 = A1`
- 当前已填入结果来自 `2026-03-30` 至 `2026-03-31` 的最新补评估日志
- 所有空位均为后续 ablation 预留，不因暂时没结果而删行
- 若某实验训练完成但尚未补最终评估，先记为 `结果待补`，待评估完成后再回填数值

---

## 4. P0 实验：必须做

这一组是最核心的主结论，优先级最高。

### 4.1 模块主 ablation

先在 `Market1501` 做全套，再把关键组合迁移到 `MSMT17`。

| 编号 | 数据集 | IRM | MMC | 说明 |
| --- | --- | :---: | :---: | --- |
| A1 | Market1501 | off | off | 纯 baseline；同时作为 M1、I1 结果复用来源 |
| A2 | Market1501 | on | off | 只看 IRM（MMC 替换为 FC classifier） |
| A3 | Market1501 | off | on | 只看 MMC（IRM 关闭） |
| A4 | Market1501 | on | on | 完整模型 |
| A5 | MSMT17 | off | off | 纯 baseline；同时作为 MSMT17 侧 I1 等价结果 |
| A6 | MSMT17 | on | off | 只看 IRM |
| A7 | MSMT17 | off | on | 只看 MMC |
| A8 | MSMT17 | on | on | 完整模型 |

**决策门：**

- 若 A4 相对 A1 的 mAP 提升 < 1.0，先停止，检查代码逻辑再继续。
- 若 A2 和 A3 均无提升，优先级最低的 P2 实验可以取消。

这一组用于回答：

- 完整模型是否优于 baseline。
- IRM 和 MMC 是否各自带来独立增益。
- 两个模块叠加后是否仍有互补增益（排除饱和效应）。

#### 4.1.1 当前实验结果记录（滚动更新）

| 编号 | 数据集 | IRM | MMC | 状态 | mAP | Rank-1 | 备注 |
|---|---|:---:|:---:|---|---:|---:|---|
| A1 | Market1501 | off | off | 已完成 | 87.9 | 94.8 | baseline；同时复用为 M1、I1 |
| A2 | Market1501 | on | off | 已完成 | 88.4 | 95.0 | 当前 `IRM only` 相比 A1 小幅提升 |
| A3 | Market1501 | off | on | 已完成 | 85.9 | 93.7 | 当前 `MMC only` 低于 A1 |
| A4 | Market1501 | on | on | 已完成 | 86.6 | 93.7 | 完整模型；当前低于 A1，已触发暂停检查 |
| A5 | MSMT17 | off | off | 已完成 | 67.8 | 85.2 | MSMT17 baseline |
| A6 | MSMT17 | on | off | 待运行 |  |  |  |
| A7 | MSMT17 | off | on | 待运行 |  |  |  |
| A8 | MSMT17 | on | on | 待运行 |  |  | 关键完整模型复验 |

---

### 4.2 MMC 关键 ablation

**说明：M1（FC classifier）直接复用 A1 结果，不重新跑。**

| 编号 | 数据集 | Memory 形式 | 说明 |
|---|---|---|---|
| M1 | Market1501 | FC classifier | 复用 A1，不重跑 |
| M2 | Market1501 | mean only | 只保留均值 memory |
| M3 | Market1501 | hard only | 只保留 hard memory |
| M4 | Market1501 | mean + hard | 完整 MMC |
| M5 | MSMT17 | mean only | 关键复验 |
| M6 | MSMT17 | hard only | 关键复验（新增，用于分离 hard 的独立贡献） |
| M7 | MSMT17 | mean + hard | 关键复验 |

> 原计划 MSMT17 侧只有 M5/M6 两个，缺少 hard only 对照，现补充 M6，原 M6 顺延为 M7。

**决策门：**

- 若 M4 相对 M2 提升 < 0.5 mAP，需检查 hard memory 初始化与更新逻辑，再决定是否继续跑 MSMT17 侧。

这一组用于回答：

- memory 本身是否比 FC classifier 更好。
- mean memory 和 hard memory 是否各自带来独立增益。
- 双 memory 是否确实优于任一单 memory。
- hard memory 是否在更难的数据集上贡献更大。

#### 4.2.1 MMC 结果填写表（滚动更新）

| 编号 | 数据集 | Memory Type | 状态 | mAP | Rank-1 | ΔmAP vs FC | 备注 |
|---|---|---|---|---:|---:|---:|---|
| M1 | Market1501 | FC classifier | 已完成 | 87.9 | 94.8 | — | 复用 A1 |
| M2 | Market1501 | mean only | 待运行 |  |  |  |  |
| M3 | Market1501 | hard only | 待运行 |  |  |  |  |
| M4 | Market1501 | mean + hard | 待运行 |  |  |  | 与 A3 设计接近，但按 MMC 章节单独记录 |
| M5 | MSMT17 | mean only | 待运行 |  |  |  |  |
| M6 | MSMT17 | hard only | 待运行 |  |  |  |  |
| M7 | MSMT17 | mean + hard | 待运行 |  |  |  |  |

> 执行备注（`2026-03-31`）：`M2` 已在 `epoch 27` 人工暂停，`checkpoint_latest.pth.tar` 保留作为中断现场，但本轮中途结果不记入正式表；后续按修正后的评测策略整轮重跑。当前先只推进 `Market1501` 侧 `M2 -> M3 -> M4`，`MSMT17` 侧 `M5-M7` 延后。

---

## 5. P1 实验：建议做

这一组帮助解释"为什么有效"，是论文机制分析章节的核心支撑。

### 5.1 IRM 内部机制 ablation

**说明：I1（no reorder, no Mamba）直接复用 A1 结果，不重新跑。**

| 编号 | 数据集 | 设置 | 说明 |
|---|---|---|---|
| I1 | Market1501 | no reorder, no Mamba | 复用 A1，不重跑 |
| I2 | Market1501 | reorder only | 只做 patch 重排，不接 Mamba |
| I3 | Market1501 | reorder + Mamba | 完整 IRM |
| I4 | MSMT17 | reorder only | 关键复验 |
| I5 | MSMT17 | reorder + Mamba | 关键复验 |

这一组用于拆分 IRM 的收益来源：

- 收益来自 patch 重要性排序本身。
- 还是来自排序后的 Mamba 序列建模。
- 或两者缺一不可。

#### 5.1.1 IRM 内部机制结果填写表（滚动更新）

| 编号 | 数据集 | 设置 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---|---:|---:|---|
| I1 | Market1501 | no reorder, no Mamba | 已完成 | 87.9 | 94.8 | 复用 A1 |
| I2 | Market1501 | reorder only | 待运行 |  |  |  |
| I3 | Market1501 | reorder + Mamba | 待运行 |  |  |  |
| I4 | MSMT17 | reorder only | 待运行 |  |  |  |
| I5 | MSMT17 | reorder + Mamba | 待运行 |  |  |  |

---

### 5.2 IRM 排序准则有效性（新增）

**动机：** I2/I3 只能回答"有无 reorder"，但无法证明排序准则本身的价值。若随机打乱也能得到类似增益，说明提升来自 Mamba 而非排序策略。

| 编号 | 数据集 | 排序方式 | 说明 |
|---|---|---|---|
| I6 | Market1501 | 随机打乱 + Mamba | 对照：排序准则是否必要 |
| I7 | Market1501 | 反向排序 + Mamba | 极端对照：最不重要的 patch 排在前面 |

**结论判断：**

- I3 > I6 ≈ I7：排序准则是关键，Mamba 只是工具。
- I3 ≈ I6 > I7：Mamba 对有序输入更好，但排序方向不重要。
- I3 ≈ I6 ≈ I7：收益主要来自 Mamba 本身，排序几乎无关。

#### 5.2.1 IRM 排序准则结果填写表（滚动更新）

| 编号 | 数据集 | 排序方式 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---|---:|---:|---|
| I6 | Market1501 | 随机打乱 + Mamba | 待运行 |  |  |  |
| I7 | Market1501 | 反向排序 + Mamba | 待运行 |  |  |  |

---

### 5.3 MMC 损失权重 ablation（新增）

**动机：** 验证双 memory 的增益是来自结构设计，还是对权重比例高度敏感。

| 编号 | 数据集 | mean loss 权重 | hard loss 权重 | 说明 |
| --- | --- | :---: | :---: | --- |
| W1 | Market1501 | 1.0 | 0.5 | hard 损失降权 |
| W2 | Market1501 | 1.0 | 1.0 | 等权（默认） |
| W3 | Market1501 | 0.5 | 1.0 | mean 损失降权 |
| W4 | Market1501 | 1.0 | 2.0 | hard 损失加权 |

**目的：**

- 若 W1–W4 结果相近（差异 < 0.5 mAP），说明方法对权重不敏感，鲁棒性强。
- 若差异显著，需找到最优权重并在主实验中使用。

#### 5.3.1 MMC 损失权重结果填写表（滚动更新）

| 编号 | 数据集 | mean loss 权重 | hard loss 权重 | 状态 | mAP | Rank-1 | 备注 |
|---|---|:---:|:---:|---|---:|---:|---|
| W1 | Market1501 | 1.0 | 0.5 | 待运行 |  |  |  |
| W2 | Market1501 | 1.0 | 1.0 | 待运行 |  |  | 默认设置 |
| W3 | Market1501 | 0.5 | 1.0 | 待运行 |  |  |  |
| W4 | Market1501 | 1.0 | 2.0 | 待运行 |  |  |  |

---

### 5.4 Hard sample mining 策略 ablation（新增）

**动机：** "hard memory"的有效性依赖于 hard 样本的定义方式，目前未做对比。

| 编号 | 数据集 | Hard 定义方式 | 说明 |
|---|---|---|---|
| H1 | Market1501 | 全局最难（跨 batch，当前实现） | 默认 |
| H2 | Market1501 | batch 内最难 | 计算更简单的替代 |
| H3 | Market1501 | 按相似度随机加权采样 | 软化版 hard mining |

**目的：**

- 验证当前 hard mining 策略是否确实最优。
- 若 H2 与 H1 结果相近，说明实现可以简化。

#### 5.4.1 Hard sample mining 结果填写表（滚动更新）

| 编号 | 数据集 | Hard 定义方式 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---|---:|---:|---|
| H1 | Market1501 | 全局最难（跨 batch，当前实现） | 待运行 |  |  | 默认策略 |
| H2 | Market1501 | batch 内最难 | 待运行 |  |  |  |
| H3 | Market1501 | 按相似度随机加权采样 | 待运行 |  |  |  |

---

### 5.5 Memory 动量 ablation

| 编号 | 数据集 | `MEMORY_MOMENTUM` | 说明 |
| --- | --- | :---: | --- |
| MM1 | Market1501 | 0.1 | 更新较慢 |
| MM2 | Market1501 | 0.2 | 默认值 |
| MM3 | Market1501 | 0.5 | 更新较快 |
| MM4 | Market1501 | 0.9 | 极端快速更新 |
| MM5 | MSMT17 | 0.2 | 关键复验（默认值） |

**目的：**

- 评估 memory 更新速度对性能的影响。
- 确认当前默认值（0.2）是否处于合理区间。
- 若 0.1–0.5 结果相近，说明该超参数鲁棒。

#### 5.5.1 Memory 动量结果填写表（滚动更新）

| 编号 | 数据集 | `MEMORY_MOMENTUM` | 状态 | mAP | Rank-1 | 备注 |
|---|---|:---:|---|---:|---:|---|
| MM1 | Market1501 | 0.1 | 待运行 |  |  |  |
| MM2 | Market1501 | 0.2 | 待运行 |  |  | 默认值 |
| MM3 | Market1501 | 0.5 | 待运行 |  |  |  |
| MM4 | Market1501 | 0.9 | 待运行 |  |  |  |
| MM5 | MSMT17 | 0.2 | 待运行 |  |  | 默认值关键复验 |

---

## 6. P2 实验：有余力再做

这一组偏工程敏感性，适合作为补充材料或 Appendix，不建议优先消耗主要算力。

### 6.1 训练配置敏感性

| 编号 | 数据集 | 改动项 | 说明 |
|---|---|---|---|
| T1 | Market1501 | `IMS_PER_BATCH: 64`（默认） | 基准 |
| T2 | Market1501 | `IMS_PER_BATCH: 128` | 更大 batch |
| T3 | MSMT17 | `IMS_PER_BATCH: 64` | 跨数据集复验 |
| T4 | MSMT17 | `IMS_PER_BATCH: 128` | 跨数据集复验 |
| T5 | Market1501 | `NUM_INSTANCE: 4`（默认） | 基准 |
| T6 | Market1501 | `NUM_INSTANCE: 8` | 更多难样本 |

**目的：**

- 证明主结论不是 batch 或采样参数偶然带来的。
- 帮助理解 OOM 约束下的最优训练配置。

#### 6.1.1 训练配置敏感性结果填写表（滚动更新）

| 编号 | 数据集 | 改动项 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---|---:|---:|---|
| T1 | Market1501 | `IMS_PER_BATCH: 64`（默认） | 待运行 |  |  |  |
| T2 | Market1501 | `IMS_PER_BATCH: 128` | 待运行 |  |  |  |
| T3 | MSMT17 | `IMS_PER_BATCH: 64` | 待运行 |  |  |  |
| T4 | MSMT17 | `IMS_PER_BATCH: 128` | 待运行 |  |  |  |
| T5 | Market1501 | `NUM_INSTANCE: 4`（默认） | 待运行 |  |  |  |
| T6 | Market1501 | `NUM_INSTANCE: 8` | 待运行 |  |  |  |

---

### 6.2 输入与增强策略

| 编号 | 数据集 | 改动项 | 说明 |
|---|---|---|---|
| E1 | Market1501 | Random Erasing off | 去除遮挡增强 |
| E2 | Market1501 | Random Erasing on（默认） | 基准 |
| E3 | Market1501 | 分辨率 192×96 | 降分辨率 |
| E4 | Market1501 | 分辨率 256×128（默认） | 基准 |

**目的：**

- 评估收益是否严重依赖数据增强。
- 判断输入分辨率变化对 IRM patch 排序的影响是否一致。

#### 6.2.1 输入与增强策略结果填写表（滚动更新）

| 编号 | 数据集 | 改动项 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---|---:|---:|---|
| E1 | Market1501 | Random Erasing off | 待运行 |  |  |  |
| E2 | Market1501 | Random Erasing on（默认） | 待运行 |  |  | 基准 |
| E3 | Market1501 | 分辨率 192×96 | 待运行 |  |  |  |
| E4 | Market1501 | 分辨率 256×128（默认） | 待运行 |  |  | 基准 |

---

### 6.3 模型效率对比（新增）

对比完整模型与 baseline 的计算开销，用于论文效率分析部分。

| 对比项 | Baseline | +IRM | +MMC | 完整模型 |
| ------ | -------: | ---: | ---: | -------: |
| 参数量（M） |  |  |  |  |
| FLOPs（G） |  |  |  |  |
| 推理速度（query/s） |  |  |  |  |
| 训练显存（GB） |  |  |  |  |

**说明：**

- 参数量和 FLOPs 用 `thop` 或 `torchinfo` 统计，取单张输入（256×128）结果。
- 推理速度在单 GPU 上统计 1000 次平均，排除第一次 warm-up。

---

## 7. 推荐执行顺序

建议严格按下面顺序执行，避免实验爆炸。

### 第一步：Market1501 主模块 ablation

跑 `A1–A4`。

- 先拿到最核心的主结果表。
- **决策门：若 A4 未稳定优于 A1（mAP 差 < 1.0），立即停止，排查代码，不继续下一步。**
- 当前状态（`2026-03-31`）：`A4` 最终结果为 `86.6 / 93.7`，低于 `A1` 的 `87.9 / 94.8`，已按决策门暂停后续 `M2-M4` 连跑与 `MSMT17` 迁移，先复核训练与评测设置。

### 第二步：Market1501 MMC 机制 ablation

跑 `M2–M4`（M1 复用 A1）。

- 确认双 memory 优于单 memory，且各自有独立贡献。
- **决策门：若 M4 不明显优于 M2（< 0.5 mAP），优先检查 hard memory 实现，再做 MSMT17 侧。**

### 第三步：Market1501 IRM 机制 ablation

跑 `I2–I3, I6–I7`（I1 复用 A1）。

- 拆清楚 IRM 收益来源，同时验证排序准则的必要性。
- 若 I6（随机排序）已接近 I3（正确排序），需重新审视排序准则设计。

### 第四步：关键实验迁移到 MSMT17

跑 `A5–A8, M5–M7, I4–I5`。

- 不再把所有低优先级实验搬到 MSMT17。
- 重点验证结论在更难数据集上是否仍成立。

### 第五步：P1 超参数 ablation

跑 `W1–W4, H1–H3, MM1–MM5`。

- 验证方法对超参数的鲁棒性。
- 若结果稳定，作为鲁棒性论据写入论文；若不稳定，调整默认值。

### 第六步（可选）：P2 工程敏感性

跑 `T1–T6, E1–E4`，补充效率表格。

---

## 8. 建议最终表格结构

### 表 1：主模块 ablation

| Dataset | Method | IRM | MMC | 状态 | mAP | Rank-1 |
|---|---|:---:|:---:|---|---:|---:|
| Market1501 | Baseline |  |  | 已完成 | 87.9 | 94.8 |
| Market1501 | +IRM | ✓ |  | 已完成 | 88.4 | 95.0 |
| Market1501 | +MMC |  | ✓ | 已完成 | 85.9 | 93.7 |
| Market1501 | CLIMB (Ours) | ✓ | ✓ | 已完成 | 86.6 | 93.7 |
| MSMT17 | Baseline |  |  | 已完成 | 67.8 | 85.2 |
| MSMT17 | +IRM | ✓ |  | 待运行 |  |  |
| MSMT17 | +MMC |  | ✓ | 待运行 |  |  |
| MSMT17 | CLIMB (Ours) | ✓ | ✓ | 待运行 |  |  |

### 表 2：MMC 机制 ablation

| Dataset | Memory Type | 状态 | mAP | Rank-1 | ΔmAP vs FC |
|---|---|---|---:|---:|---:|
| Market1501 | FC classifier | 已完成（复用 A1） | 87.9 | 94.8 | — |
| Market1501 | Mean only | 待运行 |  |  |  |
| Market1501 | Hard only | 待运行 |  |  |  |
| Market1501 | Mean + Hard | 待运行 |  |  |  |
| MSMT17 | Mean only | 待运行 |  |  |  |
| MSMT17 | Hard only | 待运行 |  |  |  |
| MSMT17 | Mean + Hard | 待运行 |  |  |  |

### 表 3：IRM 机制 ablation

| Dataset | Reorder | Sequence Model | 状态 | mAP | Rank-1 |
|---|:---:|:---:|---|---:|---:|
| Market1501 | — | — | 已完成（复用 A1 / I1） | 87.9 | 94.8 |
| Market1501 | Random | Mamba | 待运行 |  |  |
| Market1501 | Reversed | Mamba | 待运行 |  |  |
| Market1501 | Importance | — | 待运行 |  |  |
| Market1501 | Importance | Mamba | 待运行 |  |  |
| MSMT17 | Importance | — | 待运行 |  |  |
| MSMT17 | Importance | Mamba | 待运行 |  |  |

### 表 4：效率对比

| Method | Params (M) | FLOPs (G) | Speed (q/s) | mAP |
|---|---:|---:|---:|---:|
| Baseline | | | | |
| +IRM | | | | |
| +MMC | | | | |
| CLIMB (Ours) | | | | |

## 8.1 当前阶段结论（滚动更新）

- `A2` 相比 `A1` 在 `Market1501` 上有小幅提升，说明 `IRM only` 当前已表现出正向收益。
- `A3` 当前低于 `A1`，说明 `MMC only` 在现阶段设置下尚未体现独立优势，后续仍需结合 `M2/M3/M4` 进一步拆解。
- `A4` 已完成最终评估，当前为 `mAP 86.6 / Rank-1 93.7`，低于 `A1`；按照既定决策门，先暂停 `M2-M4` 串行运行与 `MSMT17` 扩展，优先复核训练与评测设置。
- `A5` 已建立 `MSMT17` baseline，可作为后续 `A6-A8` 和 `M5-M7` 的统一对照基线。

---

## 9. 可视化分析清单（新增）

消融实验结束后，建议补充以下定性分析，强化论文叙事：

| 分析类型 | 对应模块 | 说明 |
|---|---|---|
| Patch 重要性热图 | IRM | 可视化排序前后的 patch 分布，说明 IRM 关注区域合理 |
| Hard sample 示例 | MMC | 展示 hard memory 保存的样本与 mean memory 的差异 |
| Feature 分布（t-SNE） | 整体 | 对比 baseline 与完整模型的类间/类内分散程度 |
| 检索结果示例 | 整体 | 展示完整模型在难样本上的改善（遮挡/光照变化场景） |
| Loss 曲线对比 | 整体 | 验证各 ablation 变体的训练稳定性 |

---

## 10. 结果解释模板

实验结束后，建议按下面的逻辑写结论：

1. 完整模型相对 baseline 的提升幅度（mAP 和 Rank-1 分别报）。
2. IRM 单独带来的提升，以及提升来自排序准则还是 Mamba。
3. MMC 单独带来的提升，以及 mean/hard 各自的贡献比例。
4. 双模块联合是否存在互补（联合增益 > 两者单独增益之和）。
5. Mean+Hard 是否优于任一单 memory，且在 MSMT17 上是否差距更大。
6. 在 MSMT17 上整体增益是否更显著（验证难数据集上的鲁棒性）。
7. 超参数（momentum、损失权重）的敏感性结论，支撑方法鲁棒性声明。

---

## 11. 当前最推荐的最小可执行子集

如果现在只想做一版最有价值、最省时间的当前阶段计划，先只跑下面这 **7 个 `Market1501` 实验**：

| 编号 | 说明 |
|---|---|
| A1 | Market1501 baseline（同时复用为 M1、I1） |
| A2 | Market1501 +IRM only |
| A3 | Market1501 +MMC only |
| A4 | Market1501 完整模型 |
| M2 | Market1501 mean only memory |
| M3 | Market1501 hard only memory |
| M4 | Market1501 mean+hard memory |

> `MSMT17` 相关关键复验（如 `A5/A8/M7`）保留到下一阶段，在 `Market1501` 侧主结论与 `M2-M4` 机制结论稳定后再启动。

这 7 个实验支撑的核心论点：

- 有 baseline 对比（A1 vs A4）
- 有模块各自增益（A2、A3）
- 有 MMC 机制支撑，含 mean/hard 各自贡献（M2、M3、M4）

---

## 12. 执行建议

- `Market1501` 适合先做全 ablation，确认结论方向。
- `MSMT17` 只做关键复验，不建议全扫。
- 当前阶段先不启动 `MSMT17`；待 `Market1501` 侧 `M2-M4` 按统一策略整轮重跑并完成复核后，再恢复 `A6-A8`、`M5-M7`。
- 每次只改一个因素，避免解释混乱。
- 每组 P0/P1 实验至少跑 2–3 次，记录均值 ± 标准差，避免随机波动干扰结论。
- 统一 seed（固定为 3407），所有对比实验使用相同 seed。
- 优先保证日志、checkpoint、最终表格可回溯。
- 每个实验的 config 文件以 `{编号}_{数据集}_{改动描述}.yaml` 命名，统一存放。
- `M2/M3/M4` 恢复运行时统一使用相同 `seed / batch / checkpoint` 策略，只切换 `MMC_MEMORY_MODE`；不再从外部脚本显式覆盖 `SOLVER.EVAL_PERIOD`。
- 本轮已中断的 `M2` 仅保留 `checkpoint_latest.pth.tar` 作为现场，不计入正式结果表。

**下一步可补充的配套文件：**

- `ablation_result_template.md`：结果填写模板
- `experiment_tracker.csv`：实验进度追踪表
- `configs/ablation/`：每个实验对应的 YAML 配置文件
- 一份可直接用于汇报的结果表格骨架（已在第 8 节提供）

---

## 13. 实验结果汇总追踪表（滚动更新）

| 实验编号 | 数据集 | 状态 | mAP | Rank-1 | 备注 |
|---|---|---|---:|---:|---|
| A1 | Market1501 | 已完成 | 87.9 | 94.8 | baseline |
| A2 | Market1501 | 已完成 | 88.4 | 95.0 | IRM only |
| A3 | Market1501 | 已完成 | 85.9 | 93.7 | MMC only |
| A4 | Market1501 | 已完成 | 86.6 | 93.7 | 完整模型；当前低于 A1 |
| A5 | MSMT17 | 已完成 | 67.8 | 85.2 | baseline |
| A6 | MSMT17 | 待运行 |  |  | IRM only |
| A7 | MSMT17 | 待运行 |  |  | MMC only |
| A8 | MSMT17 | 待运行 |  |  | 完整模型 |
| M1 | Market1501 | 已完成 | 87.9 | 94.8 | 复用 A1 |
| M2 | Market1501 | 待运行 |  |  | mean only；`2026-03-31` 已暂停，后续整轮重跑 |
| M3 | Market1501 | 待运行 |  |  | hard only；待 `M2` 重跑后继续 |
| M4 | Market1501 | 待运行 |  |  | mean + hard；待 `M2/M3` 后继续 |
| M5 | MSMT17 | 待运行 |  |  | mean only |
| M6 | MSMT17 | 待运行 |  |  | hard only |
| M7 | MSMT17 | 待运行 |  |  | mean + hard |
| I1 | Market1501 | 已完成 | 87.9 | 94.8 | 复用 A1 |
| I2 | Market1501 | 待运行 |  |  | reorder only |
| I3 | Market1501 | 待运行 |  |  | reorder + Mamba |
| I4 | MSMT17 | 待运行 |  |  | reorder only |
| I5 | MSMT17 | 待运行 |  |  | reorder + Mamba |
| I6 | Market1501 | 待运行 |  |  | 随机排序 + Mamba |
| I7 | Market1501 | 待运行 |  |  | 反向排序 + Mamba |
| W1 | Market1501 | 待运行 |  |  |  |
| W2 | Market1501 | 待运行 |  |  | 默认等权 |
| W3 | Market1501 | 待运行 |  |  |  |
| W4 | Market1501 | 待运行 |  |  |  |
| H1 | Market1501 | 待运行 |  |  | 默认 hard mining |
| H2 | Market1501 | 待运行 |  |  |  |
| H3 | Market1501 | 待运行 |  |  |  |
| MM1 | Market1501 | 待运行 |  |  |  |
| MM2 | Market1501 | 待运行 |  |  | 默认动量 |
| MM3 | Market1501 | 待运行 |  |  |  |
| MM4 | Market1501 | 待运行 |  |  |  |
| MM5 | MSMT17 | 待运行 |  |  | 默认动量关键复验 |
| T1 | Market1501 | 待运行 |  |  |  |
| T2 | Market1501 | 待运行 |  |  |  |
| T3 | MSMT17 | 待运行 |  |  |  |
| T4 | MSMT17 | 待运行 |  |  |  |
| T5 | Market1501 | 待运行 |  |  |  |
| T6 | Market1501 | 待运行 |  |  |  |
| E1 | Market1501 | 待运行 |  |  |  |
| E2 | Market1501 | 待运行 |  |  | 默认增强 |
| E3 | Market1501 | 待运行 |  |  |  |
| E4 | Market1501 | 待运行 |  |  | 默认分辨率 |
