# 搬家不掉链 — submission draft

Prepared 2026-11-06. 未报名、未上传市场；此文件可用于正式表单和演示策划，不能代替平台使用证明。

## 作品名称

搬家不掉链 · Move Light Skill

## 作品简介

把物品清单、搬家日期、纸箱限制和搬运报价，变成日期任务表、编号箱单、车辆容量检查和精确到分的报价对比。首日必需品与易碎品分别处理，大件单列；超期任务保留，缺项报价不把未知费用当作零元。可选边长会检查单件能否经直角旋转放入箱体，缺尺寸明确显示未核对。

## 实用价值与差异

装箱与搬家清单已有成熟方案。本作品聚焦普通家庭在临近搬家时容易漏掉的执行细节：明天就要用的物品、不能混装的易碎品、体积小但过长的物品，以及表面便宜但费用未报全的报价。算法为可解释启发式，不保证装箱最优或完整三维可行；实际车辆、搬运和费用需向服务方核实。

## 演示顺序

1. 导入虚构家庭示例，生成箱单和日期任务。
2. 用尺寸示例展示长条物品不能只按体积判断。
3. 将“今天”设为临近搬家日，展示逾期任务仍保留。
4. 对比完整报价和缺项报价，展示待确认费用。

使用 README 的可复现命令；通用包为 `submission/move-light.zip`，根目录含 `SKILL.md`。包内不含个人清单或生成结果。

## 正式提交前尚需完成

2026-11-06 实读[华为官方赛事页](https://developer.huaweicloud.com/competition/information/1300000350/introduction)：报名/作品截止 11/24（未具体时分），个人或 2–5 人团队，每人仅一队；需华为云登录报名并在“我的团队”建队。

按赛事[创作与提交要求](https://developer.huaweicloud.com/competition/information/1300000350/html3)，至少实际使用 CodeArts 或 OfficeAce 之一，保存真实创作/改进过程，**同时发布华为云和小红书两个 Skill 市场**，并至少发布一条小红书笔记，带 `#小红书Skill创新赛` 和 `#2026华为开发者大赛`。操作可参考[官方 CodeArts 上传说明](https://support.huaweicloud.com/offers-codeartsagent/codeartsagent_offers_0008.html)；比赛要求优先于通用说明中的单个市场示例。

当前项目由 Codex 多智能体协作完成，尚无 CodeArts/OfficeAce 贡献、两市场发布或笔记记录；不得写成“已使用”“已上架”或“已参赛”。账号授权与发布由本人统一处理。

公开案例仅用虚构数据。工具不联系搬家商、不预订、不付款。

Repository: https://github.com/misakamikotoghr-5205/move-light-skill

License: MIT.

本轮只补缺少的实际运行附件和发布执行稿：见[中文录屏/上传清单](submission/guide-zh.md)、[离线证据](submission/offline-demo-20261106.json)、[家庭箱单](submission/family-plan.md)与[尺寸例外报告](submission/dimensions-plan.md)。现有作品简介与 Skill 包不重复另做；CodeArts/OfficeAce、双市场、笔记和报名仍未完成。
