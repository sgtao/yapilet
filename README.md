# yapilet

A YAML-driven Python toolkit for API requests and action chaining.
Available as a library, CLI, GUI, or API server.

---

## Installation

```bash
git clone <repo-url>
cd yapilet
mise install        # Set up Python 3.13 + uv
mise run install    # Install dependencies
```

---

For detailed usage, see **[USAGE.md](USAGE.md)**.

Japanese documentation: [README.ja.md](README.ja.md) / [USAGE.ja.md](USAGE.ja.md)

---

## Development Commands

```bash
mise run test       # Run tests
mise run test-cov   # Run tests with coverage
mise run lint       # Lint with ruff
mise run format     # Format with ruff
mise run check      # lint + mypy + test
mise run build      # Build wheels (dist/)
mise run cli:single # CLI smoke test (single request)
mise run cli:action # CLI smoke test (action chain)
```

---

## License

[Apache License 2.0](LICENSE)

---

🤖 Built with [Claude Code](https://claude.com/claude-code)
