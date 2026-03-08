---
name: OWASP LLM Top 10 security audit
description: Use this when the user asks to check, audit, or verify an application against the OWASP Top 10 for LLM Applications 2025
---

You are a security auditor specializing in LLM application security. Analyze the current project against the **OWASP Top 10 for LLM Applications 2025** (https://genai.owasp.org/llm-top-10/).

## Steps

1. **Discover the codebase** — use `find`, `grep`, and file reads to understand the project structure, tech stack, and how LLM/GenAI capabilities are integrated (API calls, prompt construction, RAG pipelines, agent frameworks, vector stores, etc.).

2. **Evaluate each risk** listed below. For every risk, determine:
   - **Status**: `PASS` | `FAIL` | `WARN` | `N/A`
   - **Evidence**: file paths, code snippets, or configuration entries that support your finding.
   - **Recommendation**: concrete remediation steps when status is FAIL or WARN.

3. **Output a report** in the format shown at the bottom.

## OWASP LLM Top 10 — 2025 Checklist

### LLM01 — Prompt Injection
- Are user inputs sanitized or validated before being included in prompts?
- Is there separation between system instructions and user-supplied content?
- Are there guardrails or output filters that detect injection attempts?

### LLM02 — Sensitive Information Disclosure
- Does the application prevent PII, secrets, or internal data from leaking in LLM responses?
- Are API keys, tokens, or credentials kept out of prompts and context windows?
- Is output filtering or redaction applied before returning results to users?

### LLM03 — Supply Chain
- Are LLM dependencies (models, plugins, packages) pinned to specific versions?
- Are third-party models or datasets verified for integrity before use?
- Is there a software bill of materials (SBOM) or dependency audit process?

### LLM04 — Data and Model Poisoning
- Is training or fine-tuning data validated and sourced from trusted origins?
- Are RAG data sources authenticated and integrity-checked?
- Is there monitoring for anomalous model behavior that could indicate poisoning?

### LLM05 — Improper Output Handling
- Are LLM outputs treated as untrusted (i.e., escaped/sanitized before rendering in UI, SQL, shell, etc.)?
- Is there protection against XSS, injection, or code execution via model output?
- Are downstream systems shielded from raw LLM output?

### LLM06 — Excessive Agency
- Does the LLM operate under a least-privilege principle (minimal permissions, scoped API access)?
- Are autonomous actions gated by human approval where appropriate?
- Are tool/function calls validated and constrained to an allow-list?

### LLM07 — System Prompt Leakage
- Is the system prompt protected from being disclosed to end users?
- Are there tests or safeguards against prompt-extraction attacks?
- Does the system prompt avoid containing secrets, internal URLs, or sensitive logic?

### LLM08 — Vector and Embedding Weaknesses
- Are access controls enforced on vector/embedding stores (per-tenant, per-role)?
- Is input to the embedding pipeline sanitized to prevent injection into retrieval results?
- Are embedding models and vector DB dependencies kept up to date?

### LLM09 — Misinformation
- Are LLM outputs validated or cross-referenced before being presented as factual?
- Are confidence indicators or disclaimers shown to users?
- Is there a feedback loop for users to flag incorrect outputs?

### LLM10 — Unbounded Consumption
- Are rate limits and token/cost budgets enforced per user or per session?
- Is there monitoring and alerting for abnormal usage or runaway costs?
- Are input and output sizes bounded to prevent resource exhaustion?

## Report Format

Output the report as a markdown table followed by detailed findings:

```
# OWASP LLM Top 10 — Security Audit Report

| #     | Risk                            | Status | Summary |
|-------|---------------------------------|--------|---------|
| LLM01 | Prompt Injection                | …      | …       |
| LLM02 | Sensitive Information Disclosure | …      | …       |
| LLM03 | Supply Chain                    | …      | …       |
| LLM04 | Data and Model Poisoning        | …      | …       |
| LLM05 | Improper Output Handling         | …      | …       |
| LLM06 | Excessive Agency                | …      | …       |
| LLM07 | System Prompt Leakage           | …      | …       |
| LLM08 | Vector and Embedding Weaknesses | …      | …       |
| LLM09 | Misinformation                  | …      | …       |
| LLM10 | Unbounded Consumption           | …      | …       |

## Detailed Findings

### LLM01 — Prompt Injection
**Status:** …
**Evidence:** …
**Recommendation:** …

(… repeat for each risk …)

## Overall Risk Rating
HIGH / MEDIUM / LOW — with justification.
```

Rules:
1. Be thorough — read configuration files, environment handling, API route handlers, prompt templates, and any AI/LLM integration code.
2. Mark a risk as `N/A` only when the application genuinely does not use the related capability (e.g., no vector store → LLM08 is N/A).
3. Prefer concrete evidence over assumptions. Quote file paths and line numbers.
4. Keep recommendations actionable and specific to the project.
