# DeepSeek Harness · 插件原理

[离线交互预览](preview.html) · [10秒MP4](../../../docs/media/deepseek-plugins.mp4) · [3秒动作测试](../../../docs/media/deepseek-plugins-action-test.mp4)

使用高级模式制作，不属于三种现成配方。主时间线为 project.json，场景为 scene.mjs；runtime 为 Explain Motion 原创 MIT 运行库。

从仓库根目录复现（需已安装官方渲染依赖）：

```bash
python3 technical-animation/scripts/validate.py technical-animation/examples/deepseek-plugins
python3 technical-animation/scripts/render.py technical-animation/examples/deepseek-plugins --out build/deepseek-plugins.mp4
```

## 边界与验证

600帧状态检查、随机寻帧一致性、完整解码、帧数、时长、无音轨和关键帧检查通过。交互预览在本地Chrome与Codex内置浏览器中检查过播放、拖动和暂停。
尚未进行人工连续审片或观众理解测试。工具能力在画面中合并为一个教学模块，省略依赖注入、完整Agent回合和多作用域细节。卸载示例不承诺所有配置都支持热替换。

模型适配、工具注册与循环均以插件形式提供能力；ctx是有作用域的能力入口。原始技术依据见project.json的sources。
