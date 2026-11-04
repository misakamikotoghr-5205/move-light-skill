# 相近实现与本轮改进

核查日期：2026-11-04。装箱算法、容量约束、三维旋转与搬家清单不是本项目独有的概念。Move Light 是把本地家庭清单、日期任务和报价不确定性接起来的轻量 Skill，不宣称首创或优于以下成熟工具，也没有做求解速度或最优性对比。

## 相近开源来源

| 来源与固定版本 | 已有能力 | 本项目的实际差距与取舍 |
| --- | --- | --- |
| [Google OR-Tools README](https://github.com/google/or-tools/blob/100f66e6242ab8bf8d32feb8f3bf086db66ae2b5/README.md)，`100f66e6242ab8bf8d32feb8f3bf086db66ae2b5`，stable 分支快照；[官方装箱说明](https://developers.google.com/optimization/pack/bin_packing) | 组合优化、装箱、背包和车辆路径等已有成熟求解工具。官方示例用“每件分到一个箱、容量不能超限、尽量少用箱”的整数规划。 | Move Light 没有优化器、最优性证明、路径规划或车辆调度。本项目保留确定性启发式和标准库，增加可解释的限制检查，而非把简单脚本称作优化求解器。 |
| [3dbinpacking / py3dbp README](https://github.com/enzoruiz/3dbinpacking/blob/31b9a40c78490da082bebde39a36e5327fb5191e/README.md)，`31b9a40c78490da082bebde39a36e5327fb5191e`，master 分支快照 | 使用箱体和物品的宽高深及重量，报告已装入和未装入物品，支持排序与多箱分配。这说明物理尺寸建模已有直接相近的 Python 实现。 | Move Light 没有复制其三维放置算法，也不输出多件物品的空间坐标。本轮仅补单件直角旋转可放入性，避免把“升数够”误当成“边长一定放得下”。 |

## 许可证与复用说明

- OR-Tools 为 [Apache-2.0](https://github.com/google/or-tools/blob/100f66e6242ab8bf8d32feb8f3bf086db66ae2b5/LICENSE)。若以后引入其源码或二进制，需遵守相关许可与第三方声明，不能仅保留本仓库的 MIT 文件。
- 3dbinpacking 为 [MIT](https://github.com/enzoruiz/3dbinpacking/blob/31b9a40c78490da082bebde39a36e5327fb5191e/LICENSE)。其 README 还列出了更早的算法来源，本项目不把这些算法据为原创。
- 本轮只阅读 README、许可证与官方问题建模说明，借鉴“区分容量与物理尺寸”的设计；没有复制、移植或捆绑这些仓库的实现、文档、图像或依赖。新增校验、报告与测试独立编写，仍只依赖 Python 标准库。固定版本与文件 SHA256 见 [landscape-sources.json](landscape-sources.json)。

## 已落实：尺寸约束与未知尺寸披露

原先只有升数和重量。例如 70×5×5 cm、约 2 L 的画筒能被排入 40×30×30 cm 的箱子，因为升数和公斤数都没超限，但沿箱边旋转无法放下。

现在支持可选 `box_dimensions_cm` 与逐件 `dimensions_cm`：

- 对已测量的箱和物品检查单件直角旋转。无法放入的物品留在 `loose_items`，附 `dimensions_exceed_box` 原因并阻止散件费用未核实的报价获得推荐。
- 箱内可用容量取名义升数与测得内体积的较小值；物品占用取声明升数与测得包围体积的较大值。原始升数保留，不把乐观估计覆盖成测量事实。
- 缺失尺寸逐件列为 `unchecked_unit_ids`，不会标为几何已验证。
- `geometry.layout_verified` 始终为 `false`：这不是完整三维布局，不验证对角倾斜、相互碰撞、直立限制、保护填充或搬运通道。

这修复了一个实际可用性缺口，但仍比三维装箱库能力有限。需要真实装载布局时，应评估相应求解工具并核对现场尺寸。

## 重现与验证

```bash
python3 skill/move-light/scripts/plan.py examples/dimensions.json \
  --today 2026-11-04 --out output/dimensions
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

本地 14 项测试通过；新增 5 项覆盖低体积长条物品、旋转可放入、实测容量与包围体积、未知尺寸、非法尺寸 CLI 不生成半份报告。既有物品唯一性、重量容量、逾期任务和不完整报价排除测试继续通过。已重新构建可导入 ZIP，并从临时目录解压运行新版脚本。

所有报价和清单仍来自输入；没有查询搬家商、联系他人、预订或付款。
