# technical-animation v0.2

给编程 Agent 的漫画技术动画 Skill。默认配方模式，完整入口见 [SKILL.md](SKILL.md)。

只生成 HTML 需要 Python 3.10+：

```bash
python scripts/recipe.py list
python scripts/recipe.py build recipes/retrieval-evidence.json --out /your/new-project
```

打开输出的 `preview.html`，无需模型 API。模型换主题时先选择匹配配方并修改 JSON；不写坐标、缓动或场景代码。支持反馈重试、RAG 证据汇入、cache-aside 三种机制。

导出 MP4 需 Playwright/Chromium、FFmpeg/ffprobe、系统中文字体：

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/render.py /your/new-project --out /your/new-project/video.mp4
```

默认仅 16:9、1080p、30/60fps、无声、comic-lab。不支持的机制/画幅转高级模式，不能硬套。配方不是事实验证器，也不是实时模型/工具录屏。

[配方指南](references/recipe-mode.md) · [高级模式](references/freeform-mode.md) · [Schema](schemas/recipe.schema.json) · [评测协议](evals/README.md)
