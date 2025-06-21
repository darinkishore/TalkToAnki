# Contributing to TalkToAnki

Thank you for your interest in contributing to TalkToAnki! This guide will help you get started.

## 🚀 Quick Start

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/TalkToAnki.git
cd TalkToAnki
   ```

2. **Set up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install AnkiConnect**
   - Open Anki Desktop
   - Go to Tools > Add-ons > Get Add-ons
   - Enter code: `2055492159`
   - Restart Anki

## 🧪 Testing

Run tests before submitting:
```bash
# Run all tests
python test_anki_mcp.py

# Or using pytest (if available)
pytest
```

## 📝 Code Style

We use Black for code formatting:
```bash
# Format code
black .

# Check formatting
black --check .
```

## 🐛 Bug Reports

When reporting bugs, please include:
- Anki version
- AnkiConnect version
- Python version
- Error messages and stack traces
- Steps to reproduce

## ✨ Feature Requests

Feature requests are welcome! Please:
- Check existing issues first
- Describe the use case clearly
- Explain how it fits with the project goals

## 🔧 Development Guidelines

### Adding New Tools

1. Add the tool function in `anki_mcp_server.py`
2. Follow the existing pattern:
   ```python
   @app.tool()
   async def anki_your_tool(param: Type) -> str:
       """Tool description
       
       Args:
           param: Parameter description
           
       Returns:
           JSON formatted response
       """
       try:
           # Implementation
           return AnkiTools.format_response("your_tool", data)
       except Exception as e:
           return AnkiTools.handle_error("your_tool", e)
   ```
3. Add tests for the new tool
4. Update the README documentation

### Code Organization

- **anki_mcp_server.py**: Main MCP server and tool definitions
- **anki_client.py**: AnkiConnect client and connection management
- **config.py**: Configuration management
- **test_anki_mcp.py**: Test suite

### Error Handling

- Use `AnkiTools.handle_error()` for consistent error responses
- Validate input parameters
- Provide helpful error messages

## 📄 Documentation

- Update README.md for new features
- Include usage examples
- Document any new configuration options

## 🔄 Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following the guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   python test_anki_mcp.py
   black --check .
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use a clear title and description
   - Link related issues
   - Include testing information

## 📊 Project Structure

```
TalkToAnki/
├── talktoanki_server.py    # Main server
├── talktoanki_client.py    # AnkiConnect client
├── config.py               # Configuration
├── test_talktoanki.py      # Tests
├── requirements.txt        # Dependencies
├── pyproject.toml          # Package config
├── README.md               # Documentation
├── examples/               # Configuration examples
└── CONTRIBUTING.md         # This file
```

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's technical standards

## 📞 Getting Help

- Open an issue for questions
- Check existing issues and discussions
- Be patient and provide details

Thank you for contributing! 🎉 