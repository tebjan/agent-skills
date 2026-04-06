# agent-skills

General-purpose utility skills for AI coding agents.

## What This Is

This repository contains **agent skills** — structured knowledge packages that AI coding agents load automatically. Each skill covers a specific utility task and follows the open [Agent Skills](https://skills.sh) standard.

Skills work with any compatible coding AI agent, including Claude Code, OpenAI Codex CLI, Cursor, Windsurf, GitHub Copilot, and [many others](https://skills.sh).

## Skills

| Skill | Description |
|-------|-------------|
| [fix-jsonl-surrogates](skills/fix-jsonl-surrogates/) | Diagnose and repair "invalid high surrogate" API errors in Claude Code JSONL chat files |

## Installation

### Via skills.sh (recommended)

```bash
npx skills add tebjan/agent-skills
```

### Install a specific skill

```bash
npx skills add tebjan/agent-skills --skill fix-jsonl-surrogates
```

### Manual Installation

Clone the repo and copy the `skills/` contents into your agent's skills directory:

```bash
# Claude Code (Windows)
git clone https://github.com/tebjan/agent-skills %TEMP%\agent-skills
xcopy /E /I %TEMP%\agent-skills\skills\* %USERPROFILE%\.claude\skills\

# Claude Code (macOS/Linux)
git clone https://github.com/tebjan/agent-skills /tmp/agent-skills
cp -r /tmp/agent-skills/skills/* ~/.claude/skills/
```

## License

CC-BY-SA-4.0 — see [LICENSE](LICENSE) for details.
