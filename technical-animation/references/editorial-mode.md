# Editorial directing mode / 内容驱动的多镜头讲解

## 先选机制，不先选皮肤

导演模式补充原有配方，不替代它们。当前只实现 `partition-search`：显式选分区 → 展开其中三个段 → 并行检索 → 等待候选返回 → 排序 → 回到全局。其他主题匹配原有三套配方；仍不匹配才进入高级模式。不要把训练、事务或 Agent 循环改几个标签后冒充这个机制。

**让普通模型负责技术内容，让运行库负责镜头和动作。** 不能改生成的 `scene.mjs`、坐标、事件时间或校验器来绕过输入错误。

## 三条命令生成完整动画

下面命令从仓库根目录运行；安装为 Skill 后用对应绝对路径替换 `technical-animation`。

```bash
python3 technical-animation/scripts/direct.py init --out work/search.json
# 只编辑 work/search.json 的内容
python3 technical-animation/scripts/direct.py check work/search.json
python3 technical-animation/scripts/direct.py build work/search.json --out build/search-v1
```

双击 `build/search-v1/preview.html`：离线、播放/暂停、任意帧拖动，无模型接口、无 CDN、无字体分发。生成 HTML 只需要 Python 3.10+；查看需要浏览器和系统中文字体。

```bash
# 校验生成项目及其来源是否一致
python3 technical-animation/scripts/direct.py check build/search-v1
# MP4 复用现有导出器，依赖 Playwright/Chromium、FFmpeg/ffprobe
python3 technical-animation/scripts/recipe.py doctor
python3 technical-animation/scripts/render.py build/search-v1 --out build/search-v1/video.mp4
```

输出已存在会拒绝，修改使用 `search-v2`，不要覆盖确认稿。预览浏览器与导出能力分开验证，继续遵守 SKILL.md 的浏览器回退规则。没有真正导出 MP4，不能只交付 HTML 却声称“视频已完成”。

## 内容字段与预算

复制 [完整配置](../directing/partition-search.json)，不要自己猜字段。

| 字段 | 约束 |
|---|---|
| schema_version / pattern | `1` / `partition-search` |
| title / query / takeaway | 最多 24 / 8 / 24 个字符，无空白全文、换行、控制字符 |
| groups | 恰好三组；id 全局唯一，label 最多 6 字符 |
| selected_group | 引用一个真实 groups.id，不自动推断路由 |
| segments | 恰好三段；label 最多 4 字符，每段恰好两个候选 |
| candidate id | 英文字母开头，字母数字下划线横线，全局唯一，最多 8 字符 |
| score | 0–1 有限数值，较大更相似，拒绝 bool/NaN；仅示意，非概率 |
| top_k | 整数 1–3；按分数降序，同分按 ID 排序 |
| duration / fps | 默认 24 秒 / 60fps；20–40 秒、30/60fps，总帧数必须为整数 |
| aspect / style / audio | 目前只有 `16:9` / `paper-explainer` / `none` |

所有 ID（含组、段、候选）最长 8 字符；`Q1` 为保留的逻辑查询 ID。未知字段报错，不静默删除。语言预算是当前版式的安全约束，不通过缩到看不清来解决溢出。

## 六个镜头如何协作

1. **Overview:** 三组对象出现，用同一查询建立“范围”问题。
2. **Select:** 目标保持原颜色和位置，其他对象变暗而不消失；查询卡固定，避免缩放切掉输入。
3. **Expand:** 目标父框展开，父级标签保留，内部段逐个揭示；不能把父级展开误画成复制多个分区。
4. **Parallel:** 同一 Q1 发出三个独立调用，抵达后才工作；候选沿回程返回，显示收齐进度。
5. **Rank:** 收齐三个结果后重排候选。大卡先缩成标签、再移动、最后展开，避免多个大框在途中重叠。
6. **Recap:** 回到同一组概览和原查询，显示真实由配置计算出的 TopK。交付后停止发包并保留阅读时间。

动作不靠随机数或之前的播放历史决定；任意寻帧应一致。语义检查、页面状态和视觉动画消费同一份编译事件表。每个阶段最多三个主要焦点，但焦点计数不是观众理解测试。

## 素材与镜头的通用规则

- 先写“名词身份 → 动词变化 → 观察角度”，再画图。角色不是必需品；数据库、分区、记录、索引更适合可展开的结构对象。
- 背景安静、笔触统一、颜色表达职责；不要看到参考中的可爱角色就把每个节点改成机器人。
- 主体、标签、数据、指示线分层。保留对象 ID、父子关系、颜色和局部坐标，转场不能让观众误以为是新对象。
- 只在有观察目的时推近。局部放大后应能回到全局；不要在所有画面上叠循环漂浮和随机镜头。
- 对比必须控制相同输入、对象和尺度，不凭动画播放速度编造性能倍数。
- 剪辑节奏可参考句子边界，但本路径**尚无音频对齐或卡点实现**，不能冒充已经处理声音。
- 参考只提炼表达方法，不上传他人的视频/截图/配音/标识。精确代码、边和状态保持程序可编辑。

## 给能力较弱模型的执行提示

```text
使用 technical-animation 导演模式，讲“显式指定范围后，查询怎样在段内执行并汇总候选”。
复制 partition-search 配置，只改标题、短查询、组标签、候选和结论。
保持原镜头运行库，不写动画代码。先检查 JSON，再生成到新目录。
错误按 code/field/message/hint 修复，最多两轮；机制不匹配就说明，不硬套。
先审预览，具备导出依赖后交付 MP4；没有音频不要承诺卡点。
```

若两轮仍失败，保留错误记录并诊断。`build-files.json` 是误改检测，不是安全签名或恶意内容沙箱。自动时序/布局测试不证明技术正确、弱模型成功率或受众理解；分别核验、分别披露。

## 本次依据

见 [参考视频逐段观察与边界](reference-milvus.md)。新增的是一条可执行的导演路径和可复用原语，并非宣称整套系统已经优于某位创作者。原有 Agent、RAG、缓存、DeepSeek 示例不重做、不覆盖。
