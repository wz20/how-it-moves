# Illustrated Studio · 精致漫画模式

默认用于 Agent 反馈、RAG 证据、cache-aside 三种机制。**素材质量与技术正确性分开验收，不能用动态技术图替代精致漫画。** 保留初版机器人和实体终端；新道具提供外壳、侧面、纸张、螺丝、手柄、印刷层次和可独立运动部件。

## 三条命令
```bash
python3 technical-animation/scripts/illustrate.py init --recipe feedback-retry --out work/agent.json
python3 technical-animation/scripts/illustrate.py check work/agent.json
python3 technical-animation/scripts/illustrate.py build work/agent.json --out build/agent-v1 --render
```
另外两种 recipe 是 `retrieval-evidence`、`cache-aside`。默认 20 / 20 / 22 秒、1920×1080、60fps、无声。可调整为18—40秒、30或60fps；输出必须新目录。无导出依赖时去掉 `--render`，得到离线 `preview.html`，不能声称已生成MP4。复用原 `render.py`。

## 模型只改内容，不能降低美术标准

复制完整 JSON 示例。机制校验仍来自 `recipe_core.py`，动作与状态读取同一个事件表；新模式不会执行真实测试/检索/数据库。固定剧情是示意，不保证真实业务结果。

沿用原字段；为实体纸张增加更严格文字上限（汉字宽度单位，英文按0.6计）：问题14、证据每段10、证据ID为2、回答13、缓存键7.5。其他字段沿用原 schema。超预算返回 `E_ART_TEXT`，缩短内容，不把字缩到不可读。

- Agent：原关节机器人、实体测试机、任务夹板、上下文纸本；先收到反馈再决定修复，重新验证后才完成。
- RAG：档案柜保留原件，选中资料的副本带相同 ID 飞入活页本，生成机输出有引用的纸张。不是把原文从库中删除，更不是修改模型权重。
- Cache：同一键第一次打开空抽屉，应用回源并保存副本，第二次抽屉中有值；数据库计数不再增加。假设未过期、未失效，不宣称速度倍数。

## 美术锁定（Art lock）

`studio-art.mjs` 与原始 `rigs.mjs` 是素材来源；`illustrated-player.mjs` 是表演和构图；`illustrate.py` 生成内容合同。旧素材和三个旧配方不覆盖，`paper-explainer` 仍是可选架构图路径，不再作为三条漫画案例的默认。

模型不得把机器人替换成小图标，把机器换成代码面板，把档案换成无造型矩形。缺少素材或运行文件应失败并报告，不隐式回退为技术图。新主题应沿用可分层素材，或明确走高级模式建立新素材，而不是给每个节点画眼睛。

## 五个审片问题

1. 暂停一帧，角色与道具有可辨认的轮廓、体积、细节吗？
2. 运动前后还是同一件道具吗？标签、数据和 ID 是否连续？
3. 动作真的触发状态变化，还是只有文字在移动？
4. 特写有没有切掉主体、手脚、纸张或字幕？
5. 去掉装饰后技术正确，保留装饰后是否仍有清楚的视觉主次？

程序校验不能自动回答第一、第五个问题。交付前必须查看实际关键帧和过渡帧；代码测试不等于审美、弱模型成功率或观众学习效果评测。

## 验证与复现

```bash
python3 -m unittest discover -s technical-animation/tests -p 'test_illustrate.py' -v
python3 technical-animation/tests/check_illustrated.py --out build/illustrated-qa
python3 scripts/render_illustrated_showcase.py
```

第三条会重新生成 `docs/illustrated/` 中三条视频/GIF/HTML，更新中英文 README 的对应展示和文件清单；它不会推送 GitHub。仓库的专用 workflow 才会对已授权的主分支执行非强制推送。原片、人物照片、他人素材、字体和凭证均不分发。
