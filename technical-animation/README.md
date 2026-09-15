# How It Moves · Mechanism-first v0.8

**按主题生成新美术，让对象演出因果，而不是让说明图片轻微缩放。**

安装时复制完整 `technical-animation/`，不要只复制 SKILL.md。保留已有客户项目并先备份旧安装。本包无 API key、模型、字体、浏览器二进制或客户素材；生图与视觉判断由宿主真实工具完成。

## 本轮真正增加的内容

- 生图之前验证类型化事件和依赖；从操作生成必须有的部件、状态、接触/遮挡需求。
- 将声明效果与实际动作编译结果核对；错误后果、错误分支、缺少原件和纯几何替代不能进入正式导出。
- 完整 / 隐藏解释性文字 / 只看机制三种审片视图；每个事件有前态、接触、提交、后态和连续播放。
- 从实际 SVG 图层和像素贡献检查结果是否真的入镜，分开工程、事件、视觉审阅；不自动批准。
- 保留 HTML、MP4、混合 SVG、本地声音与 SRT 时点。高校项目额外有来源/公式/目标台账和教师签核交付。

## 安装与依赖

安装目录可选 `~/.agents/skills/technical-animation/` 或宿主支持的项目 Skill 目录；Claude Code 用户目录可用 `~/.claude/skills/technical-animation/`。宿主必须能读取文件和执行命令，不能假设网页会话自动读取电脑目录。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
# MP4/音轨需要操作系统安装 ffmpeg/ffprobe；中文使用本机合法授权字体。
```

从本目录运行命令；安装到其他位置后使用绝对路径。Python 3.10 语法兼容会检查；本轮实际运行环境以 verification 记录为准，不等于每个系统都已实测。

## 一条真实制作流程

```bash
python scripts/create.py init --topic "具体教学机制" --formats html video svg --profile academic --out /path/to/new-project
# 按文档填写课程、事件、操作。没有图片也能先检查这一步：
python scripts/create.py plan /path/to/new-project
python scripts/create.py asset-plan /path/to/new-project --out /path/to/new-project/asset-plan-v1.json
# 再做主题视觉构思；prompts 只输出提示，不调用模型：
python scripts/create.py prompts /path/to/new-project --out /path/to/new-project/generation-v1.md
# 实际生图，看图，绑定已测量的部件与锚点后：
python scripts/create.py check /path/to/new-project
python scripts/create.py review /path/to/new-project --folder review-v1
# 真正审看每个事件及声音，填写 pending 记录，而非自动打勾：
python scripts/create.py export /path/to/new-project --review /path/to/new-project/review-v1/review.json --out /path/to/reviewed-media
```

这不是输入一句话即可覆盖所有学科的生成器。初始化刻意不塞固定机器人/道具，也不伪造生图票据或审阅意见。完整操作和字段见 [机制合同](references/mechanism-contract.md)、[表演合同](references/performance-contract.md)、[输出合同](references/output-formats.md)。

## 高校客户交付

```bash
python scripts/create.py handoff-init /path/to/new-project --delivery /path/to/reviewed-media --out /path/to/new-project/teacher-review-v1.json
# 真实教师/学科负责人审核、填写当前版本的批准与具体发现后：
python scripts/create.py handoff /path/to/new-project --delivery /path/to/reviewed-media --teacher-review /path/to/new-project/teacher-review-v1.json --out /path/to/client-delivery
```

客户交付命令不上传任何材料。详见 [课程与验收](references/academic-delivery.md)、[需求单](templates/COURSE_WORKORDER.md)。教师记录不是可认证数字签名；实际责任与确认流程不能由脚本替代。

## 复现验证

```bash
python -m unittest discover -s tests -v
python tests/check_mechanism_browser.py --out /path/to/new-verification
```

第二条包含实际浏览器消融/状态/遮挡检查和 MP4 全片解码，素材为**合成测试夹具**。它不等于真实生图质量、弱模型成功率、全学科覆盖或学习效果验证。不把这些测试图片当演示作品发客户。

## 边界

支持有限顺序离散操作与静态关系。连续物理/公式求解、通用参数教学交互、并行 DAG、自动素材分割、任意骨骼和复杂镜头适配未实现。无可用适配器时应明确范围并另行验证，不强套已有五种操作。详见 [能力矩阵](references/capabilities.md)。

早期视频是历史作品，保留以供观察美术与动作，但不代表它们已经通过 v0.8 门禁。新默认路径不复用固定素材世界。

MIT 适用于本包原创代码/文档；第三方依赖、客户内容和各生图服务的条款须分别核对。没有分发字体或声称获得其他创作者背书。
