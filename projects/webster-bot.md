---
title: Webster Bot
tagline: Telegram bot for Webster University Canvas assignment reminders.
icon: 🎓
status: Active
version: v1.0.0
url: https://github.com/gagaci/webster-telegram-bot
github: https://github.com/gagaci/webster-telegram-bot
---

# About

Webster Bot is a focused Telegram bot for Webster University Canvas assignments. It checks Canvas, formats upcoming work, and sends it through Telegram on a daily schedule or on demand.

# Features

- **Canvas assignments** — Pulls upcoming assignments into Telegram
- **Daily reminders** — Runs on an 8am-style cron schedule by default
- **On-demand command** — Send `/brief` to fetch assignments manually
- **Small surface area** — Built around one useful workflow: knowing what is due

# Tech Stack

- TypeScript
- node-telegram-bot-api
- node-cron
- OpenAI
- Axios

# Repository

[View on GitHub](https://github.com/gagaci/webster-telegram-bot)
