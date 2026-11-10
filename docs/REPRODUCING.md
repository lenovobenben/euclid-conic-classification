# 复现与文件再生成

## 1. 固定环境

SageMath 使用前四个项目已经采用的 10.7 镜像。

```text
sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528
```

Manim 使用本机已有的 `euclid-min-manim:0.21.0` 镜像，包含 Noto Sans CJK SC 字体。动画目录保留与前项目一致的 Dockerfile，便于在其他机器重建。

## 2. 只读核验

在仓库根目录运行。macOS/Linux 命令如下。

```sh
docker run --rm --network none \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD:/workspace:ro" -w /workspace \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify.py
```

Windows PowerShell 命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/workspace:ro" -w /workspace sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 sage -python experiments/verify.py
```

安装了 SageMath 的环境也可直接执行

```sh
sage -python experiments/verify.py
```

预期退出码为零，报告包含以下字段。

```json
{
  "valid": true,
  "sage_version": "10.7",
  "symbolic_identity_count": 18,
  "fixture_count": 16,
  "point_permutation_count": 1920
}
```

## 3. 更新验证报告与动画数据

将挂载改为可写，并增加 `--write`。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/workspace" -w /workspace sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 sage -python experiments/verify.py --write
```

命令会更新两个文件。

- `experiments/results/verification.json`
- `animations/classification/geometry.json`

报告包含动画数据哈希，用于检查两者是否对应。动画类读取几何数据前也会校验该哈希。

## 4. 渲染动画

从项目根目录执行。720p30 预览命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/manim" -w /manim euclid-min-manim:0.21.0 manim --config_file animations/classification/manim.cfg -r 1280,720 --fps 30 animations/classification/classification.py ConicClassification
```

4K60 母片命令如下。

```powershell
docker run --rm --network none -e PYTHONDONTWRITEBYTECODE=1 -v "${PWD}:/manim" -w /manim euclid-min-manim:0.21.0 manim --config_file animations/classification/manim.cfg animations/classification/classification.py ConicClassification
```

详细分镜、文件位置和播放版说明见 [动画说明](../animations/classification/README.md)。

## 5. 可复现关系

题面和覆盖证明位于 `docs/`，程序核验位于 `experiments/`。几何导出在正式核验全部通过后产生，Manim 从导出文件读取三类案例。

帧率、字体栅格化和视频编码可能随显示环境变化。分类结果、分数字符串、符号验证和 JSON 几何数据在相同源码和固定 Sage 环境中保持可重复。
