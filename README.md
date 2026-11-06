# 搬家不掉链 · Move Light Skill

把家庭物品清单、搬家日期、纸箱限制与搬运报价，变成可执行的日期清单、编号箱单、车辆容量检查和精确到分的费用对比。纯 Python 标准库，不上传住址，不预订、不付款。

```bash
python3 skill/move-light/scripts/plan.py examples/family.json --today 2026-11-04 --out output
python3 -m unittest discover -s tests -v
```

生成 `output/move-plan.md` 和 `output/move-plan.json`。支持首日必需品/易碎品分箱，体积与重量双重约束，大件单独处理，逾期任务，以及不完整报价排除。算法为可解释的 first-fit decreasing 启发式，不保证装箱最优；车辆空间按箱体容量估算，应由实际搬运人员核对。

新增可选箱体与物品尺寸：70×5×5 cm 的低体积画筒不会再被安排进 40×30×30 cm 的箱子；缺失尺寸明确保留为“未核对”。这是单件直角旋转检查，不证明完整三维布局。运行 `examples/dimensions.json` 可查看长条物品、易碎必需品和未知边长同时出现的示例。

[相近实现与改进记录](docs/landscape.md) 比较 OR-Tools 和 py3dbp 的现有能力、许可证与固定版本，说明本项目的差距和独立实现范围；不宣称装箱概念独有。

可复用 Skill 位于 `skill/move-light/`，入口为 `SKILL.md`，内含输入规范和实际可运行脚本。将此文件夹导入兼容的 Skill 环境即可使用；仓库并未更改你的个人全局 Skill 配置。

可直接导入的 ZIP 为 `submission/move-light.zip`（根目录含 `SKILL.md`）。运行 `python3 scripts/package.py` 可重建；ZIP 只含 Skill 本身，不含用户清单或输出文件。

## 华为 × 小红书参赛路径

对应 [小红书 Skill 创新赛](https://developer.huaweicloud.com/competition/information/1300000350/introduction)。2026-11-06 实读官方[创作与提交说明](https://developer.huaweicloud.com/competition/information/1300000350/html3)：须实际使用 CodeArts 或 OfficeAce 至少一种，并将 Skill **同时发布到华为云和小红书两个 Skill 市场**；还需至少一条针对已发布 Skill 的小红书笔记，带指定赛事话题。当前交付是可运行项目及通用 Skill 包，**尚未在 CodeArts/OfficeAce 实际创作验证，也未上传市场、报名或发小红书笔记**；不要将 GitHub 推送当作已完成参赛。官方当前报名及作品截止为 11 月 24 日，具体时刻最终请在报名后台核对。

可在 CodeArts 导入此项目，进行实际改进和演示，记录使用过程，再按官方流程上传。分享案例时使用本仓库虚构数据，避免发布住址和贵重物品清单。

MIT License. Six-project development was coordinated across a Codex agent team; all calculations can be reproduced locally.
