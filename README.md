# 搬家不掉链 · Move Light Skill

把家庭物品清单、搬家日期、纸箱限制与搬运报价，变成可执行的日期清单、编号箱单、车辆容量检查和精确到分的费用对比。纯 Python 标准库，不上传住址，不预订、不付款。

```bash
python3 skill/move-light/scripts/plan.py examples/family.json --today 2026-11-04 --out output
python3 -m unittest discover -s tests -v
```

生成 `output/move-plan.md` 和 `output/move-plan.json`。支持首日必需品/易碎品分箱，体积与重量双重约束，大件单独处理，逾期任务，以及不完整报价排除。算法为可解释的 first-fit decreasing 启发式，不保证装箱最优；车辆空间按箱体容量估算，应由实际搬运人员核对。

可复用 Skill 位于 `skill/move-light/`，入口为 `SKILL.md`，内含输入规范和实际可运行脚本。将此文件夹导入兼容的 Skill 环境即可使用；仓库并未更改你的个人全局 Skill 配置。

可直接导入的 ZIP 为 `submission/move-light.zip`（根目录含 `SKILL.md`）。运行 `python3 scripts/package.py` 可重建；ZIP 只含 Skill 本身，不含用户清单或输出文件。

## 华为 × 小红书参赛路径

对应 [小红书 Skill 创新赛](https://developer.huaweicloud.com/competition/information/1300000350/introduction)。官方 [CodeArts 上传说明](https://support.huaweicloud.com/offers-codeartsagent/codeartsagent_offers_0008.html) 要求在码道 IDE/网页端创作并通过 AI 会话上传到华为云或小红书 Skill 市场。当前交付是可运行项目及通用 Skill 包，**尚未在 CodeArts/OfficeAce 实际创作验证，也未上传市场、报名或发小红书笔记**；不要将 GitHub 推送当作已完成参赛。原始公告标明提交窗口 10月29日至11月24日，最终请在报名后台核对。

可在 CodeArts 导入此项目，进行实际改进和演示，记录使用过程，再按官方流程上传。分享案例时使用本仓库虚构数据，避免发布住址和贵重物品清单。

MIT License. Six-project development was coordinated across a Codex agent team; all calculations can be reproduced locally.
