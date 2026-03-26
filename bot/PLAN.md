# LMS Bot Development Plan

## Overview

This plan outlines the full development of an LMS Telegram bot across all four tasks. The bot allows users to interact with the LMS backend through Telegram commands and plain-language questions powered by an LLM.

## Architecture

The bot follows a **handler-first** architecture: all business logic lives in `handlers/` as plain Python functions that take input and return text. They are completely independent of Telegram. The `bot.py` entry point wires these handlers to both the Telegram dispatcher and the `--test` CLI mode.

This separation makes testing trivial: `--test "/command"` calls handlers directly without any network connection to Telegram.

## Task 1 — Scaffold

- Create `bot/` structure: `bot.py`, `handlers/`, `services/`, `config.py`
- Implement `--test` mode in `bot.py` for offline verification
- Add placeholder handler responses for all P0 commands
- Set up `pyproject.toml` with `aiogram`, `httpx`, `openai`

## Task 2 — Backend Integration

- Implement `services/lms_client.py` with `httpx` calls to all backend endpoints
- Fill in real logic for `/health`, `/labs`, `/scores`
- Add error handling: if backend is down, return a friendly message
- Test each command with `--test` mode against the live VM backend

## Task 3 — Intent-Based Natural Language Routing

- Implement `services/llm_client.py` using OpenAI-compatible API (Qwen)
- Define LLM tools wrapping all 9 backend endpoints
- Add intent router handler: plain text → LLM → tool call → response
- Support multi-step reasoning (LLM chains multiple API calls if needed)

## Task 4 — Containerize and Deploy

- Write `bot/Dockerfile` based on the same pattern as `backend/Dockerfile`
- Add `bot` service to `docker-compose.yml` with `env_file: .env.bot.secret`
- Deploy on VM and verify bot responds in Telegram
- Document deployment steps in README

## Testing Strategy

Every command is verified with `--test` before and after each task. Telegram is tested manually by sending commands to the bot after each deploy. The autochecker validates `--test "/start"` exits 0 with non-empty output.
