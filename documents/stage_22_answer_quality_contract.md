# Stage 22.4.1 - Answer Quality Contract

## Purpose

This contract defines the quality requirements for answers generated
by the RAG system.

The objective is to verify that generated answers are useful,
question-relevant, grounded in retrieved documents, and structurally
compatible with the RAG response contract.

## Answer Quality Requirements

### 1. Answer Existence

Every valid question must produce a non-empty answer.

Requirements:

- answer must not be None
- answer must be a string
- answer must not be empty after trimming whitespace

### 2. Question Relevance

The generated answer must address the user's question.

The answer does not need to use the exact wording of the question,
but its meaning must correspond to the requested information.

### 3. Context Grounding

The generated answer must be supported by the retrieved documents.

The system must not introduce factual claims that contradict the
retrieved context.

### 4. Unsupported Fabrication

The generated answer should not invent:

- policy rules
- numerical values
- dates
- eligibility conditions
- benefits
- procedural requirements

when those claims are not supported by the retrieved context.

### 5. Response Structure

Every successful generation must return a valid RAGResponse.

The response must contain:

- answer
- sources

The answer must be a string.

The sources must remain a list of SourceReference objects.

### 6. Source Preservation

Answers generated from retrieved documents must preserve the
corresponding source references.

Source references must identify the relevant document and page
information where available.

## Evaluation Principle

Evaluation should focus on semantic correctness and grounding rather
than exact string matching.

Equivalent answers expressed using different wording should be treated
as acceptable when they communicate the same information.

## Acceptance Criteria

Stage 22.4.1 is complete when:

- answer existence is defined
- question relevance is defined
- context grounding is defined
- unsupported fabrication is defined
- response structure is defined
- source preservation is defined
- evaluation principles are documented