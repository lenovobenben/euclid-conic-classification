# 圆锥曲线弧类型判定动画

[观看 4K60 播放版](media/ConicClassification_4k60.mp4)

正式成片为 3840 × 2160、60 fps，时长 97.1 秒，文件约 13.6 MB。

![判别量与曲线类别](preview.png)

## 1. 内容与风格

一个场景 `ConicClassification` 展示完整的五点判定路线及椭圆、抛物线、双曲线三个精确案例。深蓝背景、中文说明、细线及颜色角色沿用前四个项目。

洋红表示免费输入弧及选点，金色表示当前操作，淡蓝表示辅助对象，绿色表示判别量和输出类别。作图使用平行线和有向长度算术宏，宏的尺规实现见 [CONSTRUCTION](../../docs/CONSTRUCTION.md)。

## 2. 分镜

| 阶段 | 内容 |
|---|---|
| 题目 | 给定可见弧，允许弧上选点，目标为曲线类别 |
| 第一个案例 | 选取五点，建立斜标架，画出两个点的平行投影 |
| 二次项 | 展示归一化方程、两个约束行及叉积 |
| 算术宏 | 用 $2\times2=4$ 展示相似三角形乘法 |
| 椭圆结果 | $(a,b,c)\sim(2,2,1)$，$\Delta=-4$ |
| 抛物线案例 | 同一流程得到 $(4,4,1)$，$\Delta=0$ |
| 双曲线案例 | 同一流程得到 $(16,16,3)$，$\Delta=64$ |
| 通解依据 | 无三点共线、五点唯一性、叉积非零与判别量不变性 |

数轴根据该案例的判别量采用对应刻度，结果点放在实际的精确值位置。

## 3. 数据来源

[geometry.json](geometry.json) 由 `experiments/verify.py --write` 生成。精确核验通过后，才把曲线采样点和原始点转换为显示坐标。

五点、斜标架坐标、叉积系数、共同缩放后的整数系数和三个判别结果都来自同一个精确案例。全部 723 个弧采样点也通过原始曲线方程核验。

Manim 读取文件时，与验证报告保存的 SHA-256 比较。哈希不一致会停止渲染。曲线采样和屏幕坐标采用浮点表示，所有类别来自正式精确判定。

## 4. 重新渲染

在项目根目录先生成正式数据。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/workspace" -w /workspace sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 sage -python experiments/verify.py --write
```

720p30 预览和 4K60 母片命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/manim" -w /manim euclid-min-manim:0.21.0 manim --config_file animations/classification/manim.cfg -r 1280,720 --fps 30 animations/classification/classification.py ConicClassification

docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/manim" -w /manim euclid-min-manim:0.21.0 manim --config_file animations/classification/manim.cfg animations/classification/classification.py ConicClassification
```

母片输出到 `media/videos/classification/2160p60/ConicClassification.mp4`。已有镜像包含 Manim 0.21.0 及 Noto Sans CJK SC 字体。其他机器可用本目录 Dockerfile 重建该镜像。

播放版通过 FFmpeg 复制视频流并将 MP4 索引移到文件开头。

```powershell
ffmpeg -n -i animations/classification/media/videos/classification/2160p60/ConicClassification.mp4 -c copy -movflags +faststart animations/classification/media/ConicClassification_4k60.mp4
```

## 5. 视觉检查

先检查 720p30 预览，再检查 4K60 母片的题面、投影、系数、乘法和三类结果画面。检查内容包括中文行距、标签遮挡、公式边界、数轴刻度与实际判别量的一致性。

`preview.png` 来自正式成片。完整文档与一般证明从项目 [README](../../README.md) 进入。
