# Mechanism-first contract · v0.8

本实现是离散事件教学合同，不是可执行的任意物理公式语言。事件计划先于美术；语义实体、生成的图片资源与场景图层各自保持身份。

## 输入结构

`story.json` 保留 v0.7 字段，新增：

- `presentation`: animated / static。interactive 显式返回 E_INTERACTION_ADAPTER，播放条不冒充教学参数交互。
- `profile`: general / academic。academic 增加 course 台账。
- `mechanism`: version=1，kind=discrete 或 static。

### 离散合同

```json
{
  "version": 1,
  "kind": "discrete",
  "variables": {
    "occupancy": {"type":"enum","values":["empty","full"],"initial":"empty","binding":{"rig":"holder","channel":"state"}},
    "stored": {"type":"set","values":["record"],"initial":[],"binding":{"rig":"holder","channel":"contents"}},
    "copy_origin": {"type":"enum","values":[null,"record"],"initial":null,"binding":{"rig":"copy","channel":"copy"}}
  },
  "events": [
    {"id":"save","action":"save","after":[],"requires":[{"ref":"occupancy","op":"eq","value":"empty"}],
     "effects":[{"ref":"occupancy","op":"set","value":"full"},{"ref":"stored","op":"add","value":"record"}],
     "observation":"看到同一个记录进入内部，主体由空转为有内容。"},
    {"id":"recall","action":"recall","after":["save.commit"],"requires":[{"ref":"stored","op":"contains","value":"record"}],
     "effects":[{"ref":"copy_origin","op":"set","value":"record"}],"observation":"副本被取回；原记录仍在原处。"}
  ],
  "invariants": []
}
```

这是接口示意，必须与当前项目真实 `performance.actions` 的 save/recall 及 holder/record/copy rigs 对应，不是默认素材世界或完整成品。

## 类型与条件

variables 支持 bool、enum、set、number（number 必须有 unit，可声明 min/max）。变化变量必须绑定画面；number 当前主要用于已给定的条件输入，不是公式求解器。set 用有限域中的唯一字符串列表表示。

谓词列表表示 AND，支持 eq/ne/contains/empty/gte/lte。empty 不接受 value。未知字段、非法类型、未知引用和非有限数值被拒绝；不 eval 自定义代码。

effects 仅 set/add/remove；同一事件中不重复写同一变量。无实际变化的效果不通过。自然语言 `consequence` 和 observation 不参与状态求值；其事实是否准确仍由来源核验与审阅负责。

## 事件与动作绑定

每个 performance action 必须有一个同顺序 event，不允许未被机制合同覆盖的教学动作。after 使用此前事件的 start/contact/commit/end。

when=false 跳过对应动作及效果；所有分支语法仍校验。启用事件不能依赖被跳过的事件。执行仍顺序；依赖 contact/commit 是逻辑可用性声明，不会自动产生并行或资源重叠。有限失败/重试使用显式展开的 verify-fail → replace → verify-pass，不支持无限循环。

plan 在无 assets/layers/rigs 时可运行。resolve 再使用现有操作编译器生成实际轨道，并逐事件比较初态、commit 和结束状态。声明为 full 而实际变成其他状态时抛出 E_MECHANISM_DIVERGENCE。

## 可见绑定

- state → rig 当前状态及对应主体图像变体。
- contents → 单槽容器存入的对象集合；不是通用数据库。
- copy → 新副本的原件 ID，原件保留。
- receipts → transfer 接收记录；需指定 `state` 使接收可见，不能只靠脉冲证明已接收。

浏览器审阅从实际 DOM 读取正在显示的图像、透明度和范围，并测试移除该见证层是否改变实际像素。该检查不来自 `compiled_actions` 自报成功，但仍不能判断图片中的内容是否科学正确。完全遮住会阻塞；部分遮挡和微小/误导表达仍须看图。

## 静态关系

仅 SVG 项目使用 kind=static、relations：每项包含 from、to（concept.entities ID）、relation、observation。没有时间变化要求。静态通过不证明对应的动画也合格。

## 常见修复

E_MECHANISM_REQUIRED：先设计事件，不要调大缩放量。  
E_EVENT_DEPENDENCY：修生产者/分支或节点引用，不猜秒数。  
E_NO_CHANGE：这个事件没有变化；合并为观察/停留或设计真实操作，不能写一条空效果充数。  
E_BINDING：把变化绑定到真实物件，不只加字幕。  
E_MECHANISM_DIVERGENCE：查具体变量、事件和实际动作，不改验证器。  
E_VISUAL_OCCLUDED：修层次/遮挡，让已有后果可见。  
E_EVENT_REVIEW：逐事件实际看图及连续过程，记录真实发现。
