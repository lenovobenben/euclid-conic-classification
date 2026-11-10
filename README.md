# Euclid-Conic-Classification · 由圆锥曲线弧判定曲线类型

**简体中文** · [English](README.en.md)

**从可见弧选取五个不同点，通过有限的尺规操作，判定所属曲线是椭圆、抛物线还是双曲线。**

已知输入属于某条非退化实圆锥曲线，圆按题面约定排除。方法覆盖任意位置的长弧、短弧、含顶点弧和对称弧，任意五个互异选点均可使用。项目提供完整作法、一般证明、SageMath 精确核验及 Manim 动画。

[观看 4K60 动画](animations/classification/media/ConicClassification_4k60.mp4) · [完整答案](docs/ANSWER.md) · [正确性证明](docs/PROOF.md) · [核验报告](experiments/results/verification.json)

[![判别量的符号给出曲线类别](animations/classification/preview.png)](animations/classification/media/ConicClassification_4k60.mp4)

## 题目与输入范围

给定一段非零长度的可见弧 $C$，已知它属于非圆椭圆、双曲线或抛物线之一。允许在弧上选取辅助点，使用无刻度直尺和圆规，有限地确定所属类别。

初始输入仅有可见弧。算法从五个选点建立辅助标架，取得判定所需的有向长度。弧端点是否标记、弧是否含顶点或是否对称，都不影响方法成立。

允许操作和精确相等、次序测试的完整定义见 [题目模型](docs/DESIGN.md)。步数最小化研究暂缓。

## 判定方法

在可见弧上选取五个不同点 $A,B,C_0,D,E$。用前三点建立斜标架

$$A=(0,0),\qquad B=(1,0),\qquad C_0=(0,1).$$

通过平行投影构造 $D=(u,v)$、$E=(w,z)$，再用相似三角形的有向长度算术构造

$$r_1=(u^2-u,uv,v^2-v),\qquad r_2=(w^2-w,wz,z^2-z),$$

$$(a,b,c)=r_1\times r_2,\qquad \Delta=b^2-4ac.$$

| 构造出的判别量 | 输出 |
|---|---|
| $\Delta<0$ | 椭圆 |
| $\Delta=0$ | 抛物线 |
| $\Delta>0$ | 双曲线 |

这些数均用同一条定向直线上的点表示。最终通过判别量点与原点的位置关系完成分类。[完整流程](docs/ANSWER.md) · [尺规算术实施细节](docs/CONSTRUCTION.md)

## 全域通解的依据

- 非退化圆锥曲线上任意三个不同点不共线，因此五个互异点的选取始终合法。
- 五点的二次评价矩阵秩恰为五，方程唯一确定到一个非零倍数，因此两行辅助量始终独立，叉积始终非零。
- 更换标架和缩放方程，只使判别量乘以严格为正的平方因子，其符号保持不变。
- 实非退化圆锥曲线的三个判别量分支分别对应三种类别，输出互斥且完备。

这些结论对任意合法输入和任意合法五点选择成立。几何条件与完整推理见 [证明](docs/PROOF.md)，具体特殊情形见 [分支覆盖](docs/CASES.md)。

## SageMath 精确验证

| 核验 | 结果 |
|---|---|
| 一般符号恒等式及五点插值见证 | 18 项通过 |
| 精确分类案例 | 16 类通过 |
| 全部点名排列 | 1,920 种通过 |
| 有向长度算术宏 | 95 项检查通过，零除数被拒绝 |
| 非法输入对照 | 5 项被拒绝 |
| 独立核验 | 完整方程恢复、原始方程对照、几何交点重放均通过 |

正式判断使用 $\mathbb Q$、符号多项式和实代数数域 `AA`。案例包括参数间距 $10^{-12}$ 的短弧，以及参数为 $\pm10^{-30}$ 的近抛物线曲线。一般输入的覆盖性由证明给出。[验证说明](docs/VERIFICATION.md) · [机器报告](experiments/results/verification.json)

## 复现

在项目根目录运行固定 SageMath 10.7 镜像。Windows PowerShell 命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/workspace:ro" -w /workspace sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 sage -python experiments/verify.py
```

预期 `valid` 为 `true`，退出码为零。数据再生成、其他平台命令和动画渲染见 [复现说明](docs/REPRODUCING.md)。

## Manim 动画

动画为 3840 × 2160、60 fps，时长 97.1 秒。依次展示弧上五点、自建斜标架、平行投影、有向长度乘法和三个分类分支，结尾说明通解的覆盖依据。

沿用前四个项目的深蓝背景、中文说明和细线样式。洋红表示输入，金色表示当前操作，淡蓝表示辅助对象，绿色表示判定结果。动画中的点、系数和类别来自 SageMath 已验证的导出，加载时核对数据哈希。[动画与分镜](animations/classification/README.md)

## 来源与项目定位

题目和原始思路来自 `ai-math-notes` 中的“圆锥曲线作图判定”。原问答中提出平行弦中点、直径、中心及三点夹角判据。本项目保留原文和提出者来源，并记录题面扩展及证明中需要补齐的部分。

当前主解基于经典的五点插值、尺规四则运算与判别量分类，完成了统一有限程序、全域证明、精确核验和展示。[来源与订正](docs/LITERATURE.md) · [原始问答](sources/original_conic_qa.md)

前四个已完成项目提供研究组织、证明、验证和展示风格的参考。[Euclid-Min](https://github.com/lenovobenben/euclid-min) · [Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min) · [Euclid-Equal-Angle-Min](https://github.com/lenovobenben/euclid-equal-angle-min) · [Euclid-Castillon-Min](https://github.com/lenovobenben/euclid-castillon-min)

## 文档入口

| 内容 | 文档 |
|---|---|
| 输入、取点、允许操作与输出 | [DESIGN](docs/DESIGN.md) |
| 完整判定答案 | [ANSWER](docs/ANSWER.md) |
| 尺规算术的实际实施 | [CONSTRUCTION](docs/CONSTRUCTION.md) |
| 正确性、覆盖性、终止性 | [PROOF](docs/PROOF.md) |
| 特殊输入与分支 | [CASES](docs/CASES.md) |
| 验证层次和结果 | [VERIFICATION](docs/VERIFICATION.md) |
| 命令与环境 | [REPRODUCING](docs/REPRODUCING.md) |
| 来源、原作法与订正 | [LITERATURE](docs/LITERATURE.md) |
| 原始问答快照 | [sources](sources/README.md) |
