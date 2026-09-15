---
name: technical-animation
description: Use when making illustrated technical or educational explainers as HTML, MP4 or SVG, especially when new subjects need observable causal actions or university courseware needs source and teacher review.
license: MIT
compatibility: A host with real image generation, visual inspection and file commands; Python 3.10+, Pillow, Playwright/Chromium; FFmpeg/ffprobe for video/audio. No image provider, credentials, physics solver or teacher approval is bundled.
metadata:
  version: "0.8.0"
  author: "How It Moves contributors"
---

# How It Moves · 先有机制，再让新素材把它演出来

**对象执行操作，操作带来可见变化，镜头帮助观察变化。漂亮图片、可播放文件和几何运动都不能单独证明讲解完成。**

这是完整的 v0.8 发布包，不是对任意题材、任意模型或学习效果的保证。支持能力、未验证项目见 [能力边界](references/capabilities.md)。

## 1. 接单与输出

先读取已有资料和明确要求，不反复询问。缺项一次集中确认：受众/先修知识、一个可检验的学习目标、来源与简化边界、时长/画幅、输出形式、声音、客户验收人。高校/课程/教学客户使用 `--profile academic`，填写 [课程需求单](templates/COURSE_WORKORDER.md)。

选择 `html`、`video`（mp4 别名）、`svg`，可多选。HTML 播放条不是参数教学交互；当前参数交互须另做经测试的领域适配器，不伪称已支持。SVG 是静态分层混合图：栅格素材仍是栅格，文字/路径可编辑，不冒称纯矢量。

## 2. 新项目的强制制作顺序

1. **核验机制。** 明确对象、输入、状态、条件、结果、不变量。课程中的公式、单位、假设和适用范围须有来源与学科审阅；不得根据动画速度编造性能或把示意当真实仿真。
2. **先建事件合同。** 在没有图片时写 `mechanism` 与 `performance.actions`。每个关键事件有 requires/after/when、类型化 effects 和 observation。`change/consequence` 是说明，不是状态真相。
3. **操作推导素材。** 运行 `plan` 与 `asset-plan`。从必须看见的动作决定 body、必要状态、部件、入口与遮挡；不机械拆开每件物体。当前容器适配器的 gate/front 不意味着所有技术都要画成柜子。
4. **重新进行主题美术设计。** 提出三套实质不同的视觉世界，说明解释力及误导风险。复用画风/操作，不默认复用角色、柜子或整套构图。见 [主题设计](references/topic-design.md)。
5. **实际生图与看图。** 用真实工具生成独立素材和必要状态，记录真实来源；工具未披露模型名就如实填写。缺少工具或合格素材 `ASSET_BLOCKED`，不能以框＋文本或整页插画推拉降级交付。
6. **测量并绑定。** 对真实图片确认共同画布、视角、尺寸、支点、接触点、前景遮挡与状态图。不能把生成前填的坐标冒充测量。使用 [表演合同](references/performance-contract.md) 与 [机制合同](references/mechanism-contract.md)。
7. **编译并观察。** `check` 核对类型化状态与实际操作编译器的结果，`timeline` 给出 start/contact/commit/end。状态变化不得只在字幕中出现，不能靠推进镜头替代对象操作。
8. **分层审阅。** 查看全部事件的前态、接触、提交、后态及连续过程。再看 labels-only 和 mechanism-only 视图；保留必要标签和有机制意义的粒子，去掉长解释、纯装饰。不能把消融视图的像素差当审美评分。
9. **按格式输出与客户验收。** 经 `export` 生成已审阅媒体；高校客户交付另须教师/学科负责人对同一版本签核。未经教师签核的预览不是客户验收完成。

## 3. 命令路径

`SKILL`、`PROJECT`、`DELIVERY` 使用真实绝对路径；输出均为新目录。

```bash
python SKILL/scripts/create.py init --topic "明确的教学机制" --formats html video svg --profile academic --out PROJECT
# 填 course 的来源/目标，mechanism 的类型化状态与事件，performance.actions；此时不需要图像。
python SKILL/scripts/create.py plan PROJECT --out PROJECT/event-plan-v1.json
python SKILL/scripts/create.py asset-plan PROJECT --out PROJECT/asset-plan-v1.json
# 再按主题填写 concept/style，生成必要主体/部件/状态，不烘焙整页文字。
python SKILL/scripts/create.py prompts PROJECT --out PROJECT/generation-briefs-v1.md
# 宿主真实生图并看图，登记 assets/layers，测量 performance.rigs。
python SKILL/scripts/create.py check PROJECT
python SKILL/scripts/create.py timeline PROJECT --out PROJECT/timeline-v1.json
python SKILL/scripts/create.py review PROJECT --folder review-v1
# 实际查看 draft.html：逐事件播放、完整/少文字/机制视图；有声则听音。
# review.json 初始都是 pending；必须由真实视觉审阅者填写各层及逐事件发现。
python SKILL/scripts/create.py export PROJECT --review PROJECT/review-v1/review.json --out DELIVERY
# 教学客户：准备待签核记录，交给实际教师/学科负责人审阅，不让 Agent 代签。
python SKILL/scripts/create.py handoff-init PROJECT --delivery DELIVERY --out PROJECT/teacher-review-v1.json
python SKILL/scripts/create.py handoff PROJECT --delivery DELIVERY --teacher-review PROJECT/teacher-review-v1.json --out NEW_CLIENT_DELIVERY
```

只要 SVG：初始化 `--formats svg`，`presentation=static`，写结构/关系与 observation，不制造无意义的时间操作。非教学客户可用 general；不得为绕过课程验收把高校项目偷偷改成 general。

## 4. 能做与不能冒称能做

- 已有五类操作：store、retrieve、transfer、verify、replace。transfer 可用明确的新状态表达持久接收；不再只能做接收方的尺度脉冲。
- 类型化布尔/枚举/集合/有单位的输入，受限条件与有限分支；状态效果当前为 set/add/remove，绑定到真实 rig 的 state/contents/copy/receipts。
- 依赖可引用此前事件的 contact/commit/end（也支持 start）；执行仍顺序排期，不能把它说成并行 DAG。
- 同一素材与事件可输出 HTML/视频/混合 SVG；本地音轨、SRT 时点、同源寻帧与 v0.7 动作保持。
- **没有**通用物理仿真、自动科学建模、自动分割/配准、通用教学参数交互、ASR/TTS/音乐节拍识别、IK/3D或增量渲染。连续物理主题要先定义并验证领域适配器，不强套容器。
- 旧几何/矢量案例仅用于内部诊断和历史重放。`topic_output.html/svg` 是低层构建函数，不是生产交付入口；正式 v0.8 交付必须经 `create.py export`。不存在跳过机制或审阅的最终交付选项。

## 5. 三层质量与修复

**技术层：**文件、实际尺寸/帧数、播放/暂停/寻帧、解码、素材加载与来源指纹。  
**事件层：**前置条件、对象身份、分支、接触后提交、类型化效果与运行库结果一致。  
**视觉层：**实际主体参与操作、结果可见、去掉解释/装饰仍能辨认关键变化；足够阅读时间与合理观察顺序。

帧数、位移阈值或 DOM 属性不能代替视觉审阅。实际图层和像素贡献检查会拦截结果被完全遮住等问题，但不能识别所有语义错误或审美失败。每个事件允许有建立/阅读/回顾的静止阶段，不要求一直动。

```bash
python SKILL/scripts/create.py diagnose PROJECT --review PROJECT/review-v1/review.json --out PROJECT/repair-v1.json
```

只修受影响的事件、素材和衔接，再产生新审阅；修改素材/声音/代码/状态后旧批准失效。两轮仍卡住应升级给有视觉能力的作者或教师，不降低阈值，不伪造来源、观察或批准。

## 6. 客户安全与验收底线

来源必须可追溯到具体页/节；claim=verified 不意味着脚本已经核验事实。用客户材料做生图输入、对外发布或加入开源仓库都需相应授权，默认不允许；最小化材料与个人信息。客户课件、照片、音轨、审片意见和账户凭证不进入公共仓库。

高校 handoff 使用单独的 teacher-review.json，绑定源码指纹和实际媒体 manifest。脚本不生成教师签字、不证明签名真实性，学科验收责任仍需真实流程。测试夹具明确阻塞客户 handoff，不能把合成程序测试当真实生图作品。

保留原浏览器路由：指定入口优先；Chrome 首次连接/授权失败时停止该路径，使用宿主实际提供的内置浏览器；不反复索权、猜 API 或公开工作区。预览与确定性导出分开验证。

安装/复现看 [README](README.md)；课程交付看 [Academic delivery](references/academic-delivery.md)；来源、图像生成、机制正确、视觉通过、弱模型成功率、观众学习效果分别记录，未测试就明确 `not_tested`。
