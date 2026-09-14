# v0.2 本地验证记录

## 实际完成

- 50 项 Skill/配方/CLI/输入与交付回归测试通过；11 项公开发布保护测试通过，共 61 项。
- 现有 JavaScript 运动函数测试通过。
- 三个配方使用相同配置分别生成完整 HTML、便携项目与实际 MP4。浏览器在 96 个事件边界/中间帧与 Python 状态归约器一致。
- 每个配方均测试乱序寻帧像素一致、播放推进、暂停冻结、拖动到指定帧；无 JavaScript 错误、无 HTTP 外部请求。
- 实际渲染并完整解码：反馈 720 帧/12 秒、检索 720 帧/12 秒、缓存 840 帧/14 秒；全部 1920×1080、60fps、无音轨。
- 原版已确认的 HTML 和 10 秒 MP4 与上次交付逐字节一致。未将新配方替换为原版演示。
- 所附审片图来自当前配方运行时，人工查看了关键帧布局、标签和前后状态。不将这些检查称为独立受众理解测试。

## 可复现命令

从仓库根目录执行：

```bash
python3 -m unittest discover -s technical-animation/tests -v
node technical-animation/tests/test_motion.mjs
python3 -m unittest discover -s tests -v
python3 technical-animation/tests/check_recipe_browser.py --out build/recheck
python3 scripts/check_release.py
python3 scripts/publish_github.py --owner wz20 --repo explain-motion --public --dry-run
```

浏览器检查依赖 Playwright 与 Chromium，可用 `--browser` 指定。加载方式为 `page.set_content` 的原始独立 HTML，与渲染器一致；本环境的文件 URL 导航受策略限制，因此未声称成功访问 `file://` 或托管 Pages。

## 未验证 / 阻塞

没有执行真实弱模型/低能力 Agent 的 A/B 生成实验；没有跨平台像素一致性实验或观众教学效果评测。减少动画代码编写工作已通过实际 JSON→HTML/MP4 路径验证，但不能由此声称任意模型都能理解任意技术。

GitHub 当前连接只有读接口，目标仓库查询为 404，本地也没有 GitHub CLI 的登录环境。没有创建远程仓库、推送代码或部署 Pages。`publish.command` 与 `scripts/publish_github.py` 是待本机授权后执行的发布助手，不是发布成功的证据。

## 原始证据

- `python-unit.txt` / `publication-unit.txt` / `node-motion.txt`
- `browser.json` / `verification.json` / `review-sheet.jpg`
- `baseline-missing-compiler.txt`、`baseline-missing-cli.txt` 是实现前失败记录。
- `baseline-release-repairs.txt` 记录发现的浏览器检查入口缺失、损坏清单返回原始异常；已修复并纳入回归。
- 每个 MP4 的详细元数据、抽帧哈希和解码记录位于 `docs/recipes/media/*.qa.json`。

哈希证明版本一致性，不是签名或恶意攻击防护。运行日志中的容器路径仅为测试环境信息，不是安装路径要求。

已实际执行公开发布助手命令；返回码 1，明确因缺少 `gh` 停止，未初始化仓库或发起写入。原始输出见 `publish-attempt.txt`。离线 dry-run 已通过。
