# Euclid-Conic-Classification · 由圆锥曲线弧判定曲线类型

**简体中文** · [English](README.en.md)

**用尺规作出两条直径及所需切线，通过平行、相交与同侧关系，判定曲线类别。**

给定一段非零长度的可见弧，已知它属于非圆椭圆、抛物线或双曲线之一。方法覆盖任意长短、含顶点及对称的弧。项目提供完整几何作法、全域证明、SageMath 精确核验和 Manim 动画。

[观看 4K60 作图动画](animations/classification/media/ConicClassification_4k60.mp4) · [完整作图答案](docs/ANSWER.md) · [一般证明](docs/PROOF.md) · [验证报告](experiments/results/verification.json)

[![平行弦、直径与切线的作图判定](animations/classification/preview.png)](animations/classification/media/ConicClassification_4k60.mp4)

## 题目与操作

允许在可见弧上按次序选取四个不同点，允许已作直线与可见弧求交。其余步骤为两点连线、作圆、取交点、作中点和平行线。最终观察已有点线的位置关系。[输入与工具模型](docs/DESIGN.md)

## 实际作图流程

沿可见弧依次选取 $A,B,C,D$。

1. 过 $AB$ 的中点作 $AC$ 的平行线，取得可见弧上的两个交点，连结这两条平行弦的中点，得到直径 $d_1$。
2. 过 $AC$ 的中点作 $AD$ 的平行线，同样得到另一条直径 $d_2$。
3. 若两直径平行，判为抛物线。
4. 若两直径相交，取得中心 $O$，利用已有五点作出 $A$ 处切线 $t$。
5. 比较 $O$ 与 $B$ 相对于切线 $t$ 的位置，同侧为椭圆，异侧为双曲线。

| 最终几何结果 | 曲线类别 |
|---|---|
| 两条直径平行 | 抛物线 |
| 两直径相交，$O,B$ 位于切线 $t$ 同侧 | 椭圆 |
| 两直径相交，$O,B$ 位于切线 $t$ 异侧 | 双曲线 |

所有操作直接产生点和线。平行弦的两个交点一定落在可见弧内，五点切线的平行分支也有明确作法。[完整答案](docs/ANSWER.md) · [五点切线的全部分支](docs/CONSTRUCTION.md)

## 通解与覆盖证明

- 任意四个按弧次序排列的不同点均可使用，两组弦的方向自动不同。
- 两次中点引导保证每条辅助平行线都与可见弧恰交两次。
- 抛物线的两条直径平行且不同，中心型曲线的两条直径唯一交于中心。
- 切线构造覆盖辅助线相交、单对平行、两对平行及最后一步平行的全部情况。
- 中心与另一个弧上点的切线同侧判据对椭圆、双曲线分别给出严格不同的结果。

一般证明覆盖全部题面输入，包含长弧、短弧、顶点、对称和近抛物线情形。最小步数研究暂缓。[完整证明](docs/PROOF.md) · [特殊情形与分支](docs/CASES.md)

## SageMath 精确核验

| 核验部分 | 结果 |
|---|---|
| 几何一般恒等式 | 4 项通过 |
| 几何主流程 | 160 次四点选择及反向次序通过 |
| 五点切线 | 388 次通过，全部平行分支有精确对照 |
| 独立代数核验 | 18 项恒等式与插值见证、16 类输入、1,920 种排列通过 |
| 尺规算术附录 | 95 项通过，另核对零除数拒绝 |

正式重放使用精确有理数与实代数数域 `AA`，所作切线还与原始曲线的梯度独立比较。代数计算的原理与实现集中在 [ALGEBRA](docs/ALGEBRA.md) 和核验程序中。[验证层次与报告](docs/VERIFICATION.md)

## 复现

在项目根目录运行固定 SageMath 10.7 镜像。Windows PowerShell 命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/workspace:ro" -w /workspace sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 sage -python experiments/verify.py
```

预期退出码为零，报告的 `valid` 为 `true`。数据再生成、其他平台命令及动画渲染见 [复现说明](docs/REPRODUCING.md)。

## Manim 动画

4K60 动画时长 75.35 秒。开头一页简述原理，随后连续演示平行弦、弦中点、两条直径、中心、切线和同侧判定。中点和平行线采用常规尺规宏，部分标准辅助圆省略，详细证明在专门文档中展开。

深蓝背景、中文说明、细线及颜色角色沿用前四个项目。洋红为输入，金色为当前作图，淡蓝为辅助，绿色为判定结果。所有图形数据在 SageMath 核验通过后导出，加载时检查哈希。[动画说明](animations/classification/README.md)

## 来源与文档

直接题源与平行弦中点思路来自用户的 `ai-math-notes` 原始问答，原文及后续纠错已按来源保存。前四个已完成项目是本项目在证明、核验和展示方面的重要参考。[来源与贡献范围](docs/LITERATURE.md) · [原始问答](sources/original_conic_qa.md)

| 内容 | 文档 |
|---|---|
| 题面、可见弧与允许操作 | [DESIGN](docs/DESIGN.md) |
| 几何作图答案 | [ANSWER](docs/ANSWER.md) |
| 五点切线与平行分支 | [CONSTRUCTION](docs/CONSTRUCTION.md) |
| 正确性、覆盖性与终止性 | [PROOF](docs/PROOF.md) |
| 特殊位置与通解分类 | [CASES](docs/CASES.md) |
| 代数原理与独立核验 | [ALGEBRA](docs/ALGEBRA.md) |
| 尺规算术附录 | [ARITHMETIC](docs/ARITHMETIC.md) |
| SageMath 核验层次 | [VERIFICATION](docs/VERIFICATION.md) |
| 运行与再生成命令 | [REPRODUCING](docs/REPRODUCING.md) |
| 题源及原始作法 | [LITERATURE](docs/LITERATURE.md) |
