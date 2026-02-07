# Contributing to Cloudflare WARP Toggle

Thank you for your interest in contributing!

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yappiverse/cloudflare-warp-toggle.git
   cd cloudflare-warp-toggle
   ```

2. **Install system dependencies**

   ```bash
   # Debian/Ubuntu
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1

   # Fedora
   sudo dnf install python3-gobject gtk3 libappindicator-gtk3

   # Arch
   sudo pacman -S python-gobject gtk3 libappindicator-gtk3
   ```

3. **Install Python dev dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the application**
   ```bash
   ./warp_toggle.py
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use meaningful variable names

### Linting & Type Checking

```bash
# Run linter
ruff check src/

# Auto-fix issues
ruff check src/ --fix

# Type checking
pyright src/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run linting and tests
4. Commit with clear messages: `git commit -m "feat: add system tray support"`
5. Push and create a PR

### Commit Message Format

Use conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Project Structure

```
cloudflare-warp-toggle/
├── warp_toggle.py          # Main entry point
├── src/
│   ├── constants.py        # App constants and modes
│   ├── styles.py           # CSS styling
│   ├── tray.py             # System tray integration
│   ├── tabs/               # UI tab components
│   ├── warp_cli/           # CLI wrapper module
│   ├── widgets/            # Custom GTK widgets
│   └── utils/              # Utilities and helpers
└── tests/                  # Unit tests
```

## Questions?

Open an issue on GitHub for any questions or suggestions.
