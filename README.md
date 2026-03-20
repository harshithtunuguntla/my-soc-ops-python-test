# 🎉 Soc Ops: Social Bingo Game

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Play Game](https://img.shields.io/badge/Play%20Now-🎮-brightgreen)](https://madebygps.github.io/vscode-github-copilot-agent-lab/)

**Break the ice at your next in-person mixer!** Find people who match the bingo questions and get 5 in a row to win. Perfect for team building, networking events, and social gatherings.

🎯 **Quick Play**: [Click here to play the game](https://madebygps.github.io/vscode-github-copilot-agent-lab/)  
📖 **Lab Guide**: [Learn how it was built](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/)

---

## ✨ Features

- **Interactive Bingo Boards**: Dynamic bingo cards with fun, engaging questions
- **Tech Life Bingo Personas**: Role-based question sets for tech events (see below)
- **Real-time Scoring**: Track your progress and celebrate wins
- **Social Mixer Focus**: Designed for in-person events to help people connect
- **Responsive Design**: Works great on desktop and mobile devices
- **Easy Setup**: Get running in minutes with modern Python tools

## 🚀 Quick Start

### Prerequisites
- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) package manager

### Installation
```bash
# Clone the repo
git clone https://github.com/harshithtunuguntla/my-soc-ops-python-test.git
cd my-soc-ops-python-test

# Install dependencies
uv sync
```

### Run the Game
```bash
uv run uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser and start playing! 🎲

## 🖥️ Tech Life Bingo Personas

When you open the game you will see an optional **persona** dropdown on the
start screen.  Choosing a persona switches the board to **Tech Life Bingo** –
questions drawn from developer-focused categories instead of the generic
icebreaker pool.

### Available personas

| Persona key | Display name | Bias |
|---|---|---|
| *(empty)* | Classic Soc Ops | Generic icebreaker questions (default) |
| `default` | Default (all categories) | Equal mix of all three tech categories |
| `backend_engineer` | Backend Engineer | Heavy coding-habits, moderate dev-culture |
| `frontend_engineer` | Frontend Engineer | Heavy IDE/tooling, moderate coding-habits |
| `tooling_devops` | Tooling / DevOps | Heavy dev-culture, moderate IDE preferences |

### Question categories

- **coding_habits** – TDD, commit hygiene, pair programming, etc.
- **ide_preferences** – VS Code, Vim, extensions, themes, etc.
- **dev_culture** – open source, conferences, code review, podcasts, etc.

### Selecting a persona via the API

You can also send the persona directly as a query parameter:

```bash
# Start a backend-engineer-flavoured game
curl -X POST "http://localhost:8000/start?persona=backend_engineer" \
     -H "Cookie: session=<your-session-cookie>"
```

Invalid values are silently ignored and fall back to the `default` Tech Life
persona.

---



This project is part of a comprehensive workshop on building with GitHub Copilot. Follow the guided steps to learn modern development practices:

| Step | Topic | Description |
|------|-------|-------------|
| [**00**](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/step.html?step=00-overview) | Overview & Checklist | Get started with the workshop |
| [**01**](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/step.html?step=01-setup) | Setup & Context Engineering | Configure your environment |
| [**02**](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/step.html?step=02-design) | Design-First Frontend | Build the UI components |
| [**03**](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/step.html?step=03-quiz-master) | Custom Quiz Master | Add interactive features |
| [**04**](https://madebygps.github.io/vscode-github-copilot-agent-lab/docs/step.html?step=04-multi-agent) | Multi-Agent Development | Advanced collaboration techniques |

> 💡 Lab guides are also available in the [`workshop/`](workshop/) folder for offline reading.

---

## 🧪 Testing & Quality

```bash
# Run tests
uv run pytest

# Lint and format code
uv run ruff check .
uv run ruff format .
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

- 📧 [Support](SUPPORT.md)
- 🛡️ [Security](SECURITY.md)
- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)

---

**Ready to mingle?** [Play Soc Ops now!](https://madebygps.github.io/vscode-github-copilot-agent-lab/) 🎉
