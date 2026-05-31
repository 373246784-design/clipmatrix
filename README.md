# 🦞 ClipMatrix — 真实素材批量混剪+口播+发布矩阵

> **用你自己的拍摄素材，AI写口播，自动匹配画面，5种视觉风格，一键发布到TK+IG**

40秒产一条视频，从文案到发布全自动。不是AI生成画面——是用你的真实拍摄素材，AI匹配最合适的片段，HyperFrames引擎渲染，自动发到TikTok和Instagram。

---

<p align="center">
  <b>M1策略 → M1.5文案 → TTS配音 → M2审核 → M3素材匹配 → M4渲染 → M5质检 → M6发布</b>
</p>

## 5种视觉风格

| 🏙️ Velvet | 👨‍👩‍👧 Soft Signal | 🗺️ Shadow Cut | 📋 Swiss Pulse | ⚖️ Comparison |
|:---:|:---:|:---:|:---:|:---:|
| 金色杂志风 | 暖陶土编辑风 | 琥珀路线时间轴 | 蓝调动态排版 | 酒红VS分屏 |
| 城市介绍 | 亲子慢旅行 | 线路定制 | 种草建议 | 对比评测 |

## 能力一览

- 🤖 **AI文案** — DeepSeek生成TikTok风英文口播，自动注入真实信息
- 🎬 **自动剪辑** — 从你的素材库匹配实拍画面，7天去重不重复
- 🎨 **5种风格** — 不同账号不同视觉，告别千篇一律
- 🔊 **TTS配音** — ChatTTS原生发音，男女声可选
- ✅ **自动质检** — 黑帧/音画不同步/字幕重叠，不合格自动打回重做
- 🚀 **一键发布** — Metricool API直推TK+IG，随机偏移防算法识别
- 📊 **批量生产** — 一条命令跑7天×14条，25个账号同时跑

## 实际效果

这套工具正在运营 **21个TikTok/Instagram账号**，日均产出40+条竖屏旅游短视频，累计发布内容覆盖超过14万次播放。

## 安装

```bash
# OpenClaw 用户
openclaw skills install git:373246784-design/clipmatrix

# 直接使用
git clone https://github.com/373246784-design/clipmatrix.git
cd clipmatrix
pip install -r requirements.txt  # TODO
```

## 配置

```bash
cp config.yaml.example config.yaml
# 填入:
#   DeepSeek API Key
#   Metricool Token + User ID
#   素材库路径
```

## 使用

```bash
# 单条生产
python3 scripts/run_and_notify.py 00 2026-06-01 AM

# 批量生产（7天×每天2条）
python3 scripts/batch_runner.py 00 2026-06-01 2026-06-07
```

## 素材库结构

```
library/竖屏/
  成都_熊猫基地_白天_旅拍.mp4
  重庆_洪崖洞_晚上_航拍.mp4
  川西_墨石公园_晴天_航拍.mp4
  ...
```

命名规则：`{方向}_{场景名}_{时间}_{角度}.mp4`。M3会自动按场景名匹配。

## License

**7天免费试用** — 安装后自动开始。试用期内 M1-M5 全部功能开放。

过期后需购买 License Key 解锁：
1. [购买 License](https://zplaze.gumroad.com/l/uunfl)（$15/月）
2. 付款后 Gumroad 发邮件，内含 **Order ID**
3. 把 Order ID 填入 `config.yaml` → `license.key`

## 更多

- [完整工作流文档](references/WORKFLOW.md)
- [故障排查指南](references/TROUBLESHOOTING.md)
