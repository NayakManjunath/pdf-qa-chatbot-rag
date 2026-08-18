# Stage 21.1 - Multi-turn Conversation Contract

## Purpose

Define the behavioral contract for multi-turn conversational RAG.

## Contract

1. Conversation history preserves message order.
2. Original user queries are preserved.
3. Follow-up questions may use previous conversation context.
4. Query rewriting produces a retrieval-oriented standalone query.
5. Query rewriting must not generate answers.
6. Query rewriting must not introduce unsupported facts.
7. New topics must not inherit irrelevant previous context.
8. Conversation history must remain bounded.
9. Retrieved documents remain separate from conversation history.
10. Every generated RAG response preserves source references.
11. Conversation state is updated only after successful answer generation.
12. Failed retrieval/generation must not corrupt conversation state.

## Example

### Turn 1

User:
How many sick leave days do employees get?

Assistant:
Employees receive 10 paid sick leave days annually.

### Turn 2

User:
What about the medical certificate?

Internal rewritten query:
medical certificate requirement for sick leave

Assistant:
A medical certificate may be required for absences longer than two consecutive days.

Source:
employee_handbook.pdf, Page 1

### Turn 3

User:
What is the refund policy?

Internal rewritten query:
refund policy

The previous sick-leave context must not incorrectly influence this query.

## Architectural Principle

Conversation history provides context.

Retrieval provides evidence.

The LLM generates the answer only from retrieved evidence and permitted conversational context.