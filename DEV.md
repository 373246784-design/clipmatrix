# DEV.md — ClipMatrix 开发者文档

## API 清单

| API | 用途 | 获取方式 | 配置位置 |
|-----|------|---------|---------|
| DeepSeek | AI文案生成 | [platform.deepseek.com](https://platform.deepseek.com) → API Keys | `config.yaml` → `api.deepseek.api_key` |
| Metricool | 视频发布 | Metricool后台 → Settings → API | `config.yaml` → `api.metricool.token` + `user_id` |
| Gumroad | License验证 | 购买页自动 | `config.yaml` → `license.store_url` |

## 环境变量（可选，优先级高于config.yaml）

```bash
export DEEPSEEK_API_KEY=sk-xxx
export METRICOOL_TOKEN=xxx
export METRICOOL_USER_ID=123456
```

## 依赖

```
openai>=1.0.0
pyyaml>=6.0
requests>=2.28
```

媒体处理（M3/M4/M5）：

```
numpy>=1.24
opencv-python>=4.8
Pillow>=10.0
```

系统依赖：

- **ffmpeg** — 音频提取、GIF生成、质检
- **Chrome** — M4 HyperFrames渲染
- **ChatTTS** — TTS配音（首次运行自动下载模型）

## 文件地图

```
clipmatrix/
├── scripts/
│   ├── production_run.py      # 主控流水线（M1→M6）
│   ├── batch_runner.py        # 批量生产
│   ├── m15_script_generator.py # 文案生成
│   ├── m2_script.py           # 文案审核
│   ├── m3_matcher.py          # 素材匹配
│   ├── m4_hyperframes.py      # HyperFrames渲染
│   ├── m5_qa.py               # 质检
│   ├── m6_publish.py          # Metricool发布
│   ├── tts_engine.py          # ChatTTS配音
│   ├── whisper_align.py       # 字幕对齐
│   ├── m3_bgm.py              # BGM匹配
│   ├── m1_analytics.py        # 数据分析
│   ├── license.py             # License验证
│   └── config_loader.py       # 配置加载
├── config.yaml                # 运行时配置
├── config.yaml.example        # 配置模板
├── references/
│   ├── WORKFLOW.md            # 完整工作流文档
│   └── TROUBLESHOOTING.md     # 故障排查
├── demo/                      # GIF+截图
├── LICENSE.md                 # MIT
└── README.md                  # 产品宣传页
```

## M1-M6 数据流

```
config.yaml → M1(strategy) → accounts.json
                              ↓
                    M1.5(script→TTS+search) → .json + .wav
                                                 ↓
                    M2(review→storyboard) → .json + .txt
                                              ↓
                    M3(match library footage) → matched_clips[]
                                                  ↓
                    M4(render HyperFrames) → .mp4
                                               ↓
                    M5(QA check) → pass/fail
                                     ↓ (pass)
                    M6(publish Metricool) → TK + IG
```

## License 验证逻辑

```
首次运行 → 记录安装时间 → 7天试用
                 ↓
7天后 → 检查 config.yaml → license.key
                 ↓
        有Key → Gumroad Order ID验证
                 ↓
              有效 → 解锁M1-M5
              无效 → sys.exit(1)
```

## 视觉风格

| 风格 | 账号范围 | 色系 | 适用 |
|------|---------|------|------|
| Velvet | 00-04 | 金色 #FFD700 | 城市/奢华 |
| Soft Signal | 05-09 | 暖陶土 #E8775C | 亲子/慢旅行 |
| Shadow Cut | 10-14 | 琥珀 | 线路/攻略 |
| Swiss Pulse | 15-19 | 蓝调 | 种草/建议 |
| Comparison | 20-24 | 酒红 #C53030 | 对比/评测 |
