# Stage 22.1 - RAG Evaluation Contract

## 1. Purpose

The RAG Evaluation Contract defines the minimum evaluation dimensions
required to assess the quality of the PDF Q&A RAG system.

The contract separates RAG quality into multiple measurable dimensions
instead of treating answer correctness as a single metric.

---

## 2. Evaluation Dimensions

### 2.1 Retrieval Quality

Measures whether the retrieval system returns relevant documents
required to answer the user query.

Input:

- User query
- Retrieved documents
- Expected relevant sources when available

Output:

- Retrieval score

---

### 2.2 Answer Relevance

Measures whether the generated answer directly addresses the
user's question.

Input:

- User query
- Generated answer

Output:

- Answer relevance score

---

### 2.3 Groundedness / Faithfulness

Measures whether the generated answer is supported by the retrieved
context and does not introduce unsupported claims.

Input:

- Retrieved context
- Generated answer

Output:

- Groundedness score

---

### 2.4 Citation Quality

Measures whether the sources returned with the answer are relevant
to the generated answer.

Input:

- Generated answer
- Retrieved documents
- Returned source references

Output:

- Citation score

---

### 2.5 Conversation Continuity

For multi-turn RAG interactions, evaluation must verify that follow-up
questions correctly use conversation context.

Input:

- Conversation history
- Current user query
- Rewritten query
- Retrieved context
- Generated answer

Output:

- Conversation continuity result

---

## 3. Evaluation Result Contract

A future evaluation result should contain at minimum:

- Original query
- Retrieval score
- Answer relevance score
- Groundedness score
- Citation score
- Overall score

The exact implementation may evolve in later Stage 22 sub-stages.

---

## 4. Score Contract

Individual evaluation dimensions use a normalized score:

0.0 <= score <= 1.0

Where:

- 0.0 = completely unsatisfactory
- 0.5 = partially satisfactory
- 1.0 = fully satisfactory

Scores must remain numeric and bounded.

---

## 5. Overall Score

The overall evaluation score represents the combined quality of the
RAG response across the defined evaluation dimensions.

The weighting strategy is intentionally left for a later Stage 22
sub-stage.

Stage 22.1 defines the contract only and does not prescribe the final
scoring algorithm.

---

## 6. Evaluation Principles

The evaluation system must:

1. Evaluate retrieval separately from generation.
2. Evaluate generated answers against the user query.
3. Verify that answers are grounded in retrieved context.
4. Evaluate citation/source correctness.
5. Support multi-turn conversational RAG.
6. Use normalized scores where numerical scoring is applicable.
7. Keep evaluation independent from the production RAG pipeline.
8. Produce deterministic and testable evaluation results where possible.

---

## 7. Scope of Stage 22.1

Stage 22.1 defines and verifies the evaluation contract only.

It does not implement:

- Retrieval metrics
- LLM-based answer evaluation
- Groundedness evaluation algorithms
- Citation scoring algorithms
- Evaluation datasets
- Final aggregate scoring

Those responsibilities belong to later Stage 22 sub-stages.