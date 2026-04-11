# agent-skills

General-purpose utility skills for AI coding agents.

## What This Is

This repository contains **agent skills** — structured knowledge packages that AI coding agents load automatically. Each skill covers a specific utility task and follows the open [Agent Skills](https://skills.sh) standard.

Skills work with any compatible coding AI agent, including Claude Code, OpenAI Codex CLI, Cursor, Windsurf, GitHub Copilot, and [many others](https://skills.sh).

## Skills

### Workflow orchestrators

| Skill | Description |
|-------|-------------|
| [addy-orchestrator](skills/addy-orchestrator/) | Orchestrates end-to-end software development using the addyosmani/agent-skills framework. Guides through define → plan → build → verify → review → ship phases with persistent state. |
| [claude-mem-orchestrator](skills/claude-mem-orchestrator/) | Orchestrates `claude-mem` persistent memory for maximum session context. Loads relevant past work at conversation start and helps save important decisions across sessions. |
| [gepetto-orchestrator](skills/gepetto-orchestrator/) | Advises on Gepetto planning sessions. Helps assess whether the full 17-step pipeline is worth the investment, drafts spec files, and routes execution to manual / ralph-loop / Ralphy CLI. |
| [gsd-orchestrator](skills/gsd-orchestrator/) | Orchestrates and routes complete GSD (Get Shit Done) development workflows — picks the right command, asks clarifying questions, spawns subagents for each phase. |
| [ralph-orchestrator](skills/ralph-orchestrator/) | Advises on Ralph Loop automated development sessions. Writes effective loop prompts, sets safe iteration limits, monitors progress, detects stuck loops. |
| [swarm-advisor](skills/swarm-advisor/) | Advises on multi-agent swarm design using Claude Code's TeammateTool and Task system. The "think before you spawn" layer over swarm-orchestration. |

### Token efficiency

| Skill | Description |
|-------|-------------|
| [caveman-smart](skills/caveman-smart/) | Intelligent token-efficiency mode. Compresses routine chat and thinking but stays in full prose for reasoning, architecture, and safety-critical topics. Picks the level per response. Built for HPC, real-time, graphics, and other engineering work. |

### Tools and utilities

| Skill | Description |
|-------|-------------|
| [install-github-plugin](skills/install-github-plugin/) | Installs Claude Code plugins from GitHub repos that lack a marketplace manifest. Handles cloning, manifest generation, and the install workflow. |
| [fix-jsonl-surrogates](skills/fix-jsonl-surrogates/) | Diagnose and repair "invalid high surrogate" API errors in Claude Code JSONL chat files. |

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
