# refers/ — 参考实现清单与借鉴分析

本目录用于存放**参考实现**：在动手写一个新模块之前，先把值得研究的项目放进来，便于 coding 时对照。参考实现只用于指导我们自己的实现思路，**不直接照搬、不作为依赖引入**（见仓库根 `CLAUDE.md` 的「Workflow for adding a module」）。

本 README 有两个用途：

1. **清单（manifest）** —— 记录本目录放了什么、来自哪里、什么许可，使 `refers/` 的其余内容可以不入库而仍然可追溯。
2. **借鉴分析** —— 逐项列出参考实现中可提炼为 `pdb-md` 通用函数模块的操作。

> 约定：`refers/` 下除本文件外的内容建议 gitignore；本文件本身入库。

---

## 0. 清单

| 项目 | 来源 | 许可 | 快照信息 | 用途 |
|---|---|---|---|---|
| `BioStructureHub/` | https://github.com/ssciwr/BioStructureHub （ssciwr / Universität Heidelberg） | MIT（`tools/ccd2smiles`、`tools/RNAprep` 继承 MIT，二者无独立 LICENSE） | 拷贝于 2026-09-24，未保留 `.git`，upstream 版本 `0.1.0-dev` | 结构预测工具链的 notebook 教程集，含两个真实工具包 |

拷贝时未保留 git 历史，因此**无法给出 commit hash**。若后续需要精确复现，应重新 clone 并记录 commit。

---

## 1. 仓库总览（175 个文件）

| 部分 | 内容 | 对 pdb-md 的价值 |
|---|---|---|
| `tools/RNAprep/` | 完整的核酸体系预处理流水线（真包，非 notebook） | **最高** —— 与 README「5'-磷酸去除」章节完全重合 |
| `tools/ccd2smiles/` | CCD 码 → SMILES（走 RCSB REST） | **高** —— 配体参数化缺的那一环 |
| `notebooks/`（15 个） | 3 个 MD（制备 / 分析 / 可视化）+ 若干结构分析 | 中高 —— 一批可提炼的小工具 |
| `environments/molecular_dynamics.yml` | openmm 8.4 / openff-toolkit 0.18 / rdkit / mdanalysis / pdbfixer / openmmforcefields 的确切版本组合 | 高 —— 省掉版本踩坑 |
| `tests/` | 不是单元测试，是 nbval 跑 notebook + 4 个文件处理 helper | 中 —— 基建可借鉴 |
| `references/molecular_dynamics/{input,output}` | G3 RNA / 离子 / 小分子三类真实输入 + 输出 | 高 —— 现成测试夹具 |
| `docs/` | mkdocs 站点，含各预测工具的 bwVisu 教程 | 低 —— 部署相关 |

---

## 2. 与 README 现有章节的对应

仓库 README 已写了「5'-磷酸去除」与「质子化」，但目前都只是**外部工具名录**，没有实现。参考仓库正好补上实现：

| README 章节 | 参考仓库中的实现 | 位置 |
|---|---|---|
| Removal of terminal phosphate（核酸 5'-p） | `remove_op3()` 删首残基 OP3；`reorder_pdb()` 把末端原子拆成 OHE 残基移到链首；`write_pdb_with_connect()` 补 OP3–HOP3 / OP3–P 的 CONECT；`fix_phosphate_pdb()` 重建重叠的 OP3/OP1/OP2 几何 | `pipeline_steps.py:65,127,240,279` |
| protonation（加氢） | 三条不同路径：`run_pdbfixer()` 走 PDBFixer；`Modeller.addHydrogens(ff, pH=7)` 走 OpenMM；RDKit `AddHs(addCoords=True)` 走配体 | `pipeline_steps.py:101` + `Molecular_Dynamics.ipynb` |
| preprocessing（pdbfixer 那行） | `run_pdbfixer()` 是 findMissingResidues/Atoms + addMissingAtoms 的 6 行封装 | `pipeline_steps.py:101` |
| 配体参数化（README 未覆盖） | ccd2smiles → RDKit 按 SMILES 指认键级 → 加氢 → SDF → OpenFF Molecule | `ccd2smiles.py:63` + `Molecular_Dynamics.ipynb` |

`RNAprep` 的完整流水线（`RNAprep.py:13`）依次是：删 OP3 → tleap 加 OP3/质子化末端 → PDBFixer 规整 → 拆末端残基并移到链首 → PDBFixer 重新编号 → 补 CONECT → 修复磷酸几何，产物为 `{basename}_protein_fixed.pdb`，中间文件全部落盘。

---

## 3. 可提炼为通用函数模块的操作

**依赖**列决定了该操作进核心包还是可选 extras（见第 5 节）。

### A. 结构文件手术（纯 biopython，轻量）

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| 删除每个链首残基的指定原子（OP3） | `pipeline_steps.py:65` | Bio.PDB | 通用「按原子名做残基级手术」 | ★★★ |
| 把匹配原子拆到新建残基并插到链首 | `pipeline_steps.py:127` `reorder_pdb` | Bio.PDB | 通用「原子搬家 + 顺序重排」，PDB 顺序敏感的工具都需要 | ★★★ |
| 收集匹配原子的 serial number 并配对相邻残基 | `pipeline_steps.py:196` | Bio.PDB | 通用「CONECT 生成」前置 | ★★ |
| 按行插入 CONECT 记录（在 END 前） | `pipeline_steps.py:240` | stdlib | 通用 PDB 文本级后处理 | ★★ |
| `load_pdb` / `save_pdb` 两行封装（QUIET 解析） | `pdb_io.py:4,9` | Bio.PDB | 可统一 pdb-md 的 IO | ★★ |

### B. 配体 / 小分子（重依赖）

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| CCD 码 → canonical SMILES，带 LRU 缓存 + 失败清缓存 | `ccd2smiles.py:32,63` | requests | 配体参数化入口；字段是 `SMILES_stereo`（勿误取 `pdbx_chem_comp_descriptor`） | ★★★ |
| PDB→SDF：`AssignBondOrdersFromTemplate` + `SanitizeMol` + `AddHs(addCoords=True)` | `Molecular_Dynamics.ipynb` | rdkit | HETATM 只有坐标没有键级，这一步是刚需 | ★★★ |
| SDF → OpenFF `Molecule`，按 `len(mol.atoms)==1` 拆离子 vs 分子 | `Molecular_Dynamics.ipynb` | openff | 离子要单独作为 `ION` 残基加回 | ★★ |
| 从 cif 取非标准残基 + chain + SMILES（`_chem_comp.pdbx_smiles`，回退到 Boltz yaml / `ccd_to_smiles`） | `Molecular_Dynamics.ipynb` | biopython + yaml | 三条 SMILES 来源的优先级逻辑值得固化 | ★★ |

### C. 体系搭建（重依赖，OpenMM）

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| `SystemGenerator` 组合 amber14 protein + RNA.OL3 + tip3p + openff 小分子 | `Molecular_Dynamics.ipynb` | openmmforcefields | FF 组合的正确答案 | ★★ |
| `addSolvent` 溶盒 + 0.15 M NaCl + 中和 | `Molecular_Dynamics.ipynb` | openmm | 参数是该领域默认值 | ★★ |
| 把离子作为显式 `ION` 残基加回 modeller | `Molecular_Dynamics.ipynb` | openmm + openff | 非显然，容易踩坑 | ★★ |
| 能量最小化 + Langevin + reporters 的最短跑 | `Molecular_Dynamics.ipynb` | openmm | 「冒烟测试」跑 | ★ |

### D. 编号 / 序列映射（纯 biopython，**解决 README 的 SIFTS 警告**）

README 开头的警告「resseq 未必对得上 UniProt，请自行核对 SIFTS」正是这一组能自动化的。

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| 结构 → 序列：`MMCIFParser` + `PPBuilder.build_peptides` | `AFold3_mapping.ipynb` | Bio.PDB | 跳过 gap / 非标准残基的稳健取序列 | ★★★ |
| `alignment.coordinates` 遍历 → 输出配对残基索引（含 gap / 插入处理） | `AFold3_mapping.ipynb` | Bio.Align | **通用级**：模型编号 ↔ 作者编号 ↔ UniProt 编号的偏移检测 | ★★★ |
| 结构 → FASTA（`SeqRecord` + `SeqIO`） | `AFold3_mapping.ipynb` | Bio.SeqIO | 送下游比对 / 建 MSA | ★★ |

`alignment.coordinates` 那段的核心逻辑：配对遍历 `coords[0]`（template）与 `coords[1]`（query），只在 `dq>0 and dt>0` 时按 `n = min(dq, dt)` 推进索引，从而跳过纯 gap 段并正确处理插入。

### E. 轨迹分析（MDAnalysis，重依赖）

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| RMSD（backbone，对齐首帧） | `MD_Analysis.ipynb` | MDAnalysis | 标配 | ★★ |
| RMSF（Cα，可指定起始帧跳过平衡段） | `MD_Analysis.ipynb` | MDAnalysis | 标配 | ★★ |
| DSSP 二级结构 → 色条图 | `MD_Analysis.ipynb` | MDAnalysis | 绘图封装可直接抄 | ★ |
| Ramachandran（含 `((a+180)%360)-180` 缠绕） | `MD_Analysis.ipynb` | MDAnalysis | 同上 | ★ |
| 选定原子对距离时间序列 + mean±std 带 | `MD_Analysis.ipynb` | MDAnalysis | 封装干净 | ★★ |
| 能量收敛图 + `StateDataReporter` 表头清洗 | `Molecular_Dynamics.ipynb` 与 `MD_Analysis.ipynb` **重复出现** | pandas | `df.columns = [c.lstrip("#").strip('"') for c in df.columns]`，明显该合并成一个函数 | ★★ |
| nglview 轨迹可视化 | `MD_Visualization.ipynb` | MDAnalysis + nglview | 仅 Jupyter 内可用，返回 widget 而非图像，headless 场景无价值 | ☆ |

### F. 置信度指标解析（轻依赖）

| 操作 | 出处 | 依赖 | 价值 | 优先级 |
|---|---|---|---|---|
| AF3：从 mmCIF 的 `_ma_qa_metric_local.{ordinal_id,metric_value}` 取每残基 pIDDT | `AFold3_Confidence_Levels.ipynb` | MMCIF2Dict | 不必构建模型对象，最省 | ★★ |
| AF2：`result*.pkl` → `ptm/iptm/ranking_confidence/plddt/pae` 并排序选优 | `AFold2_Analysis.ipynb` | pickle + pandas | 标准契约 | ★★ |
| Boltz：JSON + npz；**pLDDT 是 0–1 需 ×100**；`iptm` 拆成 `ligand_iptm`/`protein_iptm` | `boltz_confidence_levels.ipynb` | json + numpy | 这两个坑值得写进统一 reader | ★★ |
| `chain_letters(n)`：`chr(ord("A")+i)` 得到 A..Z | AF3 与 Boltz 两个 notebook 重复 | stdlib | 极小的去重 | ★ |

### G. 工程基建

| 操作 | 出处 | 依赖 | 价值 |
|---|---|---|---|
| `normalize_text_paths()` 剥离绝对路径便于测试比对 | `tests/utils.py:13` | re | select 的输出比对很快会需要 |
| `prepare_results()` / `prepare_file()` 夹具复制 | `tests/utils.py:40,58` | shutil | 现成 fixture 管理 |
| nbval 把 notebook 当集成测试跑 | `pyproject.toml` + `.github/workflows/main.yml` | pytest + nbval | 思路可借：把参考仓库的 `references/molecular_dynamics/input` 当夹具 |

---

## 4. 参考仓库的空白（我们的差异化空间）

| 空白 | 说明 |
|---|---|
| **完全没有 CLI** | notebook 用 `__INPUT_FILE__` 占位符 + 字符串替换，没有 argparse / typer。CLI 是我们的差异化所在 |
| **没有 GROMACS / Amber 格式转换** | gro / top / prmtop / inpcrd 一律没有；只有 cif→pdb、pdb→sdf、sdf→openff。而本仓库 README 明显面向 Amber + GROMACS 用户 |
| **没有 radius of gyration** | MDAnalysis 那几项分析里恰好缺这一个 |
| **选择器很弱** | 只有 `ProteinOnly(Select)`，且作者自己注明「does not work for glycosylation」。本仓库的 `SingleChainSelector` + `MultiChainSelector` 更强（见第 5 节） |
| **不是单元测试** | 是跑 notebook 的集成测试，选择器这类纯函数逻辑没有覆盖 |

---

## 5. 注意事项

### 5.1 依赖分层

`pyproject.toml` 目前只有 `biopython` + `typer`，`pip install pdb-md` 很轻。而 openmm / mdanalysis / rdkit / openff / pdbfixer 均为重依赖（参考仓库的 `molecular_dynamics.yml` 实际装了 scipy + pandas + matplotlib + rdkit + openmm + mdanalysis + openff-toolkit + openmmforcefields）。

建议 A / D / F / G 组进核心，B / C / E 组走 extras：

```
pdb-md[ligand]     # rdkit, openff-toolkit, requests
pdb-md[md]         # openmm, openmmforcefields, pdbfixer
pdb-md[analysis]   # mdanalysis, pandas, matplotlib
```

新增重依赖是个设计决策，按 `CLAUDE.md` 的约定需要先与用户确认。

### 5.2 许可证

`BioStructureHub` 为 MIT，两个子包继承 MIT。可以借鉴，但按 `CLAUDE.md` 的约定**改写而非照抄**，即使 MIT 允许再分发。注意本仓库自身是 BSD-3-Clause。

### 5.3 参考实现中已知脆弱的点（照搬会出问题）

| 位置 | 问题 |
|---|---|
| `pipeline_steps.py:273` | `zip(p_idx, op_idx[1::2], op_idx[::2])` 依赖原子的严格交错顺序（每残基恰好 2 个目标原子），换体系即失效 |
| `pipeline_steps.py:13` `run_tleap` | 硬编码 `source leaprc.*` 与 `terminal_monophosphate.lib`，且 `subprocess.run(check=True)` 无超时、无路径解析 |
| `pipeline_steps.py:37` | basename 拼接出的中间文件名散落在 CWD；`__main__.py:16` 只保证 basename 不含路径分隔符 |
| `Molecular_Dynamics.ipynb` | `env_site_packages` 硬编码容器路径；openff 版本不一致（加氢用 `openff-2.2.0`，`SystemGenerator` 用 `openff-2.3.0`） |
| `Molecular_Dynamics.ipynb` | `residue.resname = residue.get_resname()[:3]` 直接改私有属性（`resname` 而非 `get_resname()` 的路径），且截断到 3 字符会丢信息 |
| `Molecular_Dynamics.ipynb` | 非标准残基的 `Select` 明确不支持糖基化（glycan 共价连接却会被当普通 HETATM 丢弃） |
| `ccd2smiles.py:45` | 请求失败时 `cache_clear()` 清掉**整个**缓存，一次网络抖动会丢掉所有已缓存结果 |
| `tests/utils.py:13` | `normalize_text_paths` 的路径正则复杂且未覆盖 URL，跨平台比对容易失效 |

---

## 6. 建议的模块划分

| 子命令 | 组成 | 依赖组 |
|---|---|---|
| `select` | 已有 | core |
| `renumber` / `map` | D 组（序列对齐偏移检测 + 可选 SIFTS 校验） | core |
| `termini` | A 组 + OP3 删除 + CONECT 重建 + 磷酸几何修复 | core |
| `fix` | PDBFixer 封装（缺残基 / 缺原子 / 加氢 @ pH） | `[md]` |
| `ligand` | ccd2smiles → RDKit 键级 → SDF → OpenFF | `[ligand]` |
| `solvate` | SystemGenerator + addSolvent + 离子回填 | `[md]` |
| `analyze` | E 组（RMSD / RMSF / Rg / DSSP / Rama / 距离 / 能量日志） | `[analysis]` |
| `confidence` | F 组统一 reader（AF2 / AF3 / Boltz 三后端） | core |

**起手建议**：从 `termini` 或 `renumber` 开始 —— 纯 biopython、不引重依赖、且正好补上 README 已经承诺但未实现的部分。

---

## 7. 核验程度

出处的可信度不同，使用时请据此判断：

| 内容 | 核验程度 |
|---|---|
| `tools/RNAprep/*`、`tools/ccd2smiles/*`、`tests/*.py`、`environments/molecular_dynamics.yml`、`docs/tutorials/tutorial_MD_bwVisu.md` | **已逐行读过**，文中行号可直接跳转 |
| `notebooks/*` 各行 | **未逐行亲自读过**，来自逐 cell 的源码分析（未抽样）；行号一律省略，只给 notebook 文件名。实现前建议回查对应 cell |

`references/molecular_dynamics/` 下有现成夹具（G3_RNA / G3_ion / G3_smol 三组 cif + yaml，以及一组 log 与 output.pdb），可直接用于验证未来实现的 `termini` / `ligand` 模块。
