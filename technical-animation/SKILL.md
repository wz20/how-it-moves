---
name: technical-animation
description: Use when producing illustrated technical explainers as interactive HTML, MP4 video or SVG images, especially for new topics that must not collapse into reused mascots, diagrams or slides.
license: MIT
compatibility: A host with image generation, visual inspection and local commands. Python 3.10+ and Pillow; Playwright/Chromium for review capture, plus FFmpeg/ffprobe for MP4. No model API or provider credentials are bundled.
metadata:
  version: "0.6.0"
  author: "How It Moves contributors"
---

# How It Moves · 按主题生成，而不是固定素材换标签

**先决定交付形式，理解机制，再为本主题设计并生成素材。能复用的是画风、动作和工具，不是默认复用那几个机器人、终端和柜子。**

## 1. 先选输出，不把所有请求都当视频

支持 `html`、`video`（命令也接受 `mp4`）、`svg`，可多选。用户已经指定时直接执行；没有指定时只问一次“要可交互 HTML、MP4 视频、SVG 图片，还是多种？”不要反复确认已有信息。

- **HTML**：独立离线文件，播放、暂停、逐帧拖动；实际图片嵌入，不依赖 CDN。
- **视频**：MP4，与 HTML 使用同一素材、对象 ID 和时间线；仅此格式需要 FFmpeg。当前适配器无声，不偷偷丢弃用户要求的音轨。
- **SVG 图片**：独立静态文件，选择已审阅的 `poster_frame`。图片、文字、路径分别成层，可编辑文字和结构；生图 PNG/WebP/JPEG 以图像层嵌入，**不是纯矢量、不是自动描摹，更不能把整张截图套进 SVG 冒充可编辑插画**。

仅要 SVG 就设计一张完整、好看的说明插画；不要做 42 秒动画再截一帧糊弄。多格式交付可共享艺术资产与核心语义，但新画幅必须重构图。详细入口见 [输出格式与命令](references/output-formats.md)。

## 2. 每个新主题都重新进行视觉构思

先读 [主题联想与素材生成](references/topic-design.md)，执行：

1. 用一句话确认观众应该理解的机制；确定实例、状态、因果、不可误画的事实。
2. 提出 **3 套真正不同的视觉世界**，各写“为什么合适、可能误导什么”，选择最有解释力的一套。不是同一个柜子换三种颜色，也不是从 Skill 内置图标表查主题。
3. 给每个技术实体写：**技术含义 → 具体主体 → 操作 → 可见后果 → 必须保持的身份/事实**。主角不一定是人物；道具也不一定是机器。根据主题决定材质、空间、轮廓与光线。
4. 查看当前工作区以往交付的 `asset-history-entry.json`，将相关记录放入 `history`，避开最近用过的主视觉与素材。默认 `fresh`：为当前 `project_id` 实际生成新图。改标题、改文件名、改颜色不能算新素材。
5. 用宿主**真实可用的生图工具**生成独立主体、可动部件和必要状态；记录真实 tool/model/run reference/prompt 与文件哈希。指定模型不可用就说明，不能伪称调用。
6. 查看素材和代表性构图，再制作动作。生图时不烘焙大段技术文字；数值、代码、标签和必要路径由程序绘制。

**跨项目复用默认拒绝。** 只有用户明确要求同一个品牌角色/素材，才能在 `reuse_consent` 中记录具体 asset IDs 和真实请求出处。沿用一种画风不等于允许复用图片。同一项目内，同一对象的图、姿势和状态应该保持一致，不要每个镜头换主角。

缺少生图能力/真实素材：`ASSET_BLOCKED`，留下分镜和生成提示，停止最终交付。不能切换到旧矢量案例、通用图标、框＋文本或整图平移充数。

## 3. 当前制作入口

`SKILL` 是本目录，`PROJECT` 是新目录。先初始化，填写完整的主题概念与分镜，生成真实素材；初始化不是成品。

```bash
python SKILL/scripts/create.py init --topic "要讲解的机制" --formats html svg --out PROJECT
# 填写 story.json 中 concept/style，按真实主题构思，不复制示例世界。
python SKILL/scripts/create.py prompts PROJECT --out PROJECT/generation-briefs.md
# 宿主调用实际生图工具。登记真实 assets、generation、shots、layers。
python SKILL/scripts/create.py check PROJECT
python SKILL/scripts/create.py review PROJECT --folder review-v1
# 实际检查 review-v1 的图与 draft.html 的动作；记录每镜头具体发现，不能自动批准。
python SKILL/scripts/create.py export PROJECT --formats html svg \
  --review PROJECT/review-v1/review.json --out NEW_DELIVERY
```

视频改选 `video`；三种一起选 `html video svg`。只生成请求的形式，不擅自增加 MP4。新目录输出，不覆盖已批准版本。读 [数据合同](references/production-contract.md)，不要猜字段；默认可用命名位置与关键帧，不要求宿主写动画代码。讲解结构和新题材的视觉设计仍由宿主负责，不声称任意弱模型输入标题就一定出优秀作品。

## 4. 三种形式共用质量线

- 主体必须实际出现在画面；背景或角落吉祥物不算。若去掉文字就完全不知道对象是什么，返工。
- 不是给每个矩形画眼睛、加螺丝就合格；不是生一整张 PPT 再当图片移动。
- 动画必须展示操作及其后果；位移/缩放只是实现手段。静态 SVG 应用对象关系、局部结构或同一实例的前后状态说明机制，不靠段落列表。
- 检查真实素材、项目新鲜度、完整镜头、画面中的对象尺度、可读性及实际审片证据。`check` 通过不等于漂亮或技术事实正确。
- `review` 只生成 `pending`。人或具备视觉能力的 Agent 看图并检查动作后，才能填写批准和具体发现。文字模型不能冒充看图。
- 改素材、文字、时间线或导出器后审片失效；所有 final exports 均经 `create.py export`。不能换格式、换脚本来绕过不合格结果。
- 当前布局面积检查是启发式，不能识别所有“PPT 栅格化”“不相关大图”或遮挡。必须用视觉审片补足，不能承诺绝不出现任何 badcase。

## 5. 浏览器、历史案例与事实边界

优先用户指定的浏览器，否则用宿主默认入口。Chrome 首次连接失败/授权阻塞就停止该路径，改用实际提供的内置浏览器；不循环请求权限，不猜 API，不公开整个工作区。预览能力与导出能力分开验证；缺少逐帧导出时仅对导出环节采用已安装的确定性工具，不继承登录态。

`illustrate.py`、`recipe.py`、`direct.py` 和原有案例保留为历史作品与机制/动作参考，**不再是新任务绕过主题构思和生图的默认入口**。不要把它们的三个固定素材世界照搬到 Mem0、事务、网络或任意新主题。

不把上下文更新画成训练权重；不凭动画速度声称性能倍数；不把模拟说成真实运行。来源记录不是防伪签名，程序测试不是美术验收/弱模型评测/观众学习测试。本轮实现未捆绑生图服务或声称调用某种模型；工具选择、费用和公开发布仍遵守用户授权。
