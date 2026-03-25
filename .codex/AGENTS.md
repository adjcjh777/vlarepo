## 语言规则
- 内部思考和对用户的回复统一使用中文。

## Git 与分支规范
- 修改或实验前先确认工作目录正确，必要时使用 `cd` 和 `ls` 检查。
- 开始修改前执行 `git pull` 获取最新代码。
- 修改完成后执行 `git add`、`git commit -m "简洁描述"`，再执行 `git push origin branch_name`。
- 新功能分支使用 `feature/xxx` 命名。
- Bug 修复分支使用 `bugfix/xxx` 命名。
- 消融实验分支使用 `ablation/xxx` 命名。
- 消融实验开始前先推送分支，并在提交信息中说明实验内容和结果。
- 消融实验结束后使用 `git merge branch_name` 合并回主分支，并在提交信息中总结结论。

## 进度查看
- 查看训练进度时，根据对话中的服务器上下文检查日志和指标，例如使用 `tail -f /path/to/log/file.log`。
- 查看代码历史时使用 `git log`，查看具体改动时使用 `git diff`。
