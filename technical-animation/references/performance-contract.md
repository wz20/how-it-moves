# Semantic performance / 可表演素材与语义动作

## 目标与边界

复用的是“接触—操作—可见后果”，不是机器人、柜子或固定场景。先建立类型化事件和操作需求，再按主题生成所需图层并绑定；源图和派生图的身份保持不变。当前为二维注册图层系统，不是完整三维骨骼、逆向运动学、自动分割或任意动作规划器。

v0.8 正式动画必须同时提供 `mechanism` 和 `performance`；`soundtrack` 仍可选。所有图像必须通过原有生成记录、新鲜度、美术面积和真实审片检查。仅静态 SVG 使用关系合同，不要求 performance。旧手写 keyframe 可作内部诊断，但不能通过 v0.8 正式导出。详见 [机制合同](mechanism-contract.md)。

## 素材到 rig

同一物件的 body、states、gate、front 使用**同一画布、视角、尺寸和对齐位置**。独立生成透明图时保持空白边距，不要逐张裁成紧贴主体，否则支点和遮挡会错位。`asset_pack.py` 只对已对齐的同尺寸图使用同一裁切和缩放；它不能把不同姿势/视角自动配准，不能自动分割肢体。

`assets[].id` 是图像资源编号；可新增 `entity` 指向 `concept.entities[].id`。这样同一技术实体可有多张状态图，不必把每张图谎称成新实体。同一对象的不同状态必须用不同资源，且 entity 相同。

图层可继续用命名 `slot`，或 `box:[x,y,width,height]` 指定归一化舞台区域。不要同时写两套定位。绑定的 body/gate/front 沿用同一根区域；编译器算出屏幕位置。`image_size` 由编译器设置并与实际文件尺寸核对。

### 一个 rig 合同（片段，不是可直接导出的完整工程）

```json
{
  "id": "memory",
  "layer": "memory-body",
  "artboard": [1024, 1024],
  "anchors": {"entry": [0.2, 0.6], "inside": [0.6, 0.6], "output": [0.2, 0.6]},
  "states": {"empty": "memory-empty", "full": "memory-full"},
  "initial_state": "empty",
  "gate": {"layer": "memory-gate", "pivot": [0.1, 0.65], "open_degrees": -35},
  "front": "memory-front"
}
```

这些是接口说明值，**必须按实际生成的物件改端口和支点**；不是通用美术坐标。`entry/inside/output` 表示物件本地画布中的归一化位置。它们会按图像等比缩放、位置、旋转和比例转换到舞台。物件名称和轮廓由主题决定，不是固定叫 memory 或画成柜子。

`gate` 可用 `open_degrees`＋`pivot` 表示旋转开启，也可用 `open_offset:[dx,dy]` 表示沿原图坐标滑开；dx/dy范围±0.6，至少有可见转动或位移。两者可以组合，不把所有新物件都强行当成铰链门。

被传递的对象需一个 `contact` 锚点。衍生副本必须是另一个独立 rig，起始图层 opacity=0，并声明 derived_from。门/盖需要 gate，容器前侧遮挡需要 front。front 必须是真实生成的前景层，不能用文本框替代。前景层自动排在移动对象前面。

当前一层仅属于一个 rig；绑定层不能再有手工 keys/asset_keys，也必须覆盖完整时间线。端口处于主体外、开合过程中被裁切、状态画布不匹配，会阻塞并给出修复阶段。

## 五种已实现的动作

| kind | 必需素材/端口 | 实际编译动作 | 最短时长 |
|---|---|---|---|
| store | object.contact；target.entry/inside、gate、front、empty/full 两状态 | 开启 → 到入口 → 进入遮挡后方 → 状态变满、移动层隐藏 → 合上 | 2.4s |
| retrieve | object.contact；target.inside/output、gate、front；已存原件 | 内部显现副本 → 移到出口 → 返回该副本原来的舞台位置 → 合上；原件保留 | 2.4s |
| transfer | object.contact、target.entry；声明接收时还需目标新状态图 | 预备 → 传输 → 接触；显式 state 产生状态变更和持久 receipt | 1.6s |
| verify | object.contact、target.entry、probe、checking/pass/fail 状态 | 请求到达 → 检测部件扫描 → 显示指定测试结果 → 请求回到原位 | 2.8s |
| replace | object.contact、target.entry、不同目标状态 | 传入对象 → 到达 → 更换为新状态图 → 隐藏传入层 | 2.4s |

store/retrieve 是**单槽容器的教学合同**，不自动实现复杂内存、数据库或检索算法。retrieve 复制的是被确认存入的那一个 ID，不自动判断相似性。verify 的 result 是已核验教学输入，不运行真实测试代码。replace 是可见状态更换，不表示模型权重训练。transfer 的响应不是吞吐或性能证据。

```json
{
  "version": 1,
  "rigs": [],
  "cues": [],
  "actions": [
    {"id":"save","kind":"store","object":"fact","target":"memory","duration":4,
     "caption":"保存这条事实","consequence":"事实进入物件内部，内容状态从空变为已保存。"},
    {"id":"recall","kind":"retrieve","object":"fact-copy","target":"memory","after":["save"],
     "derived_from":"fact","duration":4,"caption":"找回副本，保留原件",
     "consequence":"同一事实的副本离开，原件仍在原物件中。"}
  ]
}
```

rigs 必须填写真实绑定，示例空数组故意不能通过。编译器不给主题分配固定素材。`create.py timeline PROJECT` 输出诊断时序，不是成品。修改素材或性能计划必须重新审片。

## 排期、因果与寻帧

当前底层 action 按列表**顺序执行**；机制事件的 after 可引用此前事件 start/contact/commit/end，编译后保守等待上游动作结束，不声称并行或精确重叠调度。底层 action.after 仍只引用此前动作。没有实现通用 DAG 并行调度，不能把三个 serial 操作说成并行机制。每个动作包含 start/contact/commit/end 与必要临界帧，结果不能早于 commit。整段至少保留1.5秒阅读停留，不通过全片倍速解决短时长。

带 cue 时，该动作使用指定起止时间；后续未锁定动作顺延。时间量化到最近输出帧，偏差最多半帧。明确 cue 冲突或太短会报错；不是任意拖动语音就自动修剪动画。局部时间变化会重编整个确定性时间表，**还不是增量视频渲染缓存**。

`compiled_actions` 是派生诊断信息，不是输入字段。Python/SVG 与 JS 播放器读取同一组生成轨道和离散状态键；任意顺序寻帧应得到相同画面。拒绝靠前一次播放留下的状态决定结果。

## 配音时点与本地音轨

导入用户提供的 SRT：

```bash
python scripts/create.py cue-import --srt narration.srt --out PROJECT/cues.json
```

将结果放入 performance.cues，给动作设置 `cue:"line-1"` 等。这里只读现成时间码；没有转写、强制对齐、自动识别音乐节拍、TTS 或声音克隆。

可选 `soundtrack` 最多一条 narration＋一条 music：

```json
[{"role":"narration","path":"audio/narration.wav","sha256":"填写实际哈希",
  "start":0,"trim_in":0,"trim_out":8,"gain":0.85}]
```

支持本地 WAV/MP3/M4A/OGG/FLAC 音频文件；验证需要 ffprobe，不能提供URL或项目外路径。必须显式指定裁切终点，不能超出文件或工程长度。两轨 gain 之和≤1，防止简单叠加削波；这不是自动响度标准化或混音质量评测。

HTML 内嵌音频，播放/暂停/手动寻帧联动；播放中有约120ms的时钟偏差纠正阈值，不声称浏览器声音采样精确。MP4 由 FFmpeg 按明确裁切、延迟和音量混入AAC，不再只有空音轨。浏览器不支持音频编码时明确报 AUDIO_BLOCKED；不能悄悄静音。SVG 本身没有声音，只有SVG时拒绝未处理的音轨需求。

有音轨的审片额外要求 audio_timing 与 mix_clarity，需实际听音检查；视觉截图、音轨存在、RMS测试都不能替代听音。
