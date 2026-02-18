# AI Prompts

## Final Prompt (Implemented in Ollama Client)
**System**
You are an internal knowledge assistant. Use only the provided context. If the answer is not in the context, respond with: "I don't have enough context to answer that question based on the available documents." Do not guess.

**User**
Question: {{question}}
Context:
{{top_chunks}}

Answer in a concise paragraph.

## Iterations
### v0 (Rejected)
- **Prompt**: "Answer the question using the context."
- **Problem**: Model sometimes added extra information not present in the context.

### v1 (Accepted)
- **Prompt**: Added explicit refusal rule and concise answer instruction.
- **Why accepted**: Reduces hallucinations and makes responses easier to validate.

## Accepted vs Rejected Outputs
**Accepted output**
```
Employees must submit PTO requests 2 weeks in advance.
```

**Rejected output**
```
Employees should submit PTO requests 3 weeks in advance.
```

**Reason**: Answer contradicts the source content; indicates hallucination.

## Notes on Human Judgment
- A human reviewer is needed to validate whether citations actually support the answer.
- If the system returns a refusal, humans can decide if more documents are needed.
