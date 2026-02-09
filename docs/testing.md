# Testing

This page explains how tests are organized, why integration tests are skipped by default, and how to run them. It also describes how the in-repo sequential thinking tool is covered by integration tests.

## Why integration tests show as SKIPPED

The integration tests in [tests/integration/test_mcp_client.py](../tests/integration/test_mcp_client.py) are **intentionally skipped** when you run the normal test command without a special environment variable.

- **Skip condition** (lines 14–18): A module-level `pytestmark` skips the entire module unless:
  - `USE_REAL_FASTMCP` is set to one of `"1"`, `"true"`, or `"yes"` (case-insensitive).
- So when you run e.g. `uv run pytest` or `uv run pytest tests/` **without** setting that variable, every test in this file is skipped with the reason: *"Integration tests require USE_REAL_FASTMCP=1"*.

### How to run integration tests locally

**Bash / WSL:**

```bash
USE_REAL_FASTMCP=1 uv run pytest tests/integration -v
```

**Windows PowerShell:**

```powershell
$env:USE_REAL_FASTMCP="1"; uv run pytest tests/integration -v
```

**CI:** In [.github/workflows/test.yml](../.github/workflows/test.yml) (lines 36–38), integration tests run in a separate step with `USE_REAL_FASTMCP=1` and `continue-on-error: true`, so the main test run stays fast and non-flaky even if the integration step fails.

## Relation to testing best practices

We follow common Python testing practices:

- **pytest** for all tests; **conftest.py** for shared fixtures (see [tests/conftest.py](../tests/conftest.py) and [tests/integration/conftest.py](../tests/integration/conftest.py)).
- **Fast tests by default**; use mocks for I/O or external services when appropriate.

This project does that by:

- Keeping the **default** test run fast and stable (unit tests only; no real MCP client/server).
- Making **integration tests opt-in** via `USE_REAL_FASTMCP=1`, so they only run when you or CI explicitly request them.
- Using a **conftest** in [tests/integration/conftest.py](../tests/integration/conftest.py) with a `require_integration_env` fixture that skips if the env is not set or if the FastMCP `Client` is not importable.

So the skip behavior is **by design** and consistent with “keep tests fast; use mocks where appropriate; heavier tests opt-in.”

## Sequential thinking and integration tests

There is **no separate sequential-thinking MCP server** in this repo. “Sequential thinking” is implemented as an **in-repo MCP tool** inside the UML-MCP server:

- **Implementation:** [mcp_core/tools/sequential_thinking.py](../mcp_core/tools/sequential_thinking.py) — a tool named `sequentialthinking` that mirrors the Node sequential-thinking server API (plan → revise → verify; used for diagram planning before calling `generate_uml`).
- **Registration:** The tool is registered by importing the module in [mcp_core/tools/diagram_tools.py](../mcp_core/tools/diagram_tools.py) (line 15: `from . import sequential_thinking`), so the decorator registers it with the same server that exposes `generate_uml`, etc.

The **integration tests** that are skipped by default:

- **TestDiscoveryViaClient::test_list_tools_via_client** — Asserts that `sequentialthinking` is in the list of tools returned by the client (line 83: `assert "sequentialthinking" in names`).
- **TestSequentialThinkingViaClient::test_sequentialthinking_via_client** — Calls the `sequentialthinking` tool with sample arguments and asserts the response shape (`thoughtNumber`, `totalThoughts`, `nextThoughtNeeded`, `branches`, `thoughtHistoryLength`).

When you run integration tests with `USE_REAL_FASTMCP=1`, they verify that the in-repo sequential thinking tool is discoverable and callable via the real FastMCP client.

## MCP Evaluation

An evaluation harness for testing LLM usability of the MCP server is provided:

- **Evaluation questions**: [evaluations/uml_mcp_eval.xml](../evaluations/uml_mcp_eval.xml) — 10 read-only Q&A pairs answerable from `uml://` resources.
- **Script**: [scripts/evaluation.py](../scripts/evaluation.py) — Verifies server connection and tools/resources discovery.

To run the connectivity check:

```bash
python scripts/evaluation.py -t stdio -c python -a server.py evaluations/uml_mcp_eval.xml
```

For full evaluation with Claude (requires `anthropic`), use the evaluation harness from the MCP Development Guide.

## Summary

| Topic                     | Detail                                                                                    |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| **Why skipped**           | `USE_REAL_FASTMCP` is not set; skip is intentional.                                       |
| **Run integration tests** | `USE_REAL_FASTMCP=1 uv run pytest tests/integration -v` (or set env in PowerShell first). |
| **Testing approach**      | Default suite stays fast; integration tests are opt-in and use conftest/fixtures.          |
| **Sequential thinking**   | In-repo MCP tool `sequentialthinking`; integration tests check it is listed and callable. |

No code changes are required to “fix” the skips; they are the intended behavior. To see the integration tests execute, run them with the environment variable above.
