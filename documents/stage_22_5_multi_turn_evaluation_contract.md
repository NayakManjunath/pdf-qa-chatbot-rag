# Stage 22.5 Multi-turn RAG Evaluation Contract

## 1. Purpose

Stage 22.5 evaluates the ability of the conversational RAG system to maintain
correct retrieval and answer quality across multiple conversation turns.

The evaluation focuses on conversation-level behavior rather than isolated
single-turn question answering.

---

## 2. Multi-turn Conversation Model

A conversation consists of an ordered sequence of user questions and assistant
answers.

Example:

Turn 1:
USER -> Question 1
ASSISTANT -> Answer 1

Turn 2:
USER -> Follow-up Question 2
ASSISTANT -> Answer 2

Turn 3:
USER -> Follow-up Question 3
ASSISTANT -> Answer 3

The order of completed turns must be preserved.

---

## 3. Conversation Continuity

The system must preserve relevant conversational context across turns.

A follow-up question may depend on information established in an earlier turn.

Example:

USER:
How many sick leave days are employees entitled to?

ASSISTANT:
[Answer]

USER:
What about the medical certificate?

The second question must be interpreted using the appropriate previous
conversation context.

---

## 4. Original User Questions

The original user questions must remain unchanged in conversation history.

Query rewriting may be used internally for retrieval, but the rewritten query
must not replace the original user question stored in conversation history.

---

## 5. Retrieval Context

Retrieval for a follow-up question may use conversation context.

However, retrieval processing must not modify or corrupt the conversation
history.

The retrieval query and conversation history are separate concerns.

---

## 6. Answer Generation

Each conversation turn must produce an answer that:

- is non-empty
- addresses the current user question
- uses appropriate retrieved information
- remains grounded in the available document content
- preserves the expected RAG response structure

---

## 7. Source Preservation

Each answer should preserve source references when relevant documents are
retrieved.

Sources must contain valid metadata such as:

- filename
- page information

Source information from one turn must not incorrectly replace or corrupt
source information belonging to another turn.

---

## 8. Multi-turn Consistency

Answers across multiple turns should remain consistent with the information
established by the source documents.

A later follow-up answer must not contradict the previously established answer
without document evidence supporting the change.

---

## 9. Conversation Isolation

Independent conversations must remain isolated.

Information from Conversation A must not leak into Conversation B.

---

## 10. Long Conversation Behavior

The system must remain functional when multiple turns are performed.

Conversation history must respect the configured history limit.

Older messages may be removed according to the history policy, but the remaining
messages must preserve their original order.

---

## 11. Edge Cases

The evaluation should consider:

- standalone questions
- follow-up questions
- repeated questions
- topic changes
- short follow-up questions
- ambiguous references
- multiple consecutive follow-ups
- conversation history limits

---

## 12. Evaluation Principle

Stage 22.5 is successful when the system demonstrates reliable conversational
RAG behavior across multiple turns while preserving:

1. conversation continuity
2. original user questions
3. retrieval correctness
4. answer relevance
5. answer grounding
6. source integrity
7. conversation isolation
8. history ordering
9. response structure

---

## 13. Stage Completion Criteria

Stage 22.5 will be considered complete when:

- all Stage 22.5 sub-stage evaluations pass
- multi-turn conversations remain coherent
- follow-up retrieval uses appropriate context
- answers remain relevant and grounded
- sources remain valid
- conversation state remains isolated
- long conversations respect history limits
- edge cases are handled
- final Stage 22.5 integration tests pass
- `git diff --check` passes
- the final Stage 22.5 changes are committed and pushed to GitHub