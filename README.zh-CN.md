<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/AI_DuoForge-000000?style=for-the-badge&logo=github&logoColor=white">
    <img alt="AI DuoForge" src="https://img.shields.io/badge/AI_DuoForge-000000?style=for-the-badge&logo=github&logoColor=white">
  </picture>
</p>

<p align="center">
  <strong>两个AI一起干活，比一个强十倍。</strong><br>
  <strong>总监负责拆任务+审稿 · 工人负责执行 · 循环迭代直到质量达标</strong>
</p>

<p align="center">
  <strong>不需要会写代码。</strong> 任何行业、任何岗位、任何语言都能用。
</p>

<p align="center">
  <a href="#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B"><strong>快速上手</strong></a> ·
  <a href="#%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"><strong>工作原理</strong></a> ·
  <a href="#%E9%80%82%E7%94%A8%E8%A1%8C%E4%B8%9A"><strong>适用行业</strong></a> ·
  <a href="#agent-bridge-%E5%8D%8F%E8%AE%AE"><strong>通信协议</strong></a> ·
  <a href="#%E9%85%8D%E7%BD%AE%E6%96%B9%E6%B3%95"><strong>配置方法</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/suisui9527/ai-duoforge/ci.yml?style=flat-square&logo=github&label=CI" alt="CI">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/status-alpha-orange?style=flat-square" alt="Alpha">
</p>

---

<p align="center">
  <img src="assets/duoforge-demo.gif" alt="房地产 Demo" width="48%">
  &nbsp;&nbsp;
  <img src="assets/duoforge-hr-demo.gif" alt="HR Demo" width="48%">
  <br>
  <em>左：房地产 — 经纪人 ↔ 写手 迭代豪宅房源描述（73秒）</em>
  <br>
  <em>右：人力资源 — HR经理 ↔ 招聘专员 起草高级PM职位描述（84秒）</em>
</p>

---

## 为什么需要 DuoForge？

一个AI只有一颗大脑。它要同时做规划、执行、审查——全在同一个上下文窗口里。结果就是：

- **自审等于没审**（确认偏误）
- **Token上限撞得快**（大任务做不完）
- **一个模型的盲点没人补**

**DuoForge 把大脑拆成两个。**

一个当 **总监（Overseer）**——拆任务、定标准、审结果、打回重做。另一个当 **工人（Worker）**——写代码、出文案、跑分析、画图表。总监不写，工人不审。循环迭代，直到总监签字放行。你只管验收。

| 单打独斗 | DuoForge 双AI编队 |
|---|---|
| 一个脑子做所有事 → 上下文切到崩 | 总监专注规划，工人专注执行 |
| 自己审自己 = 白审 | 独立审查人抓出你的漏 |
| 一个模型的盲点一直存在 | 两个模型交叉覆盖 |
| 大任务 token 不够用 | 拆到两个上下文 = 2倍容量 |

**核心洞察：这不是技术问题，是角色分离问题。** 各行各业早就在用这个模式——合伙人审助理的案子、创意总监审文案的稿子、总建筑师审工程师的图纸。DuoForge 把这个循环自动化了。

---

## 快速上手

```bash
# 安装
pip install ai-duoforge
# 或者克隆仓库
git clone https://github.com/suisui9527/ai-duoforge.git
cd ai-duoforge
pip install -e .

# 初始化一个编队会话
duoforge init coding -d ./my-project

# 查看可用领域
duoforge list
```

### 运行你的第一个编队

**1. 打开总监 AI**（Hermes、Claude Code、ChatGPT 等，指向项目目录）：

```
我是 DuoForge 编队的 OVERSEER（总监）。
读取 .ai-pair/overseer_prompt.md 了解我的角色。
查看 .ai-pair/session.json 获取上下文。
向 .ai-pair/outbox/ 下发任务——我来审查和迭代。
```

**2. 打开工人 AI**（另一个AI，指向同一目录）：

```
我是 DuoForge 编队的 WORKER（工人）。
读取 .ai-pair/worker_prompt.md 了解我的角色。
轮询 .ai-pair/inbox/ 接收任务——我来执行并返回结果。
```

**3. 看它们自动迭代。** 总监发任务→工人执行→总监审查→打回修改→再审查→通过。你只管验收最终成果。

---

## 工作原理

```
                    ┌─────────────────────┐
                    │   DuoForge CLI       │
                    │  duoforge init/start │
                    └─────────┬───────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ┌───────────────┐             ┌───────────────┐
      │    总监       │◄────JSON────│    工人       │
      │  (Agent A)    │──消息交换──►│   (Agent B)   │
      └───────┬───────┘             └───────┬───────┘
              │                             │
              └───────────┬─────────────────┘
                          │
                  ┌───────┴───────┐
                  │ Agent Bridge  │
                  │ (文件/HTTP)   │
                  └───────────────┘
```

迭代闭环：

```
你           总监           工人
 │            │             │
 ├─ 提需求 ──►│             │
 │            │             │
 │            ├─ 任务 ─────►│
 │            │             ├── 执行
 │            │◄── 结果 ────┤
 │            │             │
 │            ├─ 审查       │
 │   [打回]   ├─ 修改意见 ─►│
 │            │             ├── 修改
 │            │◄── 新版 ────┤
 │            │             │
 │  [通过]    │             │
 ◄── 交付 ────┤             │
```

不需要服务器。不需要守护进程。只需要 JSON 文件在共享目录里。

---

## 适用行业

DuoForge 不是编程工具。它是一个**通用的工作自动化模式**，任何行业都能用。

<details>
<summary><strong>⚖️ 法律</strong> — 起草合同、审查诉状、研究判例</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 高级合伙人 | 实习律师 |
| 干什么 | 审法律逻辑、查引用、定策略 | 起草文件、整理案例、汇编证据 |
| 例子 | "起草一份基于缺乏诉讼资格的回驳动议，引用三个相关先例" | 产出草稿。合伙人审逻辑和完整性。循环直到法庭可用。 |

</details>

<details>
<summary><strong>🏥 医疗</strong> — 整理病历、研究疗法、写出院小结</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 主任医师 | 住院医 / 研究员 |
| 干什么 | 诊断、定方案、审病历 | 整理病史、收集团队意见、写报告 |
| 例子 | "总结这个病人的情况用于早交班，包含生命体征趋势和待查项目" | 产出小结。主任审后签字。 |

</details>

<details>
<summary><strong>💰 金融</strong> — 对账、出报告、分析利润表</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | CFO / 财务总监 | 分析师 / 会计 |
| 干什么 | 审报告、识别风险、定方法论 | 算数字、做表格、准备报表 |
| 例子 | "按部门做Q3环比分析，标出变化超过10%的项" | 产出分析。CFO审阅并加批注。 |

</details>

<details>
<summary><strong>📢 市场营销</strong> — 策划方案、写文案、分析投放数据</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 创意总监 / 市场总监 | 文案 / 设计师 |
| 干什么 | 定品牌调性、审内容、批方案 | 写文案、做素材、分析数据 |
| 例子 | "为新品上市写三版小红书种草文案，语气：年轻、真实、有烟火气" | 出三个版本。总监选一个，另外两个打回改。 |

</details>

<details>
<summary><strong>🎓 教育</strong> — 编写教案、设计课程、出卷子</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 课程设计师 | 助教 |
| 干什么 | 定教学目标、审内容 | 做课件、出习题、整理资料 |
| 例子 | "设计一个4周的气候变化模块，面向初三学生，每周配3个动手活动" | 产出模块。设计师审查年龄适配性和准确性。 |

</details>

<details>
<summary><strong>📰 媒体</strong> — 调查采访、写稿、事实核查</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 主编 | 记者 |
| 干什么 | 定选题、审稿、核实事实 | 采访、找资料、写初稿 |
| 例子 | "写一篇2000字特稿：AI对中小企业的影响，至少采访3个老板" | 出初稿。主编审准确性、调性、叙事节奏。 |

</details>

<details>
<summary><strong>🏗️ 建筑</strong> — 审图纸、汇材料清单、写提案</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 主创建筑师 | 绘图员 |
| 干什么 | 审设计、查规范、定规格 | 画图、列材料表、查法规 |
| 例子 | "为这个商业项目列一份材料规格表，附本地建筑规范参考" | 出规格表。主创审后签章。 |

</details>

<details>
<summary><strong>🛒 电商</strong> — 写商品描述、分析库存、做用户分层</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 产品经理 | 上架编辑 |
| 干什么 | 定产品定位、审商品页 | 写描述、优化SEO、分析数据 |
| 例子 | "为50款春季新品写商品描述，突出可持续材质" | 出50条描述。PM审一致性和品牌调性。 |

</details>

<details>
<summary><strong>🎮 游戏开发</strong> — 写设计文档、配表、做QA报告</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 游戏制作人 | 策划 / 开发 |
| 干什么 | 定玩法、审版本、设质量标准 | 写功能、配表、跑测试 |
| 例子 | "设计第三章的潜入机制，必须兼容现有的守卫AI" | 出方案+实现。制作人实测反馈。迭代到手感对为止。 |

</details>

<details>
<summary><strong>🏢 房地产</strong> — 写房源描述、做竞品分析、市场报告</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 资深经纪人 | 助理 |
| 干什么 | 定价格策略、审房源页、建议客户 | 写描述、做对比表、搜集市场数据 |
| 例子 | "为这套CBD豪宅写一段房源描述，突出景观和智能家居" | 出初稿。经纪人从买家视角审。打回再改。批准后上架。 |

</details>

<details>
<summary><strong>📊 人力资源</strong> — 写JD、出面试题、发Offer</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | HR经理 | 招聘专员 |
| 干什么 | 定岗位要求、审候选人 | 写JD、筛简历、草拟Offer |
| 例子 | "写一份高级后端工程师的JD，列5个必须条件和3个加分项" | 出JD。经理审准确性和合规性。 |

</details>

<details>
<summary><strong>🔬 科研</strong> — 文献综述、写基金申请、设计实验</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 课题组长（PI） | 研究助理 |
| 干什么 | 定研究方向、审方法、检查结果 | 查文献、跑分析、写章节 |
| 例子 | "检索近3年CRISPR在肿瘤学中的应用文献，写一份2页综述" | 出综述含引用。PI检查遗漏和解读偏差。 |

</details>

<details>
<summary><strong>💼 咨询</strong> — 写PPT、做市场分析、出建议书</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 合伙人 | 咨询顾问 / 分析师 |
| 干什么 | 定框架、审交付物、管理客户 | 做研究、搭PPT、跑模型 |
| 例子 | "为我们的金融科技客户做竞争格局分析，10个竞品，5个维度" | 出分析报告。合伙人审战略洞察。 |

</details>

<details>
<summary><strong>🌐 翻译</strong> — 文档翻译、术语管理、质量把控</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 本地化QA负责人 | 翻译 |
| 干什么 | 定义术语表、审译文、检查一致性 | 翻译、标疑、维护词条 |
| 例子 | "把这份20页的用户手册译成日语，遵守既有术语表，标记任何歧义术语" | 出翻译稿。QA审准确性、一致性、自然度。 |

</details>

<details>
<summary><strong>🧑‍💻 软件开发</strong> — 写功能、做Code Review、修Bug</summary>

| 角色 | 总监 | 工人 |
|------|------|------|
| 你相当于 | 架构师 | 开发工程师 |
| 干什么 | 设计架构、审代码、定规范 | 写功能、写测试、修Bug |
| 例子 | "实现一个速率限制中间件，支持Redis后端，每个路由可配" | 出代码+测试。架构师审性能和边界情况。 |

</details>

---

## Agent Bridge 协议

底层的通信协议叫 **Agent Bridge Protocol v1 (ABP)**——一个轻量级、与传输方式无关的消息格式。任何人都可以用。

```json
{
  "version": "abp/v1",
  "id": "msg_1780954000_a1b2",
  "from": "hermes",
  "to": "clawx",
  "type": "task",
  "payload": { "goal": "起草一份回驳动议" },
  "timestamp": "2026-06-09T10:00:00Z"
}
```

### 消息类型

| 类型 | 用途 | 例子 |
|---|---|---|
| `task` | 派任务 | "审查这10份合同" |
| `result` | 返回结果 | "完成，3份需要修改" |
| `ack` | 确认收到 | "收到，正在做" |
| `ping/pong` | 心跳检测 | 保活 |
| `context` | 共享上下文 | "客户偏好：言简意赅" |
| `train` | 给反馈 | "引用案例要更新" |
| `announce` | 注册上线 | "Hermes 上线" |

### 传输方式

- **文件** — 零依赖，JSON文件放共享目录，任何AI都能用
- **HTTP** — REST接口，跨网络通信
- **MCP** — 原生集成（Hermes Agent、Claude Code、Cursor）
- **STDIO** — 管道友好，适合命令行串联
- **Shell** — 100行bash客户端，见 `bridge/implementations/cli/abp.sh`

```bash
# 派一个任务
export ABP_AGENT_NAME="hermes"
bash bridge/implementations/cli/abp.sh send clawx task \
  '{"goal":"总结这个季度的业绩"}'

# 查回复
bash bridge/implementations/cli/abp.sh poll
```

---

## 配置方法

### 领域配置文件

每个行业是一个 YAML 文件，定义角色描述和质检标准：

```yaml
# configs/legal.yaml
domain: legal
description: "起草和审查法律文件"

quality_gates:
  - "所有引用真实可查"
  - "法律论证逻辑严谨"
  - "没有自相矛盾的观点"
  - "格式符合法庭要求"

pair:
  overseer:
    persona: >
      你是一位资深合伙人，审查法律工作。你核查每一个引用、
      挑战薄弱论点、确保逻辑闭环。你绝不亲自起草文件。
    review_criteria:
      - "引用的判例切题"
      - "论证基于事实"
      - "没有逻辑漏洞"

  worker:
    persona: >
      你是一位实习律师。你从合伙人那里收到清晰指令，
      起草有正确引用的文件。你不改变策略——你精准执行。
    output_format: |
      格式规范的法律文件，含引用。
```

### 添加自定义领域

```bash
# 复制一个现有配置，按需修改
cp configs/coding.yaml configs/my-industry.yaml

# 改完后的领域名、角色描述、质检标准
# 然后初始化：
duoforge init my-industry -d ./my-project
```

---

## 支持的 AI 编队

| 总监 | 工人 | 最适用 |
|------|------|--------|
| Hermes Agent | Claude Code | 追求精度的开发者 |
| Hermes Agent | Codex CLI | 快速原型 |
| Hermes Agent | ClawX | 量化 / 分析场景 |
| Claude Code | Codex CLI | 重型工程 |
| ChatGPT | Claude Code | 非技术用户，任意行业 |
| 任意AI | 任意AI | 你说了算 |

DuoForge 能配合 **任何能读写文件的AI**。你的AI能跑一条提示词，就能参与。

---

## 项目结构

```
ai-duoforge/
├── duoforge/                     # Python CLI
│   ├── __init__.py
│   └── cli.py                    # init, list, inspect 命令
├── configs/                      # 领域配置
│   ├── coding.yaml
│   ├── analysis.yaml
│   ├── real-estate.yaml         # 房地产（含演示）
│   └── ...
├── assets/                       # 演示资源
│   └── duoforge-demo.gif        # 循环演示GIF
├── bridge/                       # Agent Bridge 协议
│   ├── spec/SPEC.md              # 完整协议规范（英文）
│   └── implementations/
│       ├── file-bridge/          # Python 文件传输 CLI
│       ├── cli/abp.sh            # 零依赖 Shell 客户端
│       └── hermes-skill/         # Hermes Agent 集成
├── examples/                     # 教程
├── .github/workflows/ci.yml      # CI 流水线
├── pyproject.toml                # 包配置
└── README.md                     # 本文（英文版）
```

---

## 路线图

- [x] CLI：`init`、`list`、`inspect` 命令
- [x] 5个预置领域配置（含房地产）
- [x] Agent Bridge Protocol v1 规范
- [x] 文件传输（Python + Shell）
- [x] GitHub CI 流水线
- [x] 演示 GIF
- [ ] **PyPI 发布** — pip install 一键安装
- [ ] `duoforge start` — 一键启动双AI编队
- [ ] HTTP 传输服务 — 跨机器通信
- [ ] MCP 传输服务 — IDE 深度集成
- [ ] Web 仪表盘 — 实时查看编队会话
- [ ] 模板市场 — 社区共享领域配置

---

## 许可证

MIT — 个人和商用完全免费，无任何附加条件。

---

<p align="center">
  作者 <a href="https://github.com/suisui9527">suisui9527</a> ·
  <a href="https://github.com/suisui9527/ai-duoforge/issues">报告问题</a> ·
  <a href="https://github.com/suisui9527/ai-duoforge/discussions">加入讨论</a>
</p>
