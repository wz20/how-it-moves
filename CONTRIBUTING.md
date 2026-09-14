# Contributing / 贡献指南

欢迎提交能讲清楚一个机制的动画，而不是只让页面更花哨。

## 提交前

先阅读 `technical-animation/SKILL.md`、`references/motion-language.md` 和 `references/review.md`。现有 Agent 示例是参考实现，不是所有选题的固定模版。

新增选题放在 `technical-animation/examples/<topic>/`，包含：

1. `brief.md`：目标观众、唯一核心机制、简化边界与时长。
2. `semantic-map.json`、`project.json`：实体、事件、结果依赖、停止条件和素材来源。
3. `DESIGN.md`、`storyboard.md`、`scene.mjs`：视觉规则、分镜与可寻帧实现。
4. 可播放 HTML、关键帧或短成片，以及实际执行的审片结果。

准确性优先。标明教学模拟，不能把上下文更新画成训练模型，也不能用“工具执行成功”替代“结果已经验证”。不得提交无授权的创作者角色、录屏、字体、音乐或个人照片。

## 新配方贡献（v0.2）

默认配方入口与高级新场景分开维护。新增配方须同时提交：完整内容示例、严格字段 Schema、编译器的机制约束与事件表、独立场景展示、正反例测试及实际渲染。不要只在原场景中替换标签。

检查普通模型是否能只改 JSON 就完成任务；验证事件来源和 Python/JavaScript 状态一致，错误应返回字段与修复提示，而不是要求修改渲染器。事实核验、受众评测和模型成功率实验独立记录，不以单元测试代替。

现有 `docs/index.html` 和原版 MP4 是本次已认可的基准；新配方在 `docs/recipes/` 下添加演示，未经明确批准不替换旧演示。

## 测试

从仓库根目录运行：

```bash
python3 -m unittest discover -s technical-animation/tests
node technical-animation/tests/test_motion.mjs
python3 -m unittest discover -s tests
python3 technical-animation/tests/check_recipe_browser.py --out build/browser-checks
```

改动共享运行库时，重新检查现有例子的任意寻帧一致性。对新作品执行 `validate.py` 和 `render.py`；记录已检查、未检查的范围，不把静态截图检查称为独立受众观看评测。

## 修改演示

`docs/index.html` 是 `technical-animation/examples/agent-loop/preview.html` 的发布副本。修改源场景后，用 `bundle.py` 重建预览，再同步到 `docs/index.html`；需要时更新 `docs/media/` 中的 GIF 和 MP4。两个 HTML 不应各自演化。

发布清单是首发制品的完整性证据，不是自动准许所有新文件公开。文件修改后，先检查 diff、依赖和素材授权，再有意识地重建 `release-files.json`。不要仅为跳过校验而改哈希。

## 报告问题

请附上系统、Python/Chromium/FFmpeg 版本、复现命令、出错时间码、期望与实际结果，以及去除私密信息后的日志。涉及视觉问题时，说明“哪个动作导致了哪种技术误解”。

提交贡献前，请确认你有权按照本项目 MIT 条款提供对应代码、文档与素材。第三方依赖保留其原有许可。
