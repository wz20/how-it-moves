---
name: technical-animation
description: Use when explaining technical mechanisms with comic-style animation, Agent feedback loops, retrieval-augmented generation, cache hit/miss flows, or when an agent needs to produce a technical video without writing animation code.
license: MIT
compatibility: Python 3.10+ for recipe compilation and offline HTML; Playwright/Chromium, FFmpeg and system CJK fonts for silent MP4 export. A host capable of files and commands is required. No model API or image service is bundled.
metadata:
  version: "0.4.0"
  author: "Explain Motion contributors"
---

# Technical Animation / How It Moves

原名 Explain Motion；安装目录名保持 `technical-animation`。

**先匹配机制，再选择镜头路径。默认填写内容，不从零写动画；让动作解释因果，而不是给文字配动效。**

## 默认选择：精致漫画，而不是动态技术图

Agent 反馈、RAG、缓存三个机制默认使用 [Illustrated Studio](references/illustrated-mode.md)。它保持初版大机器人、实体终端、档案柜、活页本、快取抽屉等完整素材，让普通模型只填内容。不要用小图标、代码面板和通用圆角框替代已经确认的美术。

```bash
python SKILL_DIR/scripts/illustrate.py init --recipe feedback-retry --out PROJECT_DIR/source.json
python SKILL_DIR/scripts/illustrate.py check PROJECT_DIR/source.json
python SKILL_DIR/scripts/illustrate.py build PROJECT_DIR/source.json --out PROJECT_DIR/v1 --render
```

另外两个 recipe：`retrieval-evidence`、`cache-aside`。默认20/20/22秒；18—40秒、16:9、30/60fps、无声。没有渲染依赖时去掉 `--render`，明确只完成 HTML。

先匹配机制，再选呈现：上述三个机制优先 `illustrate.py`；明确要旧版才用 `recipe.py`；分区检索或明确要架构图再用 `direct.py`。不匹配的新机制使用高级模式，不乱换标签。

**美术和机制独立验收。** 暂停画面应有完整角色/实体道具及层次；动作应保持对象身份。`E_ART_TEXT` 时缩短文字，不缩成小字或退回技术图。素材缺失应报告失败；不得绕过验证器。片头/片尾至少查看实际关键帧，动作中段查看路径、接触和反馈，不能把测试通过说成审美已获用户认可。现有浏览器回退规则适用于此模式。

## v0.3 导演路径：先缩小范围，再展开机制

涉及显式分区、局部检索、并行候选汇总时，先读 [导演模式](references/editorial-mode.md)，使用已实现的 `partition-search`。只修改 [内容 JSON](directing/partition-search.json)，运行：

```bash
python SKILL_DIR/scripts/direct.py init --out PROJECT_DIR/source.json
python SKILL_DIR/scripts/direct.py check PROJECT_DIR/source.json
python SKILL_DIR/scripts/direct.py build PROJECT_DIR/source.json --out PROJECT_DIR/v1
```

它自动生成“概览 → 选中/变暗 → 保留父级并展开 → 并行工作/回传 → 候选排序 → 回到全局”六个镜头，保留查询和对象身份；大卡先收缩再重排，避免途中相撞。支持 `paper-explainer`、16:9、20—40 秒、30/60fps、无声；不是任意题材导演或自动分析视频的模型。MP4 使用下面同一个 `render.py`。

不匹配时回到下列三套机制配方，不为追求画风硬套。所有模式均遵守下面的浏览器回退规则。根据 [真实参考观察](references/reference-milvus.md) 提炼手法，不分发参考视频、截图、音轨或创作者标识。新主题设计先明确“同一对象 → 发生什么变化 → 为什么要切到这个角度”，不要只让机器人一直晃动。

## 原有机制配方的最短路径
命令中的 `SKILL_DIR` 指本文件所在目录，`PROJECT_DIR` 指用户指定的新输出目录。先确定绝对路径，不假设当前工作目录。仅在缺少关键信息时询问。

1. 读 [配方指南](references/recipe-mode.md)，选择**机制匹配**的配方：
   - `feedback-retry`：先失败、根据反馈改动、再验证成功、停止。
   - `retrieval-evidence`：检索候选、选择证据、汇入上下文、带引用回答。
   - `cache-aside`：先未命中、应用回源并填充缓存、相同键再次命中。
   不能把 TCP/训练/并行任务硬套成以上机制。没有匹配项则报告限制，征得同意后进入 [高级模式](references/freeform-mode.md)。
2. 运行 `python SKILL_DIR/scripts/recipe.py init --recipe 配方名 --out PROJECT_DIR/recipe.json`。
   复制生成的完整示例，只修改内容、标题、结论和允许的时长/帧率。不要添加坐标、缓动、时间戳、脚本或私有字段；不要让模型重写运行库。
3. 运行 `python SKILL_DIR/scripts/recipe.py check PROJECT_DIR/recipe.json`。
   按返回的 `code / field / message / hint` 修改**该字段**，最多修复两轮；仍失败则暂停并说明原因，不能改验证器或伪造通过。
4. 运行 `python SKILL_DIR/scripts/recipe.py build PROJECT_DIR/recipe.json --out PROJECT_DIR/v1`。
   得到可直接打开的 `preview.html`、自动分镜、便于复现的项目和素材。输出目录必须不存在；修改时使用 v2/v3，不能覆盖已批准版本。
5. 按下方「浏览器回退」打开预览，检查关键帧和事件衔接。需要 MP4 时先用 `doctor` 检查环境，再运行：
   `python SKILL_DIR/scripts/render.py PROJECT_DIR/v1 --out PROJECT_DIR/v1/video.mp4`。
   未实际导出就只交付 HTML，不能称已生成视频。完整检查按 [审片规则](references/review.md)。

## 浏览器回退

配方、导演与高级模式共用此规则：

- 用户指定浏览器时直接使用指定入口；其他情况按宿主的默认浏览器路由执行。
- **Chrome 首次连接失败、超时、崩溃，或出现 `permission-blocked` / 远程调试授权等待时，立即停止这条连接路径，直接使用当前宿主提供的 ChatGPT／Codex 内置浏览器。** 不把排查 Chrome、运行 doctor、等待或反复点击“允许”作为继续制作的前置条件，也不另开无头 Chrome 来替代这次回退。切换使用已有任务授权，无需再次确认。
- 使用内置浏览器工具返回的实际入口和文档，不猜测 API。首次打开后复用同一浏览器与标签页；切换后不再同时重试旧 Chrome 连接。这里的内置浏览器不指 Browser Use Cloud，不自动创建远程付费浏览器。
- 本地预览先用受支持的文件入口；若该入口无法读取，则仅将项目预览目录通过 `127.0.0.1` 提供给本机内置浏览器，不公开整个工作区、不假定云端可访问 localhost。验证页面标题、播放推进、暂停、拖动与关键画面；检查结束后关闭临时标签页和临时服务。
- **预览能力与视频导出分开验证。** 能播放 HTML 不代表能导出 MP4。内置浏览器只使用其公开支持的截图、下载或导出能力，不通过只读页面接口注入渲染调用。若缺少逐帧导出能力，可使用已具备依赖的确定性导出器；先说明这一具体缺口，再仅回退导出环节，保持原 `project.json` 时间线和帧数验证。
- 当前宿主确实没有内置浏览器入口，或尝试后缺少必需的素材访问、登录态或操作能力时，报告具体缺口，再选择能够完成该环节的已安装工具；只有必须由用户提供访问时才询问。浏览器切换不继承登录态或额外访问权限。

## 不可跳过的边界
- 原有三套配方当前仅支持 **16:9、1920×1080、30/60fps、无音轨、comic-lab**。不支持的要求明确报错，不能偷换画幅、画风或删掉音频。
- 配方时序、对象和状态来自同一事件合同；**到达后才改变状态，成功后停止，结尾保留 2 秒**。不要编辑生成合同或源码绕过这条约束。
- 配方只是原理示意，不执行真实模型/检索/数据库/示例代码。技术真实性、修复是否真的有效、证据是否支持回答，仍须根据用户材料/一手资料核验。
- 不把上下文更新说成训练权重；不保证 RAG 回答正确；缓存示例假设同一键、未过期、未失效，不保证真实延迟或强一致性。
- 原创矢量素材已随配方提供，不需要生图。用户明确要求指定生图时，转对应创作路径；工具不可用必须说明，不能冒充调用。
- `auto`：需求明确时执行上述路径并记录假设；`guided`：在内容和动态预览处确认。付费调用、覆盖文件、公开发布仍须授权及真实可用的工具。
- 程序检查不等于模型评测或观众理解测试；分别记录已验证、未验证。交付声明必须匹配实际文件。

## 按需参考
[输入 Schema](schemas/recipe.schema.json) · [完整 JSON 示例](recipes/feedback-retry.json) · [配方选择与错误修复](references/recipe-mode.md) · [高级自由创作](references/freeform-mode.md) · [视觉系统](references/visual-system.md) · [动作语言](references/motion-language.md)
