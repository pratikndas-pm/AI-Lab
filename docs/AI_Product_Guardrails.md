# AI Product Guardrails
- **Safety:** profanity/PII filters for outputs
- **Reliability:** rate-limit + retry; circuit breaker on upstream failures
- **Fallbacks:** canned answers when retrieval is empty; show source snippets
- **Observability:** log prompts, token counts, latency, errors (PII-safe)