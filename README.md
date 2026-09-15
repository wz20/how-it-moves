<!-- HOW-IT-MOVES:CURRENT:BEGIN -->
## 当前制作入口：v0.8 · 机制优先

先建立事件合同，再推导素材拆分和实际生图；逐事件检查前态、接触、后果及消融视图。高校项目增加来源/公式/目标台账与独立教师签核。

[安装与完整流程](technical-animation/README.md) · [Skill](technical-animation/SKILL.md) · [能力和未验证边界](technical-animation/references/capabilities.md)

下方早期案例作为历史展示保留，不代表已通过 v0.8 新门禁。v0.8 不宣称任意学科自动仿真或学习效果已经验证。
<!-- HOW-IT-MOVES:CURRENT:END -->

<div align="center">

# How It Moves · 让原理动起来

### 让动作讲清技术，而不是让文字动起来。

**为主题设计素材，让过程变成动画与插画。支持 HTML / MP4 / SVG。**

[English](README.en.md) · [原版交互动画](https://wz20.github.io/how-it-moves/) · [三套配方演示](docs/recipes/index.html) · [Skill](technical-animation/SKILL.md) · [MIT](LICENSE)

[![原版 10 秒 Agent 动画，可播放、暂停、拖动](docs/media/agent-loop.gif)](https://wz20.github.io/how-it-moves/)

[离线 HTML](docs/index.html) · [原版 1080p60 MP4](docs/media/agent-loop-10s.mp4)

</div>

点击动画可打开交互预览，支持播放、暂停和逐帧拖动。

## v0.6 · 按主题生图，按需要交付

每个新主题先理解机制、构思三套视觉世界，再通过宿主生图工具生成本项目的主体和可动部件。旧案例用于参考，不再默认把机器人、终端或柜子换标签套到新主题。

- **HTML**：嵌入素材的离线交互动画，支持播放、暂停和逐帧拖动。
- **MP4**：与 HTML 共用素材、对象和时间线；当前视频输出为无声。
- **SVG**：分层静态说明图，含可编辑文字、路径和嵌入图片，不是纯矢量。

```bash
python3 technical-animation/scripts/create.py init --topic "要讲解的机制" --formats html svg --out work/my-topic
# 填写主题构思与分镜，通过宿主生图工具生成素材并登记来源
python3 technical-animation/scripts/create.py prompts work/my-topic --out work/my-topic/generation-briefs.md
python3 technical-animation/scripts/create.py check work/my-topic
python3 technical-animation/scripts/create.py review work/my-topic --folder review-v1
# 实际看图、检查动作后，填写逐镜审阅结果
python3 technical-animation/scripts/create.py export work/my-topic --formats html svg --review work/my-topic/review-v1/review.json --out build/my-topic-v1
```

[输出格式](technical-animation/references/output-formats.md) · [主题设计](technical-animation/references/topic-design.md) · [数据合同](technical-animation/references/production-contract.md)

需要宿主提供生图和视觉审阅能力；初始化与测试不会自动生成真实艺术素材。素材、时间线或导出器变更会使审片记录失效。下方保留的演示来自 v0.1–v0.4，不代表 v0.6 新主题生图的美术验收结果。

## 历史 v0.3：从动态流程图，到有观察重点的多镜头讲解

新增**内容驱动的导演路径**：普通模型填短文案和候选数据，不写 Canvas、镜头坐标或缓动。固定的机制合同与镜头运行库共同保证对象身份、动作先后和读图顺序；不替换已有三个配方或 DeepSeek 演示。

**[▶ 新增 24 秒分区检索演示](https://wz20.github.io/how-it-moves/directed-search.html)** · [演示源码](docs/directed-search.html) · [参考视频逐段分析](technical-animation/references/reference-milvus.md) · [完整使用指南](technical-animation/references/editorial-mode.md)

六个镜头：概览 → 选中分区、其余变暗 → 同一父框展开 → 三路检索/候选回传 → 收齐再排序 → 回到全局。新增有边界的镜头聚焦、逐层揭示、恒速路径传输，以及“收缩—移动—展开”的防重叠重排。浅底细线、语义配色与原创结构道具服务于理解，不复制参考创作者素材。

```bash
python3 technical-animation/scripts/direct.py init --out work/search.json
# 只修改内容；不改生成的场景代码
python3 technical-animation/scripts/direct.py check work/search.json
python3 technical-animation/scripts/direct.py build work/search.json --out build/search-v1
# 双击 build/search-v1/preview.html；具备原有渲染依赖后导出 MP4：
python3 technical-animation/scripts/render.py build/search-v1 --out build/search-v1/video.mp4
```

**实现边界：** 当前导演模式只支持 `partition-search`，恰好三组、选中组内三个逻辑段、每段两个示意候选、Top 1—3；20—40 秒、16:9、30/60fps、静音。不会自动套用到任意架构，也不代表完整 Milvus、真实延迟、物理节点映射或 ANN 精确召回。现有配方仍使用 `comic-lab`，新导演路径使用 `paper-explainer`。弱模型成功率和观众理解尚未实测。

可复现检查见 [v0.3 验证记录](release-checks/v0.3/README.md)。旧版演示与浏览器回退策略保留，参考原视频及截图不提交到开源仓库。

<!-- ILLUSTRATED-STUDIO:BEGIN -->
## v0.4 · 精致漫画素材，不再退化成技术图

保留初版的精致角色与实体道具，重制 Agent、RAG、缓存三个案例。模型只填写内容，素材、表演和构图由运行库提供；不需要普通模型重新写动画代码。自动检查不等于审美、弱模型成功率或学习效果评测。

```bash
python3 technical-animation/scripts/illustrate.py init --recipe feedback-retry --out work/agent.json
python3 technical-animation/scripts/illustrate.py check work/agent.json
python3 technical-animation/scripts/illustrate.py build work/agent.json --out build/agent-v1 --render
```

[Guide / 使用指南](technical-animation/references/illustrated-mode.md) · [All three demos](docs/illustrated/index.html)

18–40s · 1920×1080 · 30/60fps · silent / 无声。Old demos are preserved / 原版保留。
<!-- ILLUSTRATED-STUDIO:END -->

## 动画效果展示

### DeepSeek Harness：插件如何协作 · 10s

[![DeepSeek Harness：插件如何协作](docs/media/deepseek-plugins.gif)](https://wz20.github.io/how-it-moves/deepseek-plugins.html)

高级模式：装入 → 注册 → 调用与回传 → 卸载清理。

[▶ 交互预览](https://wz20.github.io/how-it-moves/deepseek-plugins.html) · [MP4](docs/media/deepseek-plugins.mp4)

### 反馈与重试 · 20s · Illustrated Studio

[![反馈与重试](docs/illustrated/media/feedback-retry.gif)](https://wz20.github.io/how-it-moves/illustrated/feedback-retry.html)

保留初版关节机器人与实体终端；先看反馈，再修改与验证。

[▶ HTML](https://wz20.github.io/how-it-moves/illustrated/feedback-retry.html) · [1080p60 MP4](docs/illustrated/media/feedback-retry.mp4)

### 检索与证据 · 20s · Illustrated Studio

[![检索与证据](docs/illustrated/media/retrieval-evidence.gif)](https://wz20.github.io/how-it-moves/illustrated/retrieval-evidence.html)

档案柜保留原件，证据副本进入活页本，生成机输出带引用的回答。

[▶ HTML](https://wz20.github.io/how-it-moves/illustrated/retrieval-evidence.html) · [1080p60 MP4](docs/illustrated/media/retrieval-evidence.mp4)

### 缓存：未命中与命中 · 22s · Illustrated Studio

[![缓存：未命中与命中](docs/illustrated/media/cache-aside.gif)](https://wz20.github.io/how-it-moves/illustrated/cache-aside.html)

快取柜先打开空抽屉，再保存键值副本；同一个键第二次命中，不再回源。

[▶ HTML](https://wz20.github.io/how-it-moves/illustrated/cache-aside.html) · [1080p60 MP4](docs/illustrated/media/cache-aside.mp4)

<details>
<summary>补充：DeepSeek 插件调用与回传动作测试 · 3s</summary>

![DeepSeek motion test](docs/media/deepseek-plugins-action-test.gif)

[MP4](docs/media/deepseek-plugins-action-test.mp4)

</details>

DeepSeek 示例的[可修改工程](technical-animation/examples/deepseek-plugins/)和[验证边界](technical-animation/examples/deepseek-plugins/README.md)一并开源。它使用高级模式，不是新增的通用插件配方。所有示例为静音机制示意，不是真实运行录像；未做观众理解测试。

## v0.2 改了什么？

上一版让宿主 Agent 自己设计分镜并编写 `scene.mjs`，因此很依赖模型的动画编码与审美能力。

历史 v0.2 配方路径让模型**选择机制配方、填写少量 JSON 内容**。原创矢量角色、素材分层、构图、路径、动作、整数帧排期和结尾停留由代码生成，不再要求普通模型重新发明一套动画。

```text
用户主题 + 可靠资料
       ↓
选择匹配配方 → 完整示例 JSON → 只改内容
       ↓
严格检查 → 自动编译分镜 / 事件 / 素材 / 场景
       ↓
可拖动 HTML → 画面与内容审查 → 高清无声 MP4
```

这不是独立的文生视频模型，也不自动证明技术事实。降低的是动画工程门槛；对陌生技术的理解、引用是否支持答案、观众是否真的学懂，仍须核验。**尚未做弱模型成功率或受众理解效果的对比实验。**

## 兼容保留的旧版配方

| 配方 | 讲清的机制 | 可拖动 HTML | 实际 MP4 |
|---|---|---|---|
| `feedback-retry` | 失败返回 → 修改 → 再次验证 → 停止 | [12 秒演示](docs/recipes/feedback-retry.html) | [1080p60](docs/recipes/media/feedback-retry.mp4) |
| `retrieval-evidence` | 查询 → 选择相关片段 → 上下文 → 引用回答 | [12 秒演示](docs/recipes/retrieval-evidence.html) | [1080p60](docs/recipes/media/retrieval-evidence.mp4) |
| `cache-aside` | 未命中 → 应用回源并填充 → 再次命中 | [14 秒演示](docs/recipes/cache-aside.html) | [1080p60](docs/recipes/media/cache-aside.mp4) |

各配方有自己的布局和动作，不是换标签套图。所有示例为**机制示意、虚构教学数据、无音轨**，不是实时系统执行录屏。Agent 配方不实际执行示例补丁；RAG 例子不训练模型；缓存例子假设同一键未过期且未失效。

## 旧版配方入口（兼容保留）

解压或克隆本仓库后，在仓库根目录运行。**仅生成 HTML 只需要 Python 3.10+，不需要 API key、Node、浏览器安装或付费服务。**

```bash
# 列出支持的机制
python3 technical-animation/scripts/recipe.py list

# 复制一份完整的内容示例，不是空骨架
python3 technical-animation/scripts/recipe.py init \
  --recipe retrieval-evidence --out work/rag.json

# 编辑 work/rag.json 的标题、问题、证据、回答，然后检查
python3 technical-animation/scripts/recipe.py check work/rag.json

# 自动排版、排期、生成可拖动 HTML；输出目录必须是新的
python3 technical-animation/scripts/recipe.py build work/rag.json --out build/rag-v1
```

双击 `build/rag-v1/preview.html` 查看。浏览器中的“播放/暂停”和时间轴均可使用。中文采用系统字体，缺少 CJK 字体时请自行安装合法授权的字体；仓库不分发字体文件。

也可以直接复现内置例子：

```bash
python3 technical-animation/scripts/recipe.py build \
  technical-animation/recipes/cache-aside.json --out build/cache-v1
```

修改时编辑 JSON，然后生成 `build/rag-v2`，不要覆盖确认稿，也不要改生成的 `scene.mjs`。输出目录已存在会报 `E_EXISTS`。

## 一个最小而完整的配置

```json
{
  "schema_version": 1,
  "recipe": "cache-aside",
  "title": "缓存：为什么能少查一次库？",
  "takeaway": "未命中回源，命中直接返回",
  "content": {
    "request": "读取用户42",
    "key": "user:42",
    "value": "Ada"
  }
}
```

其他选项可以不写，脚本有明确默认值。`duration` 默认 12/12/14 秒，配方最短 10/12/12 秒，最长 40 秒；`fps` 为 30 或 60。当前配方仅支持 **16:9、1920×1080、comic-lab、无声**，不会偷偷改成别的比例或删除所需音频。

完整字段与限制：[配方指南](technical-animation/references/recipe-mode.md) · [JSON Schema](technical-animation/schemas/recipe.schema.json) · [完整 JSON 示例](technical-animation/recipes/)

## 安装给 Codex / Claude Code

把**完整的 `technical-animation/` 文件夹**复制到宿主的 Skill 目录，不要只复制 `SKILL.md`。

| 本地宿主 | 用户级路径 | 项目级路径 |
|---|---|---|
| Codex | `~/.agents/skills/technical-animation/` | `.agents/skills/technical-animation/` |
| Claude Code | `~/.claude/skills/technical-animation/` | `.claude/skills/technical-animation/` |

必须使用有本地文件与命令执行能力的宿主。云端会话不会因为你在电脑上放了一个文件夹就自动读取它。更新现有安装前请备份或合并，不要无条件覆盖。

安装后把这段发给模型：

```text
明确复用历史案例时，使用 technical-animation 的配方模式，制作 RAG 讲解动画。
只讲：先检索相关证据，再把问题和证据交给模型，最后带引用回答。
采用内置 comic-lab，16:9，12 秒，完全无声。

先读取配方指南，复制 retrieval-evidence 的完整 JSON，只修改内容。
不要编写 Canvas、坐标、缓动或新的 scene.mjs。
运行检查，最多按字段修复两轮；不匹配配方就说明限制，不硬套。
生成可拖动 HTML，再检查实际画面，有渲染依赖时导出 MP4。
不能把编译检查通过说成事实正确或模型能力已评测。
```

## 导出 MP4

只有视频渲染需要 Playwright/Chromium、FFmpeg/ffprobe 和系统中文字体。

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r technical-animation/requirements.txt
python -m playwright install chromium

# macOS/Homebrew: brew install ffmpeg
# Ubuntu/Debian: sudo apt-get install ffmpeg fonts-noto-cjk
python technical-animation/scripts/recipe.py doctor
python technical-animation/scripts/render.py build/rag-v1 --out build/rag-v1/video.mp4
```

也可以在 `recipe.py build ...` 后追加 `--render`。导出默认 H.264、CRF 16，逐帧绘制，完全无音轨；这是高质量有损编码，不是“无损”。渲染器还会检查解码、帧数、时长、音轨和随机寻帧一致性。既有 Chromium 可通过 `--browser` 或 `CHROMIUM_PATH` 指定。

## 自动检查能做什么？

严格检查字段、类型、文字预算、文档唯一 ID、选中证据/引用关系、输入前后状态、时长和已支持画幅。编译器以整数帧自动排期，最后保留 2 秒；结果抵达后才改变接收方状态。

Python 检查和浏览器播放器消费**同一份事件合同**。生成文件有校验和，修改合同或 runtime 后 `recipe.py check 项目目录` 会报告，不鼓励用改底层代码绕过质量规则。

错误以 `code / field / message / hint` 返回。允许两轮局部修复，仍不通过应暂停诊断，不删验证器。**这些是生产护栏，不是恶意代码沙箱，也不证明引用文字在事实层面支持答案。**

## 高级模式没有消失

新机制、新画幅、新画风或独特镜头可以使用 [高级自由模式](technical-animation/references/freeform-mode.md)，继续复用 [动作库](technical-animation/runtime/) 与原版场景。

```bash
python3 technical-animation/scripts/new_project.py \
  --topic "TCP 拥塞控制" --duration 15 --out ../tcp-explainer
```

这条高级路径仍由宿主核验技术、设计分镜并编写场景，不能宣传成当前三个配方已经覆盖 TCP。新增配方欢迎贡献，但需附机制说明、测试、真实渲染和审片证据。

## 测试、演示与开源

```bash
python3 -m unittest discover -s technical-animation/tests -v
python3 -m unittest discover -s tests -v
node technical-animation/tests/test_motion.mjs
python3 technical-animation/tests/check_recipe_browser.py --out build/recipe-checks
python3 scripts/check_release.py
```

[本版实测记录](release-checks/v0.2/README.md) · [模型评测协议](technical-animation/evals/README.md)。通过本地测试不等于已经在不同模型、不同操作系统或真实受众上证明稳定性。

GIF 为压缩预览，高清动画可下载 MP4。历史案例风格为原创漫画技术解说，不复制其他创作者的角色、标识或视频素材，不声称得到创作者背书。

MIT 许可覆盖本项目原创代码、文档、矢量角色及示例；第三方依赖遵循各自许可证。无字体、个人照片、API key 或浏览器二进制。见 [NOTICE](NOTICE.md)、[贡献指南](CONTRIBUTING.md)、[安全说明](SECURITY.md)。

## GitHub 发布

首发脚本会核对账号、拒绝覆盖已有仓库、扫描敏感文件、检查清单、推送后回读提交，并配置 Pages 的 `main:/docs`。它需要本机有已授权的 GitHub CLI；仅连接只读 GitHub 工具不能创建仓库。

```bash
# 先在浏览器登录，不要把 token 发到聊天或写入仓库
# macOS 尚未安装 GitHub CLI 时：brew install gh
gh auth login --hostname github.com --git-protocol https --web
python3 scripts/publish_github.py --owner wz20 --repo how-it-moves --public
```

[发布说明](docs/PUBLISHING.md)。目标已存在时脚本停止；不删除仓库，不强推，不自动开放私有仓库。只有真实创建并回读成功，才算发布完成。

一手资料：[Agent Skills](https://agentskills.io/specification) · [Skill 编写指南](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [Codex Skills](https://developers.openai.com/codex/skills/) · [Claude Code Skills](https://code.claude.com/docs/en/skills) · [Agent 工具循环](https://www.anthropic.com/engineering/building-effective-agents) · [RAG 论文](https://arxiv.org/abs/2005.11401) · [Cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

**语言与完整性边界：** 标题与业务文字可按长度预算修改；内置步骤字幕、界面和诊断目前为中文。文件哈希用于发现误改和版本不一致，不是签名，也不是防恶意篡改的安全沙箱。
