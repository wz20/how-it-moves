# 配方模式 / Recipe mode

目的：降低对模型的绘图、排版和动画编码能力的依赖，不承诺提高它对陌生技术的理解能力。模型选择机制并填写内容，预先编写的组件管理动作、时序和构图。

## 先选对机制

| ID | 适合 | 不适合 | 默认/最短 |
|---|---|---|---|
| feedback-retry | 有错误反馈、有实质改动、有再次验证的闭环 | 没有验证的“修完就成功”、训练过程、并行多 Agent | 12s / 10s |
| retrieval-evidence | 查询→相关片段→上下文→带引用回答的推理过程 | 模型训练、重排算法细节、所有片段均相关、无命中文档场景 | 12s / 12s |
| cache-aside | 同一键首次未命中，应用回源填充，缓存有效时再次命中 | 过期、写一致性、击穿、并发失效、read-through 冒充 cache-aside | 14s / 12s |

三个配方是三个独立的机制实现，不是一张流程图换标签。没有匹配项时停止自动套用。高级模式仍可创造新机制，但不能宣称未经测试的新机制已有配方质量保证。

## 文件与命令

从 Skill 根目录运行以下命令，或将 `scripts/recipe.py` 换为绝对路径：

```bash
python scripts/recipe.py list
python scripts/recipe.py init --recipe retrieval-evidence --out /your/project/recipe.json
# 编辑生成的 JSON，只改允许字段
python scripts/recipe.py check /your/project/recipe.json
python scripts/recipe.py build /your/project/recipe.json --out /your/project/v1
# 上一步无需模型 API、Node、浏览器、FFmpeg，也不需要联网
python scripts/recipe.py doctor
python scripts/render.py /your/project/v1 --out /your/project/v1/video.mp4
# build 时就导出视频：增加 --render；缺少渲染依赖会明确失败并保留 HTML
```

`check` 既接受 JSON，也接受 build 产生的项目目录。检查目录时会比较输入、重新编译的事件合同和生成文件校验和。手动改变 `recipe.json` 后必须重新 build；不能只改一半。

## 只填写这些字段

顶层：`schema_version: 1`、`recipe`、`title`、`takeaway`、`content` 必填。`duration`、`fps`、`style`、`aspect`、`audio` 有默认值。任何拼错/未知字段都会报错，不静默忽略。

反馈配方：`goal`、`action`、`failure`、`adjustment`、`success`、`before`、`after`、`decision`。补丁前后必须不同，失败和成功标签必须可区分。样例表示先失败后通过的一种机制；编译器不会执行代码来证明你的补丁正确。

检索配方：`question`、2–3 份 `documents`、`answer`、`citations`。文档有唯一 `id`、短 `text`、布尔 `selected`。至少一份选中，至少一份未选中，以展示相关性筛选。引用只能来自已选中片段，不能引用没有检索到的文档。

缓存配方：`request`、`key`、`value`。布局固定为应用、缓存、数据库：由应用回源和填充，而非缓存自己访问数据库。示例中不包含 TTL、驱逐或写入失效过程，不能把它宣传成完整缓存一致性教程。

## 文字预算

按视觉宽度计费，汉字约 1 单位、ASCII 约 0.6 单位；单位数用于防止已知布局溢出，不是文字字符个数。每个字段的具体上限在 schema 的 `x-visual-units-limit` 以及 CLI 错误中。运行时还会按实际字体测量并换行，超出行数时抛出 `E_LAYOUT`，不缩成不可读小字。

标题应只讲一个机制。长文章应该拆镜头，而不是塞进标题和道具。配方时长上限 40 秒；增加时间不会自动增加知识点。

## 错误修复：只改输入，最多两轮

| code | 含义 | 正确修复 |
|---|---|---|
| E_RECIPE | 没有该配方 | 重新选择；无匹配项转高级模式 |
| E_UNKNOWN | 拼错字段/塞入了坐标 | 删除未知字段，对照完整示例 |
| E_TEXT / E_LAYOUT | 文案过长/不合法 | 缩短相应字段，不压小字体 |
| E_DURATION | 太短/过长/不在完整帧边界 | 使用默认时长或删除知识点 |
| E_CITATION | 引用未选中或重复的文档 | 检查来源；不要为了通过检查随便勾选 |
| E_NO_CHANGE | 修复前后没变化 | 提供真实不同的前后状态 |
| E_CONTRACT / E_FILE_CHANGED | 生成结果被手改 | 保留旧版，从输入重建新版本 |
| E_EXISTS | 输出已存在 | 新建 v2，绝不删除用户确认稿 |
| E_RENDER | 环境/导出失败 | 先保留 HTML，再补齐依赖单独重试 |

不能把“验证器通过”当成“事实正确”。引用集合检查不证明引用内容支持答案；技术内容和实际视觉仍须审查。

## 自动排期与状态

编译器分配整数帧，按事件依赖串联，并固定最后 2 秒为阅读停留。事件的 `end_frame` 不包含在执行区间内；接收和状态变化发生于抵达/完成那一帧。停止区间在上一步决策完成后开始。

动画、字幕和状态测试读取同一份 `project.json.events`，不另写一套时间。Python 和 JavaScript 的状态归约器会在边界帧、中间帧、任意跳转中进行一致性测试。时钟只控制浏览器播放游标，不能影响特定帧画面。

## 交付与测试边界

build 生成：`recipe.json`、`project.json`、`scene.mjs`、`runtime/`、`index.html`、离线 `preview.html`、`storyboard.md`、`build-files.json`。另行导出会增加 `video.mp4` 和 QA JSON。完整工程可复现，不依赖生成它的模型。

本版本没有绑定任何低能力模型或付费 API；只有通过真实模型对比试验，才可谈论跨模型收益。详见 `evals/README.md`。

界面、固定步骤字幕和诊断目前为中文；内容可在预算内使用其他语言。哈希校验用于误改检测，不是防恶意修改的签名机制。
