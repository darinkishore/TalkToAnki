# TalkToAnki

[![中文](https://img.shields.io/badge/lang-中文-red.svg)](README.md)
[![English](https://img.shields.io/badge/lang-English-blue.svg)](README_EN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Compatible-green.svg)](https://github.com/jlowin/fastmcp)
[![AnkiConnect](https://img.shields.io/badge/AnkiConnect-6.0+-red.svg)](https://ankiweb.net/shared/info/2055492159)

一个优化的 MCP (Model Context Protocol) 工具，通过 AnkiConnect 与 Anki 无缝集成，为AI助手提供强大的 Anki 操作能力。

## ✨ 功能特性

- 🔍 **智能查询**: 查询卡片和卡组信息
- ➕ **内容管理**: 创建卡片和卡组
- 📊 **数据分析**: 获取复习统计和学习数据
- 🔄 **同步支持**: 完整的同步操作支持
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- ⚡ **性能优化**: 连接池、并发控制和资源管理
- 📦 **单文件部署**: 所有功能集成在一个文件中，部署简单
- 🚀 **零配置启动**: 无需复杂的模块管理和导入

## 🏗️ 项目结构

```
TalkToAnki/
├── talktoanki_server.py    # ⭐ 完整的单文件服务器（包含所有功能）
├── requirements.txt        # 项目依赖
├── pyproject.toml          # 现代Python包配置
├── README.md               # 项目文档
├── README_EN.md            # 英文文档
├── CONTRIBUTING.md         # 贡献指南
├── CHANGELOG.md            # 变更日志
├── LICENSE                 # MIT许可证
├── .gitignore              # Git忽略文件
└── examples/               # 配置示例
    └── cursor_mcp_config.json
```

## 🛠️ 系统要求

- **Python**: 3.8+
- **Anki**: 桌面版（需要安装 AnkiConnect 插件）
- **MCP客户端**: Cursor 或其他支持MCP的AI客户端

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/TalkToAnki.git
cd TalkToAnki
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装AnkiConnect插件
1. 打开Anki桌面版
2. 进入 工具 > 插件 > 获取插件
3. 输入插件代码: `2055492159`
4. 重启Anki

### 4. 配置MCP客户端

#### Cursor配置
将以下配置添加到Cursor的MCP配置文件 (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "anki": {
      "command": "python",
      "args": ["/path/to/your/TalkToAnki/talktoanki_server.py"],
      "env": {
        "ANKI_CONNECT_URL": "http://localhost:8765",
        "ANKI_CONNECT_VERSION": "6",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

> 💡 **提示**: 将 `/path/to/your/TalkToAnki/` 替换为实际的项目路径

### 5. 启动服务
1. 确保 Anki 桌面版正在运行
2. 重启 Cursor
3. 开始使用 Anki MCP 工具！

## 🛠️ 支持的工具

### 卡组管理
- `anki_get_deck_names`: 获取所有卡组列表
- `anki_create_deck`: 创建新卡组
- `anki_get_deck_stats`: 获取卡组统计信息

### 卡片操作
- `anki_add_note`: 添加新卡片
- `anki_find_notes`: 查询卡片
- `anki_get_note_info`: 获取卡片详细信息

### 系统操作
- `anki_sync`: 同步Anki数据库
- `anki_get_server_info`: 获取服务器状态和配置信息

### 🆕 高级卡片管理（新增）
- `anki_update_note`: 更新现有卡片内容和标签
- `anki_delete_notes`: 批量删除卡片
- `anki_move_notes`: 将卡片移动到指定卡组
- `anki_suspend_notes`: 暂停或恢复卡片学习

### 📊 学习进度分析（新增）
- `anki_get_due_cards`: 获取到期需要复习的卡片信息
- `anki_get_study_progress`: 获取详细的学习进度统计
- `anki_get_review_history`: 获取复习历史数据和成功率分析

### ⚡ 批量操作（新增）
- `anki_batch_add_notes`: 批量添加多张卡片
- `anki_batch_update_tags`: 批量更新卡片标签
- `anki_export_deck`: 导出指定卡组为.apkg文件

### 🔧 模板管理（新增）
- `anki_change_note_type`: 更改卡片的笔记类型（模板）
- `anki_get_note_types`: 获取所有可用的笔记类型列表

## 📊 使用示例

### 创建卡组并添加卡片
```json
{
  "action": "create_deck",
  "deck_name": "我的新卡组",
  "success": true,
  "message": "卡组 '我的新卡组' 创建成功"
}
```

### 查找卡片
```json
{
  "action": "find_notes",
  "query": "deck:我的新卡组",
  "note_ids": [1234567890],
  "count": 1,
  "success": true
}
```

### 🆕 批量添加卡片
```json
{
  "action": "batch_add_notes",
  "deck_name": "英语单词",
  "total_attempted": 3,
  "successful_count": 3,
  "failed_count": 0,
  "successful_note_ids": [1234567890, 1234567891, 1234567892],
  "success": true,
  "message": "批量添加完成：成功 3 张，失败 0 张"
}
```

### 🆕 学习进度统计
```json
{
  "action": "get_study_progress",
  "deck_name": "英语单词",
  "analysis_period_days": 7,
  "total_cards": 150,
  "new_cards": 20,
  "young_cards": 30,
  "mature_cards": 100,
  "recent_reviews": 45,
  "mature_percentage": 66.67,
  "new_percentage": 13.33,
  "success": true
}
```

### 🆕 复习历史分析
```json
{
  "action": "get_review_history",
  "deck_name": "英语单词",
  "period_days": 30,
  "total_reviews": 120,
  "again_count": 10,
  "hard_count": 15,
  "good_count": 70,
  "easy_count": 25,
  "success_rate_percentage": 79.17,
  "total_studied_cards": 100,
  "success": true
}
```

### 🆕 模板更改
```json
{
  "action": "change_note_type",
  "original_note_ids": [1234567890, 1234567891],
  "new_note_ids": [1234567900, 1234567901],
  "original_model": "Cloze",
  "target_model": "挖空模板",
  "total_processed": 2,
  "successful_count": 2,
  "failed_count": 0,
  "field_mapping_used": "auto",
  "success": true,
  "message": "成功将 2 张卡片从 'Cloze' 更改为 '挖空模板'"
}
```

### 🆕 笔记类型查询
```json
{
  "action": "get_note_types",
  "total_count": 5,
  "note_types": ["Basic", "Cloze", "挖空模板", "Basic (reversed)", "Image Occlusion"],
  "detailed_info": [
    {
      "name": "Basic",
      "fields": ["Front", "Back"]
    },
    {
      "name": "Cloze",
      "fields": ["Text", "Extra"]
    }
  ],
  "success": true,
  "message": "找到 5 个笔记类型"
}
```

## 🔧 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ANKI_CONNECT_URL` | `http://localhost:8765` | AnkiConnect服务地址 |
| `ANKI_CONNECT_VERSION` | `6` | AnkiConnect API版本 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `REQUEST_TIMEOUT` | `30.0` | 请求超时时间(秒) |
| `CONNECTION_TIMEOUT` | `10.0` | 连接超时时间(秒) |
| `MAX_RETRIES` | `3` | 最大重试次数 |

### 高级配置

更多配置选项请参考 `config.py` 文件。

## 🧪 测试

运行完整的测试套件：

```bash
python test_talktoanki.py
```

测试涵盖：
- 连接验证
- 所有工具功能
- 错误处理
- 批量操作
- 学习分析功能

## 🐛 故障排除

### 常见问题

1. **"0 tools enabled"**
   - 确保 Anki 桌面版正在运行
   - 检查 AnkiConnect 插件是否正确安装
   - 验证 MCP 配置文件路径正确

2. **连接被拒绝**
   - 确认 AnkiConnect 插件已启动
   - 检查防火墙设置
   - 验证端口 8765 未被占用

3. **工具无响应**
   - 检查 Anki 是否有弹窗等待用户操作
   - 重启 Anki 和 MCP 客户端
   - 查看日志文件排查具体错误

### 调试模式

设置环境变量启用调试：
```bash
export LOG_LEVEL=DEBUG
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细指南。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/anki-mcp-server.git
cd anki-mcp-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python test_talktoanki.py
```

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [AnkiConnect](https://github.com/FooSoft/anki-connect) - 提供 Anki 集成能力
- [FastMCP](https://github.com/jlowin/fastmcp) - 现代化的 MCP 服务器框架
- [Anki](https://apps.ankiweb.net/) - 优秀的间隔重复学习软件

## 📈 项目状态

- ✅ **稳定版本**: v1.0.0
- ✅ **生产就绪**: 经过全面测试
- ✅ **持续维护**: 活跃开发和支持
- ✅ **社区友好**: 欢迎贡献和反馈

---

**让AI助手帮助你更好地学习！** 🚀 