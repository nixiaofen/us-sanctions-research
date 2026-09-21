# us-sanctions-research · 美国经济制裁合规研究编排

把「美国经济制裁法律检索」整理成一套**可复用、半自动、human-in-the-loop** 的合规研究工作流，面向公司法务 / 合规实务。覆盖 OFAC 美国经济制裁线（名单筛查 → 法源覆盖核查 → 行为定性 → 许可证路径 → 留痕 → 持续监控）。

> ⚠️ **本仓库为研究辅助工具，不构成法律意见。** OFAC 名单与通用许可证（GL）持续更新，检索结果建议有效期不超过 7 天。最终合规决策须咨询具美国制裁执业资格的律师，并以 OFAC 官方实时数据为准。制裁与出口管制（BIS）可能同时适用，须分别评估。

---

## 一、定位与设计原则

- **半自动、human-in-the-loop**：机械检索与监控自动化，法律判断交回人工。
- **不重复造轮子**：名单筛查委派已安装的 [`sanctions-screening`](https://github.com/nixiaofen/us-sanctions-research)（覆盖 OFAC + 100+ 全球名单、含证据截图）；本 skill 负责「研究框架编排 + 客观事实汇集 + 持续监控 + 备忘录骨架」。
- **专治漏查**：步骤 1 强制做「适用制裁计划覆盖核查」，防止只筛名字、漏掉针对某地理/主题的专项制裁计划（如也门胡塞/Ansar Allah 在 EO 13224 反恐项下、也门/胡塞专项计划）。

### 硬性护栏（违反即高危误用）

1. **永不输出 go/no-go 结论**。只能输出：已查到 X、未发现 Y、建议人工评估 Z。
2. **数据权威且实时，打时间戳**。优先 OFAC 官方源，结论标注检索时间(UTC)。
3. **强制免责声明**（见文末）。
4. **假阴性优先于假阳性**。OFAC 严格责任下，宁可标「存疑、需人工复核」，不给「自动绿灯」。
5. **区分 OFAC 制裁 vs BIS 出口管制**。本 skill 只覆盖 OFAC 线；涉出口管制须另行查 BIS / Entity List。

---

## 二、七步工作流

| 步骤 | 名称 | 自动化 | 关键产出 |
|------|------|--------|----------|
| 1 | 法源依据与制裁计划覆盖核查 | 半自动 | **适用计划覆盖清单（防漏查核心）** |
| 2 | 名单筛查 | 自动（委派 sanctions-screening） | 命中 / 清除 / 存疑，附证据 |
| 3 | 国别 / 专项计划定位 | 自动（WebFetch） | 计划限制摘要，与步骤 1 交叉比对 |
| 4 | 行为定性（50% 规则 / 二级制裁 / 连接点） | **人工** | 待决法律判断清单（**不下结论**） |
| 5 | 许可证路径 | 半自动 | GL 适用性比对表（决策权在人工） |
| 6 | 留痕与报告 | 半自动 | 七步研究备忘录骨架（判断区留空+签核提示） |
| 7 | 持续监控 | 自动 | 名单变更 / 关注实体状态 / 定期告警 |

**步骤 1 重点**：据地理/行业/行为枚举所有可能适用的 OFAC 计划（综合 + 专项 + 反恐/网络/毒品等横向），抓取「授权法 → EO → 31 CFR 章节 → 主要被制裁群体」法源链，产出覆盖清单供合规官逐项审计是否漏查。配套可勾选审计卡见 `references/coverage_audit_card.html`。

---

## 三、仓库结构

```
us-sanctions-research/
├── SKILL.md                       # 七步工作流主文件（WorkBuddy 加载入口）
├── README.md                      # 本文件
├── references/
│   ├── ofac_resources.md          # OFAC 官网资源地图（主管机关/法规库/清单/GL/执法/报告系统）
│   ├── legal_authority_lookup.md  # 法源依据索引 + 覆盖核查方法（伊朗/也门/俄/朝/叙/古/委 深度细化）
│   ├── coverage_audit_card.html   # 可勾选覆盖核查审计卡（防漏查，可打印存档）
│   └── research_memo_template.md  # 七步研究备忘录模板
└── scripts/
    ├── monitor_ofac.py            # OFAC 名单变更 + 关注实体级告警（仅 Python 标准库）
    └── watchlist.json             # ⚠️ 示例占位，请本地自建真实关注清单（见第五节）
```

---

## 四、作为 WorkBuddy Skill 使用

1. 将本目录整体放入用户级 skill 目录：
   ```
   ~/.workbuddy/skills/us-sanctions-research/
   ```
2. 对话中描述意图（如「查一下 XX 实体是否触碰 OFAC 伊朗制裁」「建一个每日名单监控」）即触发。
3. 步骤 2 名单筛查依赖已安装的 `sanctions-screening`；若未安装，回退为官方源初查并标注「未经验证的初步筛查」。

---

## 五、监控脚本 `monitor_ofac.py`（可独立运行）

仅依赖 Python 标准库，无需第三方包。

```bash
# 默认监控 OFAC SDN 列表，首次运行自动建立基线
python scripts/monitor_ofac.py

# 监控综合清单（Consolidated）
python scripts/monitor_ofac.py --list consolidated

# 启用关注实体级告警（默认自动加载同目录 watchlist.json）
python scripts/monitor_ofac.py --watch scripts/watchlist.json

# 指定基线文件与输出报告
python scripts/monitor_ofac.py --baseline base.json --out report.md

# 覆盖默认下载端点（OFAC 调整地址时用）
python scripts/monitor_ofac.py --url https://ofac.treasury.gov/downloads/sdn.xml
```

**行为**
- 首次运行：写入基线（SHA256 + 条目名），报告「基线已建立」。
- 后续运行：比对基线，报告新增 / 移除条目与 hash 是否变动。
- 加载 watchlist 后：额外报告每个关注实体的当前状态与变化（🔴 新被列入 / 🟢 已解除制裁 / 在名单中）。

**`watchlist.json` 说明（重要）**
- 仓库内 `watchlist.json` 为**示例占位**，不含任何真实关注实体。
- 请你**在本地自建**真实清单：复制该文件，删除示例条目，填入要监控的实体关键词（大小写不敏感子串匹配）与备注。
- 改完后**不要** `git add` 它（已被 `.gitignore` 排除运行产物，但占位版已入库；改本地版即可让每日监控聚焦你的实体）。
- 若 `watchlist.json` 不存在，脚本回退到内置默认关注实体（Zanjani / Dot One / 胡塞 / BITBANK）。

**每日自动监控（可选）**：用 `automation_update` 建 recurring 自动化（如每日 09:00），prompt 调用 `monitor_ofac.py --watch scripts/watchlist.json`，发现关注实体新列入/解除即经邮件等渠道告警。

---

## 六、法源与漏查防护参考

- `references/legal_authority_lookup.md`：法源检索链（授权法 → EO → CFR → 计划 → 被制裁群体）、主要计划法源索引、也门实例、**伊朗 / 也门 / 俄罗斯 / 朝鲜 / 叙利亚 / 古巴 / 委内瑞拉深度细化**。
  - 关键编号（起始索引，正式出具意见前请以 OFAC Legal Library / eCFR 实时复核）：伊朗 ITSR = 31 CFR 560（EO 13902 落于其下）；也门 = 31 CFR 543，胡塞 SDGT = 31 CFR 594（EO 13224）；俄罗斯 = 31 CFR 587（EO 14024）+ 589（乌克兰/俄相关）；朝鲜 = 31 CFR 510；叙利亚 = 31 CFR 542；古巴 = 31 CFR 515；委内瑞拉 = 31 CFR 591。
- `references/coverage_audit_card.html`：可勾选审计卡，逐项确认是否漏查某制裁计划/关系，可打印 PDF 存档。

---

## 七、局限与注意事项

- **网络依赖**：监控脚本需可访问 `ofac.treasury.gov` 下载列表；离线/受限环境无法运行。
- **端点可能调整**：OFAC 下载地址若变更，用 `--url` 覆盖，并同步更新 `references/ofac_resources.md`。
- **非实时保证**：本工具不做法律结论，仅汇集客观事实；正式决策前须以 OFAC 官方实时数据复核。
- **仅覆盖 OFAC**：出口管制（BIS / EAR）、欧盟/英国/联合国制裁须另行评估。

---

## 免责声明

> 本工具与工作流仅供参考，**不构成法律意见**。OFAC 名单与通用许可证持续更新，检索结果建议有效期不超过 7 天。美国经济制裁与出口管制可能同时适用，须分别评估。最终合规决策应咨询具执业资格的美国制裁律师或合规专家，并以实时官方数据为准。使用本仓库产生的任何后果由使用者自行承担。
