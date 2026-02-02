# 基金市场监控工具（实时估值接口已挂）

一个功能强大的金融市场实时监控工具，支持命令行和Web两种模式，可追踪基金估值、市场指数、黄金价格、行业板块和市场快讯。

## 功能特性

### 📊 数据监控
- **基金实时估值**：实时更新基金估值、日涨幅、近30天涨跌趋势
- **市场指数**：上证指数、深证指数、创业板指、纳斯达克、道琼斯等
- **黄金价格**：中国黄金基础金价、周大福金价及历史数据
- **行业板块**：各行业板块涨跌幅、主力资金流入情况
- **7×24快讯**：实时金融市场新闻和影响股票分析

### 💡 智能分析
- **连涨/连跌分析**：自动计算基金连续涨跌天数和幅度
- **30天趋势**：展示近30天涨跌分布，一目了然
- **持仓标记**：支持标记持有基金（⭐显示），快速关注重点
- **彩色显示**：终端下红涨绿跌，直观易读
- **🤖 AI深度分析**：集成LangChain提示链，生成1200+字专业分析报告（可选功能）

### 🚀 双模式运行
- **命令行模式**：快速查看，适合终端用户
- **Web界面模式**：可视化展示，支持表格排序，适合浏览器访问

## 安装

### 依赖安装

```bash
pip install -r requirements.txt
```

### 依赖包说明
- `loguru` - 日志输出
- `requests` - HTTP请求
- `tabulate` - 表格格式化
- `flask` - Web服务器（仅Web模式需要）
- `langchain` - AI提示链框架（AI分析功能）
- `langchain-openai` - OpenAI兼容API支持
- `langchain-core` - LangChain核心组件

## 使用方法

### 命令行模式

#### 查看所有信息
```bash
python fund.py
```
或使用编译好的可执行文件：
```bash
./dist/fund.exe  # Windows
```

显示内容包括：
- 7×24快讯
- 行业板块排行
- 实时金价
- 黄金历史价格
- 近7日A股成交量
- 近30分钟上证指数
- 市场指数汇总
- 自选基金估值

#### 管理自选基金

**添加基金**
```bash
python fund.py -a
# 根据提示输入基金代码，多个代码用英文逗号分隔
# 例如：001618,161725,110011
```

**删除基金**
```bash
python fund.py -d
# 根据提示输入要删除的基金代码
```

**标记持有基金**
```bash
python fund.py -c
# 标记后的基金会在名称前显示 ⭐
```

**取消持有标记**
```bash
python fund.py -b
# 移除基金的持有标记
```

**标记基金板块**（独立功能）
```bash
python fund.py -e
# 为基金添加板块标签，独立于持有标记
# 标记后会在基金名称中显示板块信息
```

**删除板块标记**
```bash
python fund.py -u
# 删除基金的板块标签
```

### Web服务器模式

#### 启动服务
```bash
python fund_server.py
```

服务默认运行在：`http://0.0.0.0:8311`

#### 访问地址
浏览器访问：`http://localhost:8311/fund`

#### Web API

**添加基金（通过URL）**
```
http://localhost:8311/fund?add=001618,161725
```

**删除基金（通过URL）**
```
http://localhost:8311/fund?delete=001618
```

#### Web功能特性
- 📊 所有数据表格化展示
- 🔄 支持点击表头排序（升序/降序）
- 🎨 现代化UI设计（白底蓝色主题）
- 📱 响应式布局
- ⚡ 多线程并发获取数据，加载快速

## 🤖 AI智能分析（可选）

程序集成了最新版本的**LangChain (0.3.27+)**，使用**提示链（Prompt Chain）模式**生成深度AI分析报告。

### 🎯 三种分析模式

程序支持三种不同的AI分析模式，满足不同场景需求：

#### 📊 标准模式（默认）
```bash
python fund.py
```
- **输出长度**：1,200-1,600字（4个维度 × 300-400字）
- **生成时间**：2-3分钟
- **token消耗**：4,000-6,000
- **适用场景**：日常快速查看，平衡速度和质量

#### ⚡ 快速模式
```bash
python fund.py --fast
# 或
python fund.py -F
```
- **输出长度**：400-500字（简明报告）
- **生成时间**：30-60秒
- **token消耗**：~1,000
- **适用场景**：快速浏览市场概况，节省成本

#### 🔬 深度研究模式（新增）
```bash
python fund.py --deep
# 或
python fund.py -D
```
- **输出长度**：10,000-12,000字（专业行研报告）
- **生成时间**：5-10分钟
- **token消耗**：~20,000
- **成本**：约为标准模式的**6倍**
- **特色功能**：
  - 🤖 **ReAct Agent自主研究**：Agent自主决定数据收集策略
  - 🌍 **多源信息交叉验证**：使用DuckDuckGo搜索国际媒体报道
  - 📰 **网页深度抓取**：获取完整新闻文章内容
  - 🔍 **官方vs市场视角对比**：明确区分官方快讯与独立媒体观点
  - 📊 **详尽的量化分析**：每个事件500-1000字深度解读
  - 💼 **具体操作计划**：可执行的交易策略和触发条件
- **适用场景**：周末复盘、重要决策前的全面研究、专业投资分析

**模式对比表**：

| 特性 | 快速模式 | 标准模式 | 深度研究模式 |
|------|---------|---------|-------------|
| 字数 | 400-500 | 1,200-1,600 | 10,000-12,000 |
| 时间 | 30-60秒 | 2-3分钟 | 5-10分钟 |
| Token | ~1,000 | ~4,000-6,000 | ~20,000 |
| 成本 | ¥0.002 | ¥0.01-0.02 | ¥0.06-0.12 |
| 信息源 | 本地数据 | 本地数据 | 本地+网络搜索 |
| 分析深度 | 概要 | 标准 | 专业级 |

#### 无ai模式
```bash
python fund.py --no-ai
# 或
python fund.py -N
```

### 配置方式

#### 方式1：使用.env文件（推荐）

创建 `.env` 文件：
```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
```

或者使用DeepSeek：
```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

运行：
```bash
./run.sh  # 自动加载配置并启动
```

#### 方式2：临时配置

```bash
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"

python3 fund.py
```

#### 方式3：永久配置

在 `~/.bashrc` 或 `~/.zshrc` 添加：
```bash
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"
```

然后 `source ~/.bashrc` 生效。

### 支持的AI服务

OpenAI兼容格式，推荐标准模式用thinking模型，深度研究模式使用控制工具厉害的模型如claude-sonnet或kimi-k2

### 禁用AI分析

使用-N或者--no-ai参数即可禁用AI分析，不配置 `LLM_API_KEY` 也可以。

### 📄 Markdown报告输出

AI分析完成后会生成两种输出：

#### 1. 控制台输出（过滤markdown）
- 自动移除markdown语法标记（标题、加粗、列表、表格等）
- 智能分行（60字符宽度），保持良好可读性
- 使用logger.info输出，与程序日志格式统一

#### 2. Markdown文件（完整格式）
- 保存位置：`reports/AI市场深度研究报告_YYYYMMDD_HHMMSS.md`
- 文件结构：
  ```markdown
  # AI市场深度分析报告

  **生成时间**：YYYY-MM-DD HH:MM

  ## 📊 原始数据概览
  - 7×24快讯（最新10条，含情绪标签和受影响股票）
    * 发布时间精确到秒
    * 情绪标签：【利好】【利空】等
    * 受影响股票：最多显示3只（代码-名称）
  - 市场指数
  - 金价走势（历史+实时）
  - 市场成交量（近7天）
  - 上证指数分时（最近5分钟）
  - 涨幅领先板块（Top 5）
  - 跌幅板块（Bottom 5）
  - 基金持仓情况

  ## 1️⃣ 市场整体趋势分析
  （AI生成的完整markdown内容）

  ## 2️⃣ 行业板块机会分析
  （AI生成的完整markdown内容）

  ## 3️⃣ 基金组合投资建议
  （AI生成的完整markdown内容）

  ## 4️⃣ 风险提示与应对
  （AI生成的完整markdown内容）
  ```

- 支持markdown查看器美观展示
- 便于版本管理和历史回顾
- 可导出PDF或分享

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────┐
│           Presentation Layer             │
│  ┌──────────────┐      ┌──────────────┐ │
│  │  CLI Output  │      │  Web Server  │ │
│  │  (tabulate)  │      │   (Flask)    │ │
│  └──────────────┘      └──────────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            Business Layer                │
│          MaYiFund Class (fund.py)        │
│  ┌────────────────────────────────────┐ │
│  │ • Data Fetching (多线程)            │ │
│  │ • Trend Analysis (30天分析)        │ │
│  │ • Cache Management (基金缓存)      │ │
│  │ • Session Management (会话管理)    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│             Data Sources                 │
│  ┌────────┐ ┌────────┐ ┌─────────────┐ │
│  │fund123 │ │ Baidu  │ │  Eastmoney  │ │
│  │  .cn   │ │Finance │ │ jijinhao.com│ │
│  └────────┘ └────────┘ └─────────────┘ │
└─────────────────────────────────────────┘
```

### 核心类：MaYiFund

**主要方法：**

| 方法 | 功能 |
|------|------|
| `init()` | 初始化会话，获取CSRF令牌 |
| `add_code(codes)` | 添加基金到自选列表 |
| `delete_code(codes)` | 从自选列表删除基金 |
| `mark_fund_sector()` | 标记基金板块（独立功能） |
| `unmark_fund_sector()` | 删除基金板块标记 |
| `search_code()` | 查询所有自选基金数据（多线程） |
| `search_one_code()` | 查询单个基金（线程执行） |
| `bk()` | 获取行业板块数据 |
| `gold()` | 获取黄金历史价格 |
| `real_time_gold()` | 获取实时金价 |
| `get_market_info()` | 获取市场指数 |
| `A()` | 获取上证指数分时数据 |
| `seven_A()` | 获取近7日成交量 |
| `kx(is_return=False)` | 获取7×24快讯（支持返回数据给AI分析） |
| `init_langchain_llm()` | 初始化LangChain ChatOpenAI实例 |
| `ai_analysis()` | AI智能分析（使用LangChain提示链，整合全部数据源） |

**HTML输出方法（用于Web模式）：**
- `fund_html()` - 基金数据表格
- `marker_html()` - 市场指数表格
- `gold_html()` - 金价表格
- `bk_html()` - 板块数据表格
- 等等...

### 多线程设计

**并发控制：**
- 使用 `Semaphore(5)` 限制同时最多5个线程查询基金数据
- Web模式下，各数据模块（市场、黄金、基金、板块等）并行获取

**优势：**
- 大幅提升数据获取速度
- 避免API请求过于频繁被限制

### 数据缓存

**缓存文件：** `cache/fund_map.json`

**结构：**
```json
{
  "001618": {
    "fund_key": "JJ_001618",
    "fund_name": "天弘中证电子ETF联接C",
    "is_hold": true,
    "sectors": ["人工智能", "半导体"]
  },
  "161725": {
    "fund_key": "JJ_161725",
    "fund_name": "招商中证白酒指数分级",
    "is_hold": false,
    "sectors": []
  }
}
```

**编码：** 使用 GBK 编码（中文字符支持）

## 数据源

### fund123.cn
- 基金搜索和基本信息
- 基金30天估值曲线
- 实时估值数据

**主要端点：**
- `/api/fund/searchFund` - 搜索基金
- `/matiaria?fundCode=XXX` - 基金日涨幅
- `/api/fund/queryFundQuotationCurves` - 30天趋势
- `/api/fund/queryFundEstimateIntraday` - 实时估值

### 百度股市通 (gushitong.baidu.com)
- 市场指数（上证、深证、创业板、美股等）
- 7×24快讯（支持情绪标签识别和受影响股票提取，用于AI分析）
- 近7日成交量统计

**主要端点：**
- `/api/getbanner` - 市场指数横幅
- `/vapi/v1/getquotation` - 具体指数数据
- `/selfselect/expressnews` - 快讯新闻（含利好/利空标签和关联股票）
- `/sapi/v1/metrictrend` - 成交量趋势

### 其他数据源
- **api.jijinhao.com** - 中国黄金和周大福金价
- **push2.eastmoney.com** - 东方财富行业板块数据

## 项目结构

```
fund/
├── fund.py              # 核心业务逻辑（MaYiFund类）
├── fund_server.py       # Flask Web服务器
├── module_html.py       # HTML表格生成模块
├── requirements.txt     # Python依赖
├── README.md            # 项目文档（本文件）
├── CLAUDE.md            # 开发者文档
├── .env                 # 环境变量配置（需自行创建）
├── .env.example         # 环境变量配置示例
├── run.sh               # 启动脚本（自动加载.env）
├── test_ai.sh           # AI功能测试脚本
├── cache/              # 缓存目录
│   └── fund_map.json   # 自选基金缓存（GBK编码）
├── reports/            # AI分析报告目录（自动创建）
│   └── ai_analysis_*.md # AI生成的markdown报告
└── dist/               # 编译后的可执行文件
    └── fund.exe        # Windows可执行文件
```

## 数据展示说明

### 终端显示（CLI模式）

**颜色说明：**
- 🔴 红色：上涨/涨幅为正
- 🟢 绿色：下跌/跌幅为负

**基金数据列：**
1. **基金代码** - 6位数字代码
2. **基金名称** - 带⭐表示持有
3. **估值时间** - 最新估值的时间
4. **估值** - 当日实时估值涨跌幅
5. **日涨幅** - 前一交易日涨跌幅
6. **连涨天数** - 正数表示连涨，负数表示连跌
7. **连涨幅** - 连涨/连跌的累计幅度
8. **涨/总 (近30天)** - 近30天上涨天数/总天数
9. **总涨幅** - 近30天累计涨跌幅

### Web界面

**交互功能：**
- 点击表头可排序（再次点击切换升序/降序）
- 可排序的列会显示排序箭头指示器
- 表格使用现代化设计，白底蓝色边框

## 许可证

本项目仅供学习交流使用。数据来源于公开API，请遵守相关网站的使用条款。

## 免责声明

本工具仅提供数据展示功能，不构成任何投资建议。投资有风险，入市需谨慎。
