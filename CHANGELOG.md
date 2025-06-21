# Changelog

All notable changes to TalkToAnki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-21

### 🎉 Initial Release

#### Added
- **Core MCP Server**: Full FastMCP implementation with 20 professional tools
- **Basic Operations** (8 tools):
  - `anki_get_deck_names`: Get all deck names
  - `anki_create_deck`: Create new decks
  - `anki_add_note`: Add new cards with custom fields and tags
  - `anki_find_notes`: Advanced card search with Anki query syntax
  - `anki_get_note_info`: Get detailed card information
  - `anki_get_deck_stats`: Comprehensive deck statistics
  - `anki_sync`: Sync Anki database
  - `anki_get_server_info`: Server status and configuration

#### Advanced Card Management (4 tools):
- `anki_update_note`: Update card content and tags
- `anki_delete_notes`: Batch delete cards
- `anki_move_notes`: Move cards between decks
- `anki_suspend_notes`: Suspend/unsuspend cards

#### Learning Analytics (3 tools):
- `anki_get_due_cards`: Get due cards with detailed breakdown
- `anki_get_study_progress`: Comprehensive study progress analysis
- `anki_get_review_history`: Review history with success rate analysis

#### Batch Operations (3 tools):
- `anki_batch_add_notes`: Bulk add multiple cards
- `anki_batch_update_tags`: Batch tag management
- `anki_export_deck`: Export decks to .apkg files

#### Template Management (2 tools):
- `anki_change_note_type`: Change card templates with field mapping
- `anki_get_note_types`: List all available note types

### 🏗️ Architecture Features
- **Modular Design**: Separate client, config, and server modules
- **Enterprise Performance**: Async operations, connection pooling, retry mechanisms
- **Robust Error Handling**: Comprehensive error management with detailed logging
- **Configuration Management**: Environment variable support and validation
- **Type Safety**: Full type hints and Pydantic validation
- **Testing Suite**: Complete test coverage with automated verification

### 📦 Package Features
- **Professional Packaging**: Modern pyproject.toml configuration
- **Development Tools**: Black, isort, mypy, pytest integration
- **Example Configurations**: Ready-to-use MCP client configs
- **Comprehensive Documentation**: Detailed README with usage examples
- **Open Source**: MIT license with contribution guidelines

### 🧮 MathJax Support
- **Perfect Formula Rendering**: Full LaTeX/MathJax support
- **Cloze Cards**: Complete support for fill-in-the-blank cards
- **Multi-level Cloze**: Advanced c1, c2, c3 cloze functionality
- **Template Flexibility**: Support for custom note types

### ⚡ Performance Optimizations
- **Connection Management**: Efficient HTTP client with connection reuse
- **Concurrent Operations**: Parallel request handling
- **Memory Efficiency**: Optimized data structures and processing
- **Rate Limiting**: Configurable request throttling

### 🔧 Developer Experience
- **Easy Installation**: Single command setup
- **Hot Reloading**: Development mode support
- **Rich Logging**: Detailed operation logging
- **Error Recovery**: Automatic retry with exponential backoff

### 📊 Compatibility
- **Python**: 3.8+ support
- **Anki**: All modern Anki versions
- **AnkiConnect**: Version 6 support
- **MCP Clients**: Cursor, Claude Desktop, and other MCP-compatible tools

---

## How to Read This Changelog

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

For detailed migration guides and breaking changes, see the documentation. 