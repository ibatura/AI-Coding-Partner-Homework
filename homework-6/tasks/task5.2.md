# Task 5.2 — Documentation: README & HOWTORUN (Output of Agent 4 Sub-Agent)

## Overview
Generate project documentation including README.md and HOWTORUN.md. The README **must include the student's name** — this is a hard requirement for Agent 4.

**Note**: These documentation files are the **output** of the Documentation sub-agent (`agents/documentation_agent.md`). The sub-agent MD file contains the instructions for Claude to generate these docs.

---

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/documentation_agent.md` must already exist (from Task 5, Step 1). That MD file tells Claude what documentation to generate.

## Step 2: Create `README.md` (output of the sub-agent)

**Output file**: `README.md` in the project root.

### Required sections:

#### 1. Title and Author
```markdown
# AI-Powered Multi-Agent Banking Pipeline

**Created by: [Student's Name]**
```
- The student's name MUST appear prominently (author line, "Created by", or similar)
- This is a graded requirement

#### 2. Project Description (1–2 paragraphs)
- What the system does: multi-agent banking transaction pipeline
- How agents cooperate: file-based JSON message passing through `shared/` directories
- What each stage does: validation → fraud detection → settlement
- What the 4 meta-agents are: Claude sub-agents (MD files) that generate the entire system

#### 3. Agent Responsibilities (one bullet per agent)
List all 4 meta-agents (Claude sub-agents) AND 3 pipeline agents:

**Meta-agents** (Claude sub-agents that built the system):
- Agent 1 — Specification (`agents/specification_agent.md`): generates technical spec
- Agent 2 — Code Generation (`agents/code_generation_agent.md`): implements pipeline code
- Agent 3 — Unit Tests (`agents/unit_test_agent.md`): creates tests + skills/hooks
- Agent 4 — Documentation (`agents/documentation_agent.md`): generates docs

**Pipeline agents** (Python code that processes transactions):
- Transaction Validator: validates fields, amounts, currencies
- Fraud Detector: scores risk on 0–10 scale
- Settlement Processor: calculates fees, settles or holds

#### 4. ASCII Architecture Diagram
Must show the pipeline flow:
```
┌──────────────────────┐
│  sample-transactions │
│       .json          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Integrator       │  Loads & distributes
└──────────┬───────────┘
           │
     ┌─────▼──────┐
     │shared/input/│
     └─────┬──────┘
           │
    ┌──────▼───────────────┐
    │ Transaction Validator │  Validates fields, amounts, currency
    │  (validates/rejects)  │
    └──────┬───────┬───────┘
           │       │
      valid│  rejected──→ shared/results/
           │
    ┌──────▼──────────┐
    │  Fraud Detector  │  Scores risk (0-10)
    │  (scores risk)   │
    └──────┬──────────┘
           │
    ┌──────▼────────────────┐
    │ Settlement Processor   │  Fees, settlement, holds
    │  (settles/holds)       │
    └──────┬────────────────┘
           │
     ┌─────▼───────┐
     │shared/results│  Final outcomes
     └─────────────┘
```

#### 5. Tech Stack Table
| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Meta-Agents | Claude sub-agents (Markdown files) |
| Decimal Handling | `decimal.Decimal` |
| Testing | pytest + pytest-cov |
| MCP Server | FastMCP |
| MCP Lookup | context7 |
| Message Format | JSON (file-based) |
| Skills | Claude Code slash commands (.md) |
| Hooks | Coverage gate (pre-push) |

#### 6. Project Structure
Show the full directory tree including both MD sub-agent files and Python output files.

#### 7. Quick Start
Brief 3-line quick start:
```bash
pip install -r requirements.txt
python integrator.py
pytest --cov
```

---

## Step 3: Create `HOWTORUN.md` (output of the sub-agent)

**Output file**: `HOWTORUN.md` in the project root.

### Required: Numbered step-by-step instructions

```markdown
# How to Run

## Prerequisites
1. Python 3.10 or higher
2. pip package manager
3. Node.js (for context7 MCP)

## Setup
1. Clone the repository
2. Install Python dependencies:
   pip install -r requirements.txt
3. Verify installation:
   python --version
   pytest --version

## Running the Pipeline
4. Run the full pipeline:
   python integrator.py
5. Check results:
   ls shared/results/

## Running Tests
6. Run the test suite:
   pytest -v
7. Run with coverage report:
   pytest --cov=agents --cov=integrator --cov-report=term-missing

## Using Claude Code Skills
8. Run pipeline via skill:
   /run-pipeline
9. Validate transactions without processing:
   /validate-transactions

## Using the Sub-Agents
10. To regenerate the spec:
    Invoke agents/specification_agent.md in Claude Code
11. To regenerate pipeline code:
    Invoke agents/code_generation_agent.md in Claude Code
12. To regenerate tests:
    Invoke agents/unit_test_agent.md in Claude Code
13. To regenerate documentation:
    Invoke agents/documentation_agent.md in Claude Code

## MCP Server
14. Start the custom MCP server:
    python mcp/server.py
15. Test MCP tools in Claude Code:
    - get_transaction_status("TXN001")
    - list_pipeline_results()

## Troubleshooting
- If coverage is below 80%, the pre-push hook will block. Run tests to identify gaps.
- If shared/ directories are missing, run python integrator.py to create them.
```

---

## Step 4: Create `requirements.txt`

**Output file**: `requirements.txt` in the project root:
```
pytest>=7.0
pytest-cov>=4.0
fastmcp>=0.1
```

Add any additional dependencies discovered during implementation.

---

## Files Produced (by the Documentation sub-agent)
- `README.md`
- `HOWTORUN.md`
- `requirements.txt`

## Dependencies
- `agents/documentation_agent.md` (the sub-agent MD file that generates these docs)
- All tasks (1–4) completed — documentation references everything
- Student's name must be known

## Notes
- README must be factual — describe what actually exists, not aspirational features
- README must clearly distinguish between meta-agents (MD files) and pipeline agents (Python code)
- HOWTORUN must be tested — follow your own steps to verify they work
- Include the student's name prominently in README
