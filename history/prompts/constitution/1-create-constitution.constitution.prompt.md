---
id: 1
title: Create Constitution
stage: constitution
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: ShadowXD
command: /sp.constitution
labels: [constitution,spec-first,ai-book,rag-chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```
/sp.constitution

Project:
AI-Driven Book with Integrated RAG Chatbot

Core Principles:
- Specification-first (Spec-Kit Plus)
- Technical accuracy only
- Clear, AI-native explanations
- Fully reproducible project

Standards:
- Book written in Docusaurus (MD/MDX)
- Structured as modules → chapters → sections
- Content flow: concept → architecture → implementation
- No generic or filler content
- Current, stable APIs only

RAG Chatbot:
- Answers questions about the full book
- Supports answers based only on user-selected text
- Stack:
  - OpenAI Agents / ChatKit SDKs
  - FastAPI
  - Neon Serverless Postgres
  - Qdrant Cloud (Free Tier)

Specification Rules:
- Every module must define:
  - Goals
  - Inputs / Outputs
  - Constraints
  - Acceptance criteria
- No implementation without spec

Constraints:
- Docusaurus + GitHub Pages deployment
- Monorepo: book, chatbot, specs
- Clean, production-grade code

Success Criteria:
- Successful build and deployment
- Functional RAG chatbot
- Zero spec deviation

Failure Conditions:
- Hallucinated APIs
- Missing specs
- Broken chatbot or deployment
```

## Response snapshot

Created a comprehensive constitution for the AI-Driven Book with Integrated RAG Chatbot project based on the provided specifications. The constitution includes:

1. Core Principles:
   - Specification-First Development
   - Technical Accuracy and AI-Native Explanations
   - Modular Content Architecture
   - Reproducible and Production-Grade Implementation
   - RAG System Integration
   - Docusaurus-Based Documentation

2. Technology Stack Requirements:
   - Docusaurus for book content
   - FastAPI for backend
   - Neon Serverless Postgres for database
   - Qdrant Cloud for vector storage
   - OpenAI Agents/ChatKit SDKs for AI integration

3. Development Workflow and Quality Standards:
   - Spec-Kit Plus methodology
   - Clear specifications with goals, inputs/outputs, constraints, and acceptance criteria
   - Code review compliance requirements

4. Governance:
   - Constitution supremacy and amendment procedures

## Outcome

- ✅ Impact: Established foundational governance for the AI-Driven Book project
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with project-specific principles
- 🔁 Next prompts: Continue with spec creation using /sp.specify
- 🧠 Reflection: Constitution properly captures all specified project requirements and constraints

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create initial feature specification