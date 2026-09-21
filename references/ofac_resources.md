# OFAC 美国经济制裁 · 核心检索资源地图

> 整理自公众号《「美国经济制裁」法律检索方法汇总》（Compliance Lens, 2026-03-06），按公司法务合规用途重分类。链接以 OFAC 官网为准，使用前应核实有效性。

## 0. 先分清边界

| 维度 | 经济制裁（OFAC，本文） | 出口管制（BIS，另线） |
|------|----------------------|----------------------|
| 主管机关 | OFAC（财政部） | BIS（商务部） |
| 管的是 | "跟谁交易"（冻结/禁止/名单） | "什么物项能出口"（EAR/实体清单） |
| 入口 | ofac.treasury.gov | bis.doc.gov |

一笔涉俄/涉伊交易常同时触发两条线，须分别评估。

## 1. 主管机关

- **OFAC**（财政部海外资产控制办公室）：资产冻结、交易禁止、名单管理、合规指引、民事处罚 — https://ofac.treasury.gov
- 国务院：制定制裁政策、外交层面落地
- 司法部 DOJ：违规刑事调查与追诉
- BIS（商务部）：出口管制、Entity List — https://bis.doc.gov

## 2. OFAC 官网六大区块（页面导航）

| 区块 | 用途 | 链接 |
|------|------|------|
| 制裁计划与国家信息 | 俄/伊/朝/古/委等全部专项计划总览，按国别做风险评估 | https://ofac.treasury.gov/sanctions-programs-and-country-information |
| 通知与指导 Notices & Guidance | 最新政策通知、合规指引、GL、执法公告（核心依据） | https://ofac.treasury.gov |
| 制裁清单服务 Sanctions Lists | SDN、SSI、FSE 等名单筛查 | https://ofac.treasury.gov/sanctions-list-service |
| 常见问题 FAQ | 按计划/主题分类的官方问答 | https://ofac.treasury.gov/faqs |
| 合规热线 Compliance Hotline | 咨询、举报、报告被冻结/拒绝交易 | https://ofac.treasury.gov/contact-ofac |
| 特定许可证申请 | 提交被禁交易的许可申请入口 | https://ofac.treasury.gov/apply-for-specific-license |

## 3. 法律法规与清单

| 资源 | 用途 | 链接 |
|------|------|------|
| 制裁法律图书馆 Legal Library | CFR、EO、联邦公报、UN 安理会决议 | https://ofac.treasury.gov/additional-ofac-resources/ofac-legal-library |
| SDN 清单 | 资产冻结、交易全面禁止（最硬名单） | https://sanctionslist.ofac.treas.gov/Home/index.html |
| Non-SDN 清单（NS-CMIC / SSI / NS-MBS 等） | 次级/行业制裁等较轻限制 | https://sanctionslist.ofac.treas.gov/Home/index.html |
| SDN 列表 XML 下载（监控用） | 机器可读，用于变更检测 | https://ofac.treasury.gov/downloads/sdn.xml |
| Consolidated 列表 XML 下载 | 综合制裁清单机器可读 | https://ofac.treasury.gov/downloads/consolidated.xml |

## 4. 执法、新闻与行业指南

| 资源 | 用途 | 链接 |
|------|------|------|
| 近期行动 Recent Actions | 最新列名/更新，监控必看 | https://ofac.treasury.gov/recent-actions |
| 新闻稿 Press Releases | 执法动向、政策解读 | https://ofac.treasury.gov/press-releases |
| 通用许可证 GL 合集 | 已批准的例外口子，决定交易能否直接做 | https://ofac.treasury.gov/selected-general-licenses-issued-ofac |
| 民事处罚与执法信息 | 罚款案例、和解金额、违规模式 | https://ofac.treasury.gov/civil-penalties-and-enforcement-information |
| 被冻结/拒绝交易报告系统 | 法定义务：报告 blocked / rejected 交易 | https://ofac.treasury.gov/ofac-reporting-system |
| 特定行业指南 | 农业/医疗人道/航空旅行/进出口商/金融/保险等 | https://ofac.treasury.gov/additional-ofac-resources/ofac-information-for-industry-groups |

## 5. 美国制裁法律渊源位阶（检索顺序）

1. 授权制定法：IEEPA、TWEA、NEA
2. 行政令 EO（开启专项计划的开关）
3. 联邦法规 CFR：31 CFR Chapter V（OFAC 条例，日常检索主战场）
4. 制裁清单：SDN / Non-SDN / CSL
5. 许可证：General License（GL）/ Specific License
6. 解释性文件：FAQ、合规指引、行业指南
7. 执法行动：民事罚款与执法信息

检索顺序建议：先看 EO/专项计划定"是否管得到" → 查 31 CFR 看"具体禁止什么" → 查清单看"对方在不在列" → 查 GL 看"有无例外" → 用 FAQ/指引校准理解 → 用执法行动验证风险敞口。

## 6. 合规实务判断点（步骤 3 必覆盖）

- **50% 规则**：实体被一个或多个 SDN 合计持股 ≥50%，即便未列名亦视同 SDN（须股权穿透）。
- **二级制裁**：部分制裁可罚非美国人，只要踩中美元清算/美源货品/US person 连接点。
- **严格责任**：OFAC 执法不论善意/不知情，违规即可能罚款——凸显名单筛查与留痕不可替代。
