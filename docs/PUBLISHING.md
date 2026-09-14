# 发布到 GitHub / Publish to GitHub

目标首发仓库：`wz20/how-it-moves`，公开，MIT。

这份文件说明的是发布步骤，**不表示远程仓库已经创建，也不表示 Pages 已经上线**。在线状态须由 GitHub 返回的数据和实际打开页面验证。

## 一次运行：创建公开仓库、推送、配置原 HTML 演示

在本机安装 [GitHub CLI](https://cli.github.com/) 和 Git，登录你自己的账号。不要把 token 发给他人或提交到仓库。

```bash
# macOS + Homebrew；已经安装 gh 时跳过
brew install gh

# 首次登录；选择你自己的 GitHub 账号
gh auth login --hostname github.com --git-protocol https --web

# 进入解压后的 how-it-moves 目录
# 可以先只检查本地文件；这个命令不联网，也不会创建任何仓库
python3 scripts/publish_github.py --owner wz20 --repo how-it-moves --public --dry-run

# 正式执行：需要本机已登录账号具有创建公开仓库和配置 Pages 的权限
python3 scripts/publish_github.py --owner wz20 --repo how-it-moves --public
```

发布助手会确认登录账号，检查制品清单与敏感文件，拒绝覆盖已有仓库，使用 GitHub noreply 提交邮箱，提交清单中的文件，创建公开仓库并推送，然后对照本地/远程 commit SHA，最后把 Pages 源设为 **`main` 分支的 `/docs`**。不需要把模型、录音或第三方图片上传。

GitHub Pages 的构建可能排队。脚本只在读回源配置后报告“配置完成”，不会把队列状态当成站点已上线。首次部署完成后，进入 `https://wz20.github.io/how-it-moves/`，检查播放、暂停与拖动。

### 可审查的保护措施

- 必须显式传入 `--public`；不默认公开任意目录。
- 首发只针对与当前登录匹配的个人账号；组织发布请自行审核配置。
- 不覆盖已有仓库，不修改已有私有仓库的可见性，不强推，不删除仓库。
- 首发目录若已有 `.git`，脚本停止，避免提交其他历史或未审查内容。
- 只提交 `release-files.json` 清单中的文件，且逐项核验 SHA-256。
- 可能的密钥、私密配置、字体文件与软链接会被拦截。
- 不要求私密邮箱；不输出访问令牌；不修改全局 Git 用户名或邮箱。

### 异常处理

`gh` 未安装或未登录：先完成依赖和登录，再重试。账号不匹配：用 `gh auth switch --hostname github.com --user wz20` 切换，脚本不会自动切到另一个账号。

仓库已存在：先查看远端，不要换用强推。推送阶段失败但仓库已经创建时，保留当前目录，检查 `git status`、`git remote -v`，确认目标后使用普通 `git push -u origin main`。

代码推送成功、Pages 配置失败：检查仓库管理权限，在 Settings → Pages 选择 `Deploy from a branch`、`main`、`/docs`。也可在确认仓库已经公开后单独运行：

```bash
python3 scripts/publish_github.py --owner wz20 --repo how-it-moves --public --pages-only
```

内容经过修改：发布助手会拒绝旧哈希。先人工核对变更与公开范围，再运行 `python3 scripts/check_release.py --write-manifest`，随后重新检查并发布。该操作不会推送，也不替代素材授权审查。

## 手动配置 Pages

本项目不需要打包站点，也不需要另一个 Pages 分支：`docs/index.html` 已是自包含文件。按 GitHub 官方方法设置 `main:/docs` 即可。`docs/.nojekyll` 避免对静态文件作 Jekyll 模板处理。

README 中使用 **GIF 预览 + HTML 演示链接**。GIF 来自同一段示例成片，真正可拖动的演示是原始 HTML，不是替换后的录像播放器。

Fork 到其他账号时，更新 `README.md` / `README.en.md` 里的仓库与 Pages 链接；源场景与通用 Skill 不需要改作者账号。

## 官方说明

- [GitHub CLI：创建并推送仓库](https://cli.github.com/manual/gh_repo_create)
- [GitHub CLI：登录](https://cli.github.com/manual/gh_auth_login)
- [GitHub Pages：配置发布源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Pages REST API：所需权限与创建接口](https://docs.github.com/en/rest/pages/pages)
