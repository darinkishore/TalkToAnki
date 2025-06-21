# TalkToAnki

[![中文](https://img.shields.io/badge/lang-中文-red.svg)](README.md)
[![English](https://img.shields.io/badge/lang-English-blue.svg)](README_EN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**TalkToAnki** is a professional MCP (Model Context Protocol) server that enables seamless integration between AI assistants and Anki through AnkiConnect. It provides 20 comprehensive tools for complete Anki management.

## ✨ Features

### 🎯 Core Functions (8 tools)
- **Deck Management**: Create decks, get deck lists and statistics
- **Card Operations**: Add cards, search cards, get card information
- **System Functions**: Sync, get server information

### 🚀 Advanced Features (12 tools)
- **Card Management**: Update content, delete cards, move between decks, suspend/resume
- **Learning Analytics**: Due cards tracking, study progress, review history analysis
- **Batch Operations**: Bulk add cards, batch tag management, deck export
- **Template Management**: Change note types, list available templates
- **Single File Deploy**: All features integrated in one file for easy deployment
- **Zero Config**: No complex module management required

## 📊 Statistics

| Category | Tool Count | Description |
|----------|------------|-------------|
| 🏗️ **Basic Operations** | 8 | Deck/card CRUD, sync, system info |
| 📝 **Card Management** | 4 | Update, delete, move, suspend cards |
| 📈 **Learning Analytics** | 3 | Due cards, progress, review history |
| ⚡ **Batch Operations** | 3 | Bulk add, tag management, export |
| 🎨 **Template Management** | 2 | Note type operations |
| **Total** | **20** | **Complete Anki integration** |

## 📁 Project Structure

```
TalkToAnki/
├── talktoanki_server.py    # ⭐ Complete single-file server (all features included)
├── requirements.txt        # Project dependencies
├── pyproject.toml          # Modern Python package configuration
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT license
├── README.md              # Chinese documentation
├── README_EN.md           # English documentation
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md           # Version changelog
└── examples/
    └── cursor_mcp_config.json  # Cursor IDE configuration example
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Anki Desktop** with **AnkiConnect** plugin installed
- AI assistant that supports MCP (e.g., Cursor IDE)

### 2. Install AnkiConnect

1. Open Anki
2. Go to **Tools** → **Add-ons** → **Get Add-ons**
3. Enter code: `2055492159`
4. Restart Anki

### 3. Clone and Install

```bash
git clone https://github.com/your-username/TalkToAnki.git
cd TalkToAnki
pip install -r requirements.txt
```

### 4. Configure Cursor IDE

Create or update `~/.cursor/mcp_config.json`:

```json
{
  "mcpServers": {
    "TalkToAnki": {
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

> 💡 **Tip**: Replace `/path/to/your/TalkToAnki/` with your actual project path

### 5. Start Service

1. **Start Anki** (keep it running)
2. **Restart Cursor IDE**
3. The TalkToAnki MCP server will automatically connect

## 📚 Complete Tool Reference

### 🏗️ Basic Operations (8 tools)

#### 1. `anki_get_deck_names`
Get all deck names
```python
# Usage: Get all available decks
# Returns: JSON with deck list and count
```

#### 2. `anki_create_deck`
Create new deck
```python
# Parameters:
# - deck_name: Name of the new deck
# Returns: Creation confirmation
```

#### 3. `anki_add_note`
Add new card to deck
```python
# Parameters:
# - deck_name: Target deck name
# - front: Front content
# - back: Back content  
# - note_type: Note type (optional, default: "Basic")
# - tags: Tag list (optional)
# Returns: New card ID and details
```

#### 4. `anki_find_notes`
Search cards by query
```python
# Parameters:
# - query: Search query (Anki query syntax)
# Returns: List of matching card IDs
```

#### 5. `anki_get_note_info`
Get detailed card information
```python
# Parameters:
# - note_ids: List of card IDs
# Returns: Complete card information
```

#### 6. `anki_get_deck_stats`
Get deck statistics
```python
# Parameters:
# - deck_name: Target deck name
# Returns: Deck statistics (new, learning, due, etc.)
```

#### 7. `anki_sync`
Synchronize with AnkiWeb
```python
# Usage: Sync local changes with AnkiWeb
# Returns: Sync completion status
```

#### 8. `anki_get_server_info`
Get server information
```python
# Usage: Get AnkiConnect version and status
# Returns: Server details and configuration
```

### 📝 Card Management (4 tools)

#### 9. `anki_update_note`
Update card content and tags
```python
# Parameters:
# - note_id: Card ID to update
# - fields: Dictionary of field updates
# - tags: New tag list (optional)
# Returns: Update confirmation
```

#### 10. `anki_delete_notes`
Batch delete cards
```python
# Parameters:
# - note_ids: List of card IDs to delete
# Returns: Deletion results
```

#### 11. `anki_move_notes`
Move cards between decks
```python
# Parameters:
# - note_ids: List of card IDs to move
# - target_deck: Destination deck name
# Returns: Move operation results
```

#### 12. `anki_suspend_notes`
Suspend or resume card learning
```python
# Parameters:
# - note_ids: List of card IDs
# - suspend: True to suspend, False to resume (default: True)
# Returns: Suspension status changes
```

### 📈 Learning Analytics (3 tools)

#### 13. `anki_get_due_cards`
Get due cards information
```python
# Parameters:
# - deck_name: Target deck (optional, all decks if not specified)
# Returns: Due cards count and details
```

#### 14. `anki_get_study_progress`
Get detailed study progress
```python
# Parameters:
# - deck_name: Target deck (optional)
# - days: Number of days to analyze (default: 7)
# Returns: Study statistics and progress trends
```

#### 15. `anki_get_review_history`
Analyze review history and success rates
```python
# Parameters:
# - deck_name: Target deck (optional)
# - days: Number of days to analyze (default: 30)
# Returns: Review history and performance analysis
```

### ⚡ Batch Operations (3 tools)

#### 16. `anki_batch_add_notes`
Bulk add multiple cards
```python
# Parameters:
# - notes_data: List of card data
# - deck_name: Target deck name
# Returns: Batch add results with success/failure details
```

#### 17. `anki_batch_update_tags`
Batch tag management
```python
# Parameters:
# - note_ids: List of card IDs
# - add_tags: Tags to add (optional)
# - remove_tags: Tags to remove (optional)
# Returns: Tag update results
```

#### 18. `anki_export_deck`
Export deck to .apkg file
```python
# Parameters:
# - deck_name: Deck name to export
# - include_media: Whether to include media files (default: False)
# Returns: Export file path and details
```

### 🎨 Template Management (2 tools)

#### 19. `anki_change_note_type`
Change card template/note type
```python
# Parameters:
# - note_ids: List of card IDs to convert
# - target_model: Target note type name
# - field_mapping: Field mapping dictionary (optional)
# Returns: Template change results
```

#### 20. `anki_get_note_types`
List available note types
```python
# Usage: Get all available note types/templates
# Returns: List of note types with field information
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Ensure Anki is running with AnkiConnect
python test_talktoanki.py
```

Test coverage includes:
- ✅ Connection verification
- ✅ All 20 tools functionality
- ✅ Error handling
- ✅ Configuration validation
- ✅ Batch operations
- ✅ Analytics tools

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANKI_CONNECT_URL` | `http://localhost:8765` | AnkiConnect URL |
| `ANKI_CONNECT_VERSION` | `6` | AnkiConnect API version |
| `LOG_LEVEL` | `INFO` | Logging level |
| `REQUEST_TIMEOUT` | `30.0` | Request timeout (seconds) |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `DEFAULT_NOTE_TYPE` | `Basic` | Default note type for new cards |

### Advanced Configuration

Edit `config.py` for advanced settings:
- Connection timeout
- Retry policies  
- Concurrent request limits
- Default note types

## 🔧 Development

### Development Setup

```bash
git clone https://github.com/your-username/TalkToAnki.git
cd TalkToAnki

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python test_talktoanki.py

# Code formatting
black talktoanki_server.py talktoanki_client.py
isort talktoanki_server.py talktoanki_client.py
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AnkiConnect** - For providing the essential bridge between external applications and Anki
- **MCP Community** - For developing the Model Context Protocol standard
- **FastMCP** - For the excellent MCP server framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/TalkToAnki/issues)
- **Documentation**: [README.md](README.md) (Chinese) | [README_EN.md](README_EN.md) (English)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**🎯 TalkToAnki - Bridge the gap between AI and spaced repetition learning**

[![Stars](https://img.shields.io/github/stars/your-username/TalkToAnki?style=social)](https://github.com/your-username/TalkToAnki/stargazers)
[![Forks](https://img.shields.io/github/forks/your-username/TalkToAnki?style=social)](https://github.com/your-username/TalkToAnki/network/members)

</div> 