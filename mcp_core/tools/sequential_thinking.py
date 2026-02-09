"""
Minimal sequential-thinking MCP tool for diagram planning and verification.

Mirrors the Node sequential-thinking server API so clients can use the same
workflow: plan → revise → verify → then call generate_uml with final code.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from .tool_decorator import mcp_tool

logger = logging.getLogger(__name__)

SEQUENTIAL_THINKING_DESCRIPTION = """A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
  * Regular analytical steps
  * Revisions of previous thoughts
  * Questions about previous decisions
  * Realizations about needing more analysis
  * Changes in approach
  * Hypothesis generation
  * Hypothesis verification
- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end
- thoughtNumber: Current number in sequence (can go beyond initial total if needed)
- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)
- isRevision: A boolean indicating if this thought revises previous thinking
- revisesThought: If is_revision is true, which thought number is being reconsidered
- branchFromThought: If branching, which thought number is the branching point
- branchId: Identifier for the current branch (if any)
- needsMoreThoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set nextThoughtNeeded to false when truly done and a satisfactory answer is reached"""


class SequentialThinkingHandler:
    """Holds thought history and branches; processes each thought and returns state."""

    def __init__(self) -> None:
        self._thought_history: List[Dict[str, Any]] = []
        self._branches: Dict[str, List[Dict[str, Any]]] = {}
        self._disable_logging = (
            os.environ.get("DISABLE_THOUGHT_LOGGING", "").lower() == "true"
        )

    def _format_thought(
        self,
        thought: str,
        thought_number: int,
        total_thoughts: int,
        is_revision: bool = False,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
    ) -> str:
        if is_revision and revises_thought is not None:
            prefix = "Revision"
            context = f" (revising thought {revises_thought})"
        elif branch_from_thought is not None and branch_id:
            prefix = "Branch"
            context = f" (from thought {branch_from_thought}, ID: {branch_id})"
        else:
            prefix = "Thought"
            context = ""
        header = f"{prefix} {thought_number}/{total_thoughts}{context}"
        border_len = max(len(header), len(thought)) + 4
        border = "─" * border_len
        return f"\n┌{border}┐\n│ {header} │\n├{border}┤\n│ {thought.ljust(border_len - 2)} │\n└{border}┘"

    def process_thought(
        self,
        thought: str,
        next_thought_needed: bool,
        thought_number: int,
        total_thoughts: int,
        is_revision: Optional[bool] = None,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
        needs_more_thoughts: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Process one thought, update state, optionally log, return output dict."""
        if thought_number > total_thoughts:
            total_thoughts = thought_number
        is_rev = is_revision or False
        data: Dict[str, Any] = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "isRevision": is_rev,
            "revisesThought": revises_thought,
            "branchFromThought": branch_from_thought,
            "branchId": branch_id,
            "needsMoreThoughts": needs_more_thoughts,
            "nextThoughtNeeded": next_thought_needed,
        }
        self._thought_history.append(data)
        if branch_from_thought is not None and branch_id:
            if branch_id not in self._branches:
                self._branches[branch_id] = []
            self._branches[branch_id].append(data)
        if not self._disable_logging:
            formatted = self._format_thought(
                thought,
                thought_number,
                total_thoughts,
                is_rev,
                revises_thought,
                branch_from_thought,
                branch_id,
            )
            logger.info(formatted)
        return {
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "branches": list(self._branches.keys()),
            "thoughtHistoryLength": len(self._thought_history),
        }


_handler = SequentialThinkingHandler()


ANNOTATIONS_THINKING = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
}


@mcp_tool(
    name="sequentialthinking",
    description=SEQUENTIAL_THINKING_DESCRIPTION,
    category="thinking",
    annotations=ANNOTATIONS_THINKING,
)
def sequentialthinking(
    thought: str,
    nextThoughtNeeded: bool,
    thoughtNumber: int,
    totalThoughts: int,
    isRevision: Optional[bool] = None,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: Optional[bool] = None,
) -> Dict[str, Any]:
    """Process a single thought and return state (same API as Node sequential-thinking server)."""
    return _handler.process_thought(
        thought=thought,
        next_thought_needed=nextThoughtNeeded,
        thought_number=thoughtNumber,
        total_thoughts=totalThoughts,
        is_revision=isRevision,
        revises_thought=revisesThought,
        branch_from_thought=branchFromThought,
        branch_id=branchId,
        needs_more_thoughts=needsMoreThoughts,
    )
