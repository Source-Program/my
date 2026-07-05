# Agent Radar

Agent Radar is a small Telegram-first daily digest bot for tracking agent development, LLM apps, AI news, and AI engineering updates.

It is designed for a backend engineer gradually moving toward agent development. The first version is intentionally lightweight:

- no runtime dependencies beyond Python standard library
- RSS and arXiv fetchers
- rule-based ranking with an optional OpenAI summarization pass
- Telegram Bot API delivery
- local history to avoid duplicate pushes
- GitHub Actions schedule for daily runs

## Quick Start

```bash
python3 -m src.main --dry-run
```

Dry run prints the digest without sending it to Telegram.

To send to Telegram:

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python3 -m src.main
```

Optional environment variables:

```bash
export OPENAI_API_KEY="..."
```

`OPENAI_API_KEY` enables LLM-based final curation and Chinese summaries.

## GitHub Actions

Add these repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OPENAI_API_KEY` optional

The workflow in `.github/workflows/daily.yml` runs every day at 00:30 UTC, which is 08:30 in Asia/Shanghai.

## Configuration

Edit `config.json` to tune:

- sources
- keywords
- topic weights
- daily item limits
- language and target profile

## Telegram Bot Setup

1. Open Telegram and talk to `@BotFather`.
2. Create a bot and copy the bot token.
3. Send a message to your new bot.
4. Visit `https://api.telegram.org/bot<token>/getUpdates` to find your `chat.id`.
