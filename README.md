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

## M1-M6 各阶段详解

| 阶段 | 做什么 | 输入 → 输出 |
|------|--------|------------|
| **M1 策略** | 按方向轮换分配话题，避免相邻视频重复 | 账号配置 → 本轮方向 |
| **M1.5 文案** | DeepSeek生成40-60词TikTok口播（钩子→内容→CTA） | 方向词 → 英文脚本 + 搜索信息注入 |
| **TTS** | ChatTTS原生英文配音，自动清洗特殊字符 | 脚本文本 → .wav音频 |
| **M2 审核** | CTA完整性、句子长度校验、storyboard生成 | 脚本 → 通过/打回 + 分镜表 |
| **M3 匹配** | 场景名→中文关键词→素材库文件名匹配，7天去重 | 分镜场景 → 匹配到的素材文件列表 |
| **M4 渲染** | Chrome headless运行HyperFrames HTML模板，GSAP动画合成 | 素材+字幕+音频 → 1080×1920 MP4 |
| **M5 质检** | 黑帧检测(>1s打回)、音频电平、字幕重叠、场景数量 | 视频 → 通过/不合格原因 |
| **M6 发布** | Metricool API自动排期，随机偏移±30分钟发布 | 视频+文案 → TK+IG双平台上线 |

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
```

编辑 `config.yaml`，填入以下信息：

| 配置项 | 说明 | 在哪获取 |
|--------|------|---------|
| `api.deepseek.api_key` | DeepSeek API Key | [platform.deepseek.com](https://platform.deepseek.com) → API Keys |
| `api.metricool.token` | Metricool Token | Metricool后台 → Settings → API |
| `api.metricool.user_id` | Metricool用户ID | 同上 |
| `paths.library_dir` | 素材库存放路径 | 你自己整理的实拍素材目录 |
| `accounts.id_range` | 账号范围 | 你要跑几个账号就填几个，如 `["00","01","02"]` |
| `directions` | 内容方向列表 | 你的垂直领域话题，如 `["美食","探店","旅行"]` |
| `license.key` | 购买后填Order ID | [Gumroad购买页](https://zplaze.gumroad.com/l/uunfl) |

> 💡 也可用环境变量：`export DEEPSEEK_API_KEY=xxx`、`export METRICOOL_TOKEN=xxx`

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
