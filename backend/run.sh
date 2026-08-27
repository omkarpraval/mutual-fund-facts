#!/usr/bin/env bash
# Backend.
#   Optional generation:  export MF_LLM=groq   GROQ_API_KEY=...
#   Optional intent LLM:  export GROQ_API_KEY=...  (used on unmatched queries)
# Never commit a key. Both are read from the environment only.
pip install fastapi uvicorn rank_bm25 --break-system-packages -q
uvicorn app.api:app --reload --port 8000
