# 第7章 支持向量机与核方法

支持向量机（Support Vector Machine, SVM）是模式识别领域中最为重要的分类与回归方法之一。本章将从最大间隔分类器出发，系统介绍软间隔支持向量机、对偶问题与KKT条件、核技巧、SMO算法、支持向量回归、一类SVM、核PCA、核Fisher判别以及多核学习等内容。

## 7.1 最大间隔分类器

### 7.1.1 间隔的定义

考虑二分类问题，给定训练数据集 $\mathcal{D} = \{(x_1, y_1), (x_2, y_2), \ldots, (x_N, y_N)\}$，其中 $x_i \in \mathbb{R}^d$ 为特征向量，$y_i \in \{-1, +1\}$ 为类别标签。

假设存在一个超平面 $\mathcal{H}: w^T x + b = 0$ 能够将两类样本完全分开，其中 $w \in \mathbb{R}^d$ 为法向量，$b \in \mathbb{R}$ 为偏置项。对于任意样本点 $x_i$，其到超平面的距离定义为：

$$
d(x_i, \mathcal{H}) = \frac{|w^T x_i + b|}{\|w\|}
$$

对于正确分类的样本，有 $y_i(w^T x_i + b) > 0$。我们可以对 $w$ 和 $b$ 进行缩放，使得对于离超平面最近的样本（支持向量），满足：

$$
y_i(w^T x_i + b) = 1
$$

此时，支持向量到超平面的距离为 $\frac{1}{\|w\|}$。两类样本之间的间隔（margin）定义为：

$$
\gamma = \frac{2}{\|w\|}
$$

### 7.1.2 最大间隔优化问题

最大间隔分类器的目标是找到使间隔最大化的超平面，即：

$$
\max_{w, b} \frac{2}{\|w\|}
$$

等价于以下凸优化问题：

$$
\min_{w, b} \frac{1}{2} \|w\|^2
$$

$$
\text{s.t.} \quad y_i(w^T x_i + b) \geq 1, \quad i = 1, 2, \ldots, N
$$

这是一个二次规划问题（Quadratic Programming, QP），目标函数是凸的，约束条件是线性的，因此存在全局最优解。

## 7.2 软间隔支持向量机

### 7.2.1 松弛变量的引入

在实际应用中，数据往往不是线性可分的，或者存在噪声。为了处理这种情况，Cortes和Vapnik提出了软间隔支持向量机，引入松弛变量 $\xi_i \geq 0$，允许部分样本违反间隔约束：

$$
\min_{w, b, \xi} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^{N} \xi_i
$$

$$
\text{s.t.} \quad y_i(w^T x_i + b) \geq 1 - \xi_i, \quad i = 1, 2, \ldots, N
$$

$$
\xi_i \geq 0, \quad i = 1, 2, \ldots, N
$$

其中 $C > 0$ 为惩罚参数，控制对误分类样本的惩罚程度。

### 7.2.2 参数C的物理意义

参数 $C$ 在软间隔SVM中扮演着关键角色：

- 当 $C \to \infty$ 时，问题退化为硬间隔SVM，要求所有样本都正确分类
- 当 $C \to 0$ 时，对误分类的惩罚很小，可能导致欠拟合
- 较大的 $C$ 倾向于选择间隔较小但分类更准确的超平面
- 较小的 $C$ 倾向于选择间隔较大但允许更多误分类的超平面

从结构风险最小化的角度看，$\frac{1}{2}\|w\|^2$ 控制模型复杂度（VC维），$C\sum_{i=1}^{N}\xi_i$ 控制经验风险，$C$ 是两者的折中参数。

## 7.3 对偶问题与KKT条件

### 7.3.1 拉格朗日函数

为了求解软间隔SVM的优化问题，我们构造拉格朗日函数：

$$
L(w, b, \xi, \alpha, \mu) = \frac{1}{2}\|w\|^2 + C\sum_{i=1}^{N}\xi_i - \sum_{i=1}^{N}\alpha_i[y_i(w^T x_i + b) - 1 + \xi_i] - \sum_{i=1}^{N}\mu_i \xi_i
$$

其中 $\alpha_i \geq 0$ 和 $\mu_i \geq 0$ 为拉格朗日乘子。

### 7.3.2 对偶问题的推导

首先，对原变量求偏导并令其为零：

$$
\frac{\partial L}{\partial w} = 0 \Rightarrow w = \sum_{i=1}^{N}\alpha_i y_i x_i
$$

$$
\frac{\partial L}{\partial b} = 0 \Rightarrow \sum_{i=1}^{N}\alpha_i y_i = 0
$$

$$
\frac{\partial L}{\partial \xi_i} = 0 \Rightarrow C - \alpha_i - \mu_i = 0
$$

将这些条件代入拉格朗日函数，得到对偶问题：

$$
\max_{\alpha} \sum_{i=1}^{N}\alpha_i - \frac{1}{2}\sum_{i=1}^{N}\sum_{j=1}^{N}\alpha_i \alpha_j y_i y_j x_i^T x_j
$$

$$
\text{s.t.} \quad 0 \leq \alpha_i \leq C, \quad i = 1, 2, \ldots, N
$$

$$
\sum_{i=1}^{N}\alpha_i y_i = 0
$$

### 7.3.3 KKT条件

对于软间隔SVM，KKT条件包括：

1. **原始可行性**：$y_i(w^T x_i + b) \geq 1 - \xi_i$，$\xi_i \geq 0$
2. **对偶可行性**：$\alpha_i \geq 0$，$\mu_i \geq 0$
3. **互补松弛条件**：
   $$\alpha_i[y_i(w^T x_i + b) - 1 + \xi_i] = 0$$
   $$\mu_i \xi_i = 0$$
4. **平稳性条件**：前面推导的梯度为零条件

从互补松弛条件可以得出重要结论：
- 若 $\alpha_i = 0$，则样本 $x_i$ 不是支持向量
- 若 $0 < \alpha_i < C$，则 $\xi_i = 0$ 且 $y_i(w^T x_i + b) = 1$，样本在间隔边界上
- 若 $\alpha_i = C$，则样本可能被误分类或在间隔内部

## 7.4 核技巧

### 7.4.1 核函数的定义

核技巧的核心思想是将原始特征空间映射到高维特征空间，使得在高维空间中线性不可分的数据变得线性可分。设映射函数为 $\phi: \mathbb{R}^d \to \mathcal{F}$，核函数定义为：

$$
K(x_i, x_j) = \phi(x_i)^T \phi(x_j)
$$

核函数的美妙之处在于，我们可以直接计算高维空间中的内积，而无需显式计算映射 $\phi(x)$。

### 7.4.2 常用核函数

**线性核**：
$$K(x_i, x_j) = x_i^T x_j$$

**多项式核**：
$$K(x_i, x_j) = (x_i^T x_j + c)^p$$

其中 $c \geq 0$ 为常数，$p$ 为多项式次数。当 $p=1, c=0$ 时退化为线性核。

**RBF核（高斯核）**：
$$K(x_i, x_j) = \exp\left(-\frac{\|x_i - x_j\|^2}{2\sigma^2}\right)$$

RBF核对应的特征空间是无穷维的，具有很强的非线性表达能力。参数 $\sigma$ 控制核函数的宽度。

**Sigmoid核**：
$$K(x_i, x_j) = \tanh(\beta x_i^T x_j + \theta)$$

Sigmoid核与神经网络中的激活函数相关，但不满足Mercer条件（半正定性）。

### 7.4.3 Mercer定理

**定理7.1（Mercer定理）**：设 $K: \mathcal{X} \times \mathcal{X} \to \mathbb{R}$ 是一个对称函数，则 $K$ 是一个有效的核函数（即存在映射 $\phi$ 使得 $K(x, x') = \phi(x)^T \phi(x')$）的充分必要条件是：对于任意有限样本集 $\{x_1, x_2, \ldots, x_N\} \subset \mathcal{X}$，对应的核矩阵 $K$（其中 $K_{ij} = K(x_i, x_j)$）是半正定的。

Mercer定理为我们提供了判断一个函数是否为有效核函数的准则。在实际应用中，我们通常直接使用已知的有效核函数，而无需验证Mercer条件。

## 7.5 SMO算法

### 7.5.1 算法原理

序列最小优化算法（Sequential Minimal Optimization, SMO）是由John Platt于1998年提出的，用于高效求解SVM对偶问题。SMO的核心思想是将大规模QP问题分解为一系列小规模QP子问题。

在每次迭代中，SMO选择两个变量 $\alpha_i$ 和 $\alpha_j$ 进行优化，固定其他变量。由于约束条件 $\sum_{i=1}^{N}\alpha_i y_i = 0$，一旦选定 $\alpha_i$，则 $\alpha_j$ 也随之确定。

### 7.5.2 两个变量的优化子问题

假设选定变量 $\alpha_1$ 和 $\alpha_2$，固定 $\alpha_3, \ldots, \alpha_N$。则优化问题简化为：

$$
\min_{\alpha_1, \alpha_2} W(\alpha_1, \alpha_2) = \frac{1}{2}K_{11}\alpha_1^2 + \frac{1}{2}K_{22}\alpha_2^2 + y_1 y_2 K_{12}\alpha_1 \alpha_2 - (\alpha_1 + \alpha_2) + \text{常数项}
$$

$$
\text{s.t.} \quad \alpha_1 y_1 + \alpha_2 y_2 = -\sum_{i=3}^{N}\alpha_i y_i = \zeta
$$

$$
0 \leq \alpha_1 \leq C, \quad 0 \leq \alpha_2 \leq C
$$

通过代入约束条件，可以将问题转化为单变量优化问题，得到解析解。

### 7.5.3 变量选择策略

SMO采用两层启发式方法选择变量：

1. **外层循环**：遍历所有样本，寻找违反KKT条件的样本作为第一个变量
2. **内层循环**：选择使目标函数下降最快的样本作为第二个变量

### 7.5.4 收敛性分析

SMO算法的收敛性基于以下定理：

**定理7.2**：SMO算法在有限步内收敛到最优解。

证明思路：
1. 每次迭代至少使目标函数下降（除非已达到最优）
2. 目标函数有下界
3. 变量 $\alpha_i$ 被限制在有界区域 $[0, C]$ 内

因此，SMO算法必然在有限步内终止。

## 7.6 支持向量回归

### 7.6.1 ε-不敏感损失函数

支持向量回归（Support Vector Regression, SVR）将SVM的思想推广到回归问题。SVR使用 $\varepsilon$-不敏感损失函数：

$$
L_\varepsilon(y, f(x)) = 
\begin{cases}
0, & \text{if } |y - f(x)| \leq \varepsilon \\
|y - f(x)| - \varepsilon, & \text{otherwise}
\end{cases}
$$

其中 $\varepsilon > 0$ 是预设的阈值。只有当预测误差超过 $\varepsilon$ 时，才计算损失。

### 7.6.2 SVR优化问题

SVR的优化问题为：

$$
\min_{w, b, \xi, \xi^*} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^{N}(\xi_i + \xi_i^*)
$$

$$
\text{s.t.} \quad y_i - (w^T x_i + b) \leq \varepsilon + \xi_i
$$

$$
(w^T x_i + b) - y_i \leq \varepsilon + \xi_i^*
$$

$$
\xi_i, \xi_i^* \geq 0, \quad i = 1, 2, \ldots, N
$$

### 7.6.3 对偶问题

SVR的对偶问题为：

$$
\max_{\alpha, \alpha^*} \sum_{i=1}^{N}y_i(\alpha_i - \alpha_i^*) - \varepsilon\sum_{i=1}^{N}(\alpha_i + \alpha_i^*) - \frac{1}{2}\sum_{i,j=1}^{N}(\alpha_i - \alpha_i^*)(\alpha_j - \alpha_j^*)K(x_i, x_j)
$$

$$
\text{s.t.} \quad 0 \leq \alpha_i, \alpha_i^* \leq C
$$

$$
\sum_{i=1}^{N}(\alpha_i - \alpha_i^*) = 0
$$

## 7.7 一类SVM

### 7.7.1 异常检测问题

一类SVM（One-Class SVM）用于无监督的异常检测问题，目标是在只有正常样本的情况下，学习一个决策边界将正常样本与异常样本分开。

### 7.7.2 优化问题

Schölkopf等人提出的一类SVM优化问题为：

$$
\min_{w, \xi, \rho} \frac{1}{2}\|w\|^2 + \frac{1}{\nu N}\sum_{i=1}^{N}\xi_i - \rho
$$

$$
\text{s.t.} \quad w^T \phi(x_i) \geq \rho - \xi_i, \quad i = 1, 2, \ldots, N
$$

$$
\xi_i \geq 0
$$

其中 $\nu \in (0, 1]$ 控制支持向量的比例和异常点的比例。

### 7.7.3 对偶问题

对偶形式为：

$$
\max_{\alpha} -\frac{1}{2}\sum_{i,j=1}^{N}\alpha_i \alpha_j K(x_i, x_j)
$$

$$
\text{s.t.} \quad 0 \leq \alpha_i \leq \frac{1}{\nu N}
$$

$$
\sum_{i=1}^{N}\alpha_i = 1
$$

决策函数为 $f(x) = \text{sign}\left(\sum_{i=1}^{N}\alpha_i K(x_i, x) - \rho\right)$。

## 7.8 核PCA

### 7.8.1 算法原理

核主成分分析（Kernel PCA）将PCA推广到非线性情况。基本思想是将数据映射到高维特征空间，然后在特征空间中执行PCA。

设数据集 $\{x_1, x_2, \ldots, x_N\}$ 已中心化，映射为 $\{\phi(x_1), \phi(x_2), \ldots, \phi(x_N)\}$。特征空间中的协方差矩阵为：

$$
C = \frac{1}{N}\sum_{i=1}^{N}\phi(x_i)\phi(x_i)^T
$$

求解特征值问题 $C v = \lambda v$。由于 $v$ 可以表示为 $\phi(x_i)$ 的线性组合：

$$
v = \sum_{i=1}^{N}\alpha_i \phi(x_i)
$$

代入特征值问题，得到：

$$
K \alpha = N\lambda \alpha
$$

其中 $K$ 为核矩阵，$K_{ij} = K(x_i, x_j)$。

### 7.8.2 投影与重构

对于新样本 $x$，其在第 $k$ 个主成分上的投影为：

$$
z_k = v_k^T \phi(x) = \sum_{i=1}^{N}\alpha_i^{(k)} K(x_i, x)
$$

核PCA可以提取数据的非线性特征，广泛应用于特征提取、降维和数据可视化。

## 7.9 核Fisher判别

### 7.9.1 Fisher判别分析回顾

Fisher判别分析的目标是找到投影方向 $w$，使得类间散度与类内散度之比最大化：

$$
J(w) = \frac{w^T S_B w}{w^T S_W w}
$$

其中 $S_B$ 为类间散度矩阵，$S_W$ 为类内散度矩阵。

### 7.9.2 核Fisher判别

核Fisher判别（Kernel Fisher Discriminant, KFD）将Fisher判别推广到非线性情况。假设 $w = \sum_{i=1}^{N}\alpha_i \phi(x_i)$，则：

$$
w^T S_B w = \alpha^T M \alpha
$$

$$
w^T S_W w = \alpha^T N \alpha
$$

其中 $M$ 和 $N$ 分别为类间和类内散度矩阵在核空间中的表示。

优化问题变为：

$$
\max_{\alpha} J(\alpha) = \frac{\alpha^T M \alpha}{\alpha^T N \alpha}
$$

通过求解广义特征值问题 $M \alpha = \lambda N \alpha$ 得到最优投影方向。

## 7.10 多核学习

### 7.10.1 动机

在实际应用中，单一核函数可能无法充分描述数据的复杂结构。多核学习（Multiple Kernel Learning, MKL）通过组合多个核函数来提高模型的表达能力。

### 7.10.2 基本框架

给定 $M$ 个基核函数 $\{K_1, K_2, \ldots, K_M\}$，多核学习的目标是学习最优的核组合：

$$
K(x_i, x_j) = \sum_{m=1}^{M} \eta_m K_m(x_i, x_j)
$$

其中 $\eta_m \geq 0$ 为核权重，满足 $\sum_{m=1}^{M}\eta_m = 1$。

### 7.10.3 优化问题

多核学习的优化问题通常采用交替优化策略：

$$
\min_{\eta, w, b, \xi} \frac{1}{2}\|w\|_{\mathcal{H}_\eta}^2 + C\sum_{i=1}^{N}\xi_i
$$

$$
\text{s.t.} \quad y_i\left(\sum_{m=1}^{M}\eta_m \sum_{j=1}^{N}\alpha_j^{(m)} K_m(x_j, x_i) + b\right) \geq 1 - \xi_i
$$

$$
\xi_i \geq 0, \quad \eta_m \geq 0, \quad \sum_{m=1}^{M}\eta_m = 1
$$

### 7.10.4 常用方法

1. **简单平均**：$\eta_m = 1/M$
2. **加权平均**：通过交叉验证选择权重
3. **MKL优化**：使用半无限规划或梯度下降优化核权重

## 7.11 本章小结

本章系统介绍了支持向量机与核方法的理论基础。从最大间隔分类器出发，我们推导了软间隔SVM的优化问题及其对偶形式，详细讨论了KKT条件的含义。核技巧的引入使得SVM能够处理非线性问题，SMO算法提供了高效的求解方法。支持向量回归将SVM推广到回归问题，一类SVM用于异常检测。核PCA和核Fisher判别将经典的线性方法推广到非线性情况，多核学习则提供了组合多个核函数的框架。

这些方法构成了模式识别中核方法的完整体系，在文本分类、图像识别、生物信息学等领域有着广泛的应用。

## 参考文献

1. Vapnik V N. The nature of statistical learning theory[M]. New York: Springer, 1995.
2. Cortes C, Vapnik V. Support-vector networks[J]. Machine Learning, 1995, 20(3): 273-297.
3. Platt J. Sequential minimal optimization: A fast algorithm for training support vector machines[R]. Microsoft Research Technical Report MSR-TR-98-14, 1998.
4. Schölkopf B, Smola A J. Learning with kernels: Support vector machines, regularization, optimization, and beyond[M]. Cambridge: MIT Press, 2002.
5. Müller K R, Mika S, Rätsch G, et al. An introduction to kernel-based learning algorithms[J]. IEEE Transactions on Neural Networks, 2001, 12(2): 181-201.
