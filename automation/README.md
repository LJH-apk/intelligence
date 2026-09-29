# AI Brief automation

This workflow sends a compact AI news brief every day at 07:00 Asia/Shanghai (23:00 UTC).

## What it does

- Prioritizes OpenAI, Anthropic, Google DeepMind, xAI, and Meta.
- Specifically looks for OpenAI model/API/product changes, including reset, quota, deprecation, default-model, and shutdown signals.
- Falls back to Qwen, DeepSeek, GLM, Kimi, and Mistral when closed-model vendors are quiet.
- Filters for trusted/official domains and recent results.
- Sends the previously agreed restrained HTML layout through Resend.

## Required secret

Add one GitHub Actions repository secret:

- `RESEND_API_KEY`

Path: **Settings → Secrets and variables → Actions → New repository secret**

The workflow can also be tested manually via **Actions → AI Brief Daily → Run workflow**.

> Note: GitHub scheduled workflows can occasionally start a few minutes late. The cron is set to 23:00 UTC, which corresponds to 07:00 Beijing time.
