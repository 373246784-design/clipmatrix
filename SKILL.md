---
name: panda-workflow
description: "TikTok/IG short-video production pipeline: script→TTS→footage matching→render→QA→auto-publish. Batch-run 25 accounts."
metadata:
  openclaw:
    requires:
      bins: ["python3", "ffmpeg", "node"]
      env: ["DEEPSEEK_API_KEY"]
---

# Panda Workflow — TikTok/IG 短视频自动化生产

一款适合内容矩阵运营的视频自动化工具，特别针对旅游/垂直行业做了深度优化。
覆盖从文案生成到多平台发布的完整流水线：M1策略→M1.5文案→TTS→M2审核→M3素材匹配→M4渲染→M5质检→M6发布。

## 快速上手

```bash
# 1. 配置
cp config.yaml.example config.yaml
# 填写: DeepSeek API Key、Metricool Token、素材库路径

# 2. 跑一条测试
python3 scripts/run_and_notify.py 00 2026-06-01 AM

# 3. 批量生产
python3 scripts/batch_runner.py 00 2026-06-01 2026-06-07
```

## 依赖

```bash
# Python
pip install openai pyyaml requests ffmpeg-python

# 系统工具
brew install ffmpeg cwebp
# Chrome 浏览器（M4 渲染需要）

# TTS（二选一）
# ChatTTS（推荐）: pip install ChatTTS
# edge-tts（备用）: pip install edge-tts
```

## 配置文件

所有设置集中在 `config.yaml`，零硬编码：

| 配置块 | 内容 |
|--------|------|
| `accounts` | 账号范围（00-24） |
| `api` | DeepSeek / Metricool 的 API Key 和 URL |
| `feishu` | 飞书通知配置 |
| `paths` | 素材库、成品、模板的路径 |
| `workflow` | 重试次数、TTS上限、黑帧阈值 |
| `video` | 口播词数、编码格式 |
| `directions` | 内容方向轮换列表 |

## 素材库结构

```
library/竖屏/   ← M3 匹配这里
  成都_熊猫基地_白天_旅拍.mp4
  重庆_洪崖洞_晚上_航拍.mp4
  ...
library/横屏/   ← 备选
sounds/         ← BGM 曲库
```

素材命名规则：`{方向}_{场景名}_{时间}_{角度}.mp4`

## 故障排查

| 症状 | 原因 | 解决 |
|------|------|------|
| M4 黑屏 | 素材太短或 storyboard 场景过多 | 降低 `workflow.storyboard_padding` 或换长素材 |
| TTS 超长 | 口播词数 >120 | `video.max_words` 自动截断，或手动删减 |
| DeepSeek 超时 | API 不稳定 | 降低 `workflow.max_retries`，或切 `fallback_model` |
| M3 素材缺口 | `library_dir` 下没有匹配场景 | 补素材，或检查 `directions` 是否和素材文件名一致 |
| M6 发布失败 | Metricool Token 过期 | 重新获取 Token，检查 `api.metricool` |

## 账号管理

`accounts/` 下每个账号一个 JSON 文件：
```json
{
  "account_id": "00",
  "name": "China Unbounded",
  "style": "velvet",
  "orientation": "vertical",
  "gender": "female"
}
```

支持5种视觉风格：`velvet` / `soft_signal` / `shadow_cut` / `swiss_pulse` / `comparison`
