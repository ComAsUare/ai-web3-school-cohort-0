# Transaction Explainer - 项目结构

## 当前文件结构（已清理）

```
experiments/2_mini_tx_explain/
├── 📄 核心功能文件
│   ├── tx-explain.skill.md      # Skill 定义（触发器 + 执行流程）
│   ├── tx_query.py           # Phase 1: 查询脚本 ✅ 可用
│   └── requirements.txt         # Python 依赖
│
├── 📊 数据文件
│   ├── query_log.md             # 查询索引表
│   └── query_json/              # 原始 JSON 响应
│       ├── 20260521_155254_806649.json  # 成功查询
│       ├── 20260521_155523_154519.json  # 错误查询（404）
│       └── 20260521_155622_663989.json  # 空摘要
│
├── 📚 文档文件
│   ├── README.md                # 完整使用文档 + 流程图
│   ├── SUMMARY.md           # Phase 1 实现总结
│   ├── TEST_REPORT.md           # Phase 1 测试报告（6/6 通过）
│   ├── PHASE2_DESIGN.md         # Phase 2 架构设计
│   └── PHASE2_STATUS.md         # Phase 2 当前状态
│
└── 🔧 环境文件
    └── venv/                    # Python 虚拟环境
```

## 文件说明

### 核心功能文件

#### tx-explain.skill.md
- **作用**: Claude Code Skill 定义
- **内容**: 
  - 触发关键词（中英文）
  - 执行流程（Step 1-4）
  - 异常处理规则
  - 输入验证规则

#### tx_query.py
- **作用**: Phase 1 查询脚本
- **功能**:
  - 验证交易哈希格式
  - 查询 Blockscout API
  - 保存原始 JSON 到 `query_json/`
  - 更新 `query_log.md`
- **状态**: ✅ 已测试，完全可用

#### requirements.txt
- **内容**: `requests>=2.31.0`
- **安装**: `pip install -r requirements.txt`

### 数据文件

#### query_log.md
- **作用**: 查询索引表
- **格式**: Markdown 表格
- **字段**: 时间戳 | 交易哈希 | JSON 文件名 | 状态

#### query_json/
- **作用**: 存储所有原始 API 响应
- **命名**: `YYYYMMDD_HHMMSS_microseconds.json`
- **内容**: 完整的 Blockscout API 响应

### 文档文件
#### README.md
- **内容**:
  - 项目介绍
  - 完整的 ASCII 流程图
  - 安装和使用说明
  - 错误处理文档
  - API 信息

#### SUMMARY.md
- **内容**:
  - Phase 1 实现总结
  - 设计原则
  - 使用示例

#### TEST_REPORT.md
- **内容**:
  - 6 个测试用例详情
  - 测试结果（100% 通过）
  - 生成文件验证
  - 性能指标

#### PHASE2_DESIGN.md
- **内容**:
  - Phase 2 架构设计
  - 输出格式定义
  - 不确定性检测规则
  - 实现代码示例

#### PHASE2_STATUS.md
- **内容**:
  - Phase 2 当前状态
  - 待完成任务
  - 下一步行动

## 已删除的文件

- ❌ `tx_explainer.py` - 旧版本脚本，已被 `tx_query.py` 替代
- ❌ `tx_parser.py` - Phase 2 解析器，有缩进问题，待重新实现

## Phase 1 - 完全可用 ✅

**核心文件:**
- `tx-explain.skill.md`
- `tx_query.py`
- `query_log.md`
- `query_json/`

**使用方法:**
```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 查询交易
python tx_query.py 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060

# 3. 查看结果
cat query_log.md
ls query_json/
```

## Phase 2 - 待实现 ⏳

**需要创建:**
- `tx_parser.py` - 解析器脚本（需要重新实现）
- `parsed_reports/` - 解析报告目录

**设计文档:**
- ✅ `PHASE2_DESIGN.md` - 完整的架构设计
- ✅ `PHASE2_STATUS.md` - 实现状态

## 文件统计

| 类型 | 数量 | 大小 |
|----|------|------|
| 核心脚本 | 1 | 4.0K |
| Skill 定义 | 1 | 15K |
| 数据文件 | 4 | ~2K |
| 文档文件 | 5 | ~43K |
| **总计** | **11** | **~64K** |

## 下一步

1. **重新实现 tx_parser.py**
   - 在 IDE 中手动编写，避免缩进问题
   - 参考 `PHASE2_DESIGN.md` 中的代码

2. **测试 Phase 2**
   - 解析现有的 3 个 JSON 文件
   - 验证输出格式

3. **更新文档**
   - 在 README.md 添加 Phase 2 使用说明
   - 创建 Phase 2 测试报告

---

**项目状态**: Phase 1 完成并测试通过，Phase 2 设计完成待实现。
