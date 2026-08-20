# Stage 22.3 - Retrieval Relevance Evaluation Contract

## Objective

Evaluate whether the RAG retrieval pipeline returns documents that are
semantically relevant to the user's query.

## Scope

This stage evaluates retrieval relevance only.

It does not evaluate:

- LLM answer correctness
- citation correctness
- conversational quality
- final response quality

Those concerns are evaluated in later Stage 22 sub-stages.

## Relevance Requirements

### Requirement 1: Relevant document retrieval

A query about a known topic in the knowledge base should retrieve at least
one document containing relevant information.

### Requirement 2: Source preservation

Retrieved documents must preserve source metadata such as:

- filename
- page information

### Requirement 3: Query-content overlap

For known evaluation queries, retrieved content should contain meaningful
terms related to the expected topic.

### Requirement 4: Ranking sanity

The most relevant retrieved result should not be ranked below clearly
irrelevant results for the same query.

### Requirement 5: Multiple topic coverage

Evaluation should contain queries from different sections of the detailed
employee handbook rather than testing only one topic.

### Requirement 6: No retrieval-pipeline assumptions

Tests must use the project's existing hybrid retrieval interface.

Tests must not depend on the existence of a dedicated `bm25_retriever.py`
file.

## Evaluation Principle

Retrieval quality should be measured independently from answer generation.

The evaluator should inspect the retrieved documents directly.

## Expected Outcome

Known questions should retrieve content related to their expected topics,
with source metadata preserved.

## Pass Criteria

All relevance tests must pass.

The retrieval system must demonstrate meaningful retrieval across multiple
knowledge-base topics.

## Out of Scope

The following are intentionally excluded:

- LLM answer quality
- hallucination detection
- citation correctness
- multi-turn answer quality
- API behavior