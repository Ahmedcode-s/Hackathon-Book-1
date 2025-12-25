<!--
Sync Impact Report:
Version change: N/A → 1.0.0
Modified principles: N/A (new constitution)
Added sections: All principles and sections
Removed sections: None
Templates requiring updates: ✅ updated / ⚠ pending
Follow-up TODOs: None
-->

# AI-Driven Book with Integrated RAG Chatbot Constitution

## Core Principles

### I. Specification-First Development
Every feature and component must be fully specified before implementation begins; Specifications must define goals, inputs/outputs, constraints, and acceptance criteria; No implementation without an approved specification.

### II. Technical Accuracy and AI-Native Explanations
All content and code examples must be technically accurate and verified; Explanations must be designed for AI-native audiences with clear, precise terminology; No hallucinated APIs, frameworks, or technologies - all must be current and stable.

### III. Modular Content Architecture
Content must be structured as modules → chapters → sections with logical flow from concept → architecture → implementation; Each module must be self-contained and independently deployable; Clear dependencies and relationships between modules must be documented.

### IV. Reproducible and Production-Grade Implementation
All implementations must be fully reproducible from the specifications; Code must meet production-grade standards with proper error handling, testing, and documentation; Deployment configurations must be included and tested.

### V. RAG System Integration
The RAG chatbot must answer questions based solely on the book content; System must support retrieval-augmented generation with user-selected text context; Implementation must use the specified technology stack: OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres, Qdrant Cloud.

### VI. Docusaurus-Based Documentation
All book content must be written in Docusaurus using MD/MDX format; Documentation must follow established Docusaurus patterns and best practices; GitHub Pages deployment must be configured and functional.

## Technology Stack Requirements

The project must utilize the following technology stack:
- Book Platform: Docusaurus (MD/MDX)
- RAG Backend: FastAPI
- Database: Neon Serverless Postgres
- Vector Storage: Qdrant Cloud (Free Tier)
- AI Integration: OpenAI Agents / ChatKit SDKs
- Deployment: GitHub Pages
- Repository Structure: Monorepo containing book, chatbot, and specifications

## Development Workflow and Quality Standards

- Specification-first approach using Spec-Kit Plus methodology
- Every module must have clearly defined goals, inputs/outputs, constraints, and acceptance criteria
- Code reviews must verify compliance with all constitution principles
- All implementations must pass testing before merging
- Clean, maintainable code without unnecessary refactoring of unrelated components
- Proper error handling, logging, and observability implementation

## Governance

This constitution supersedes all other development practices and guidelines; All changes to this constitution require explicit approval and documentation; Every pull request must verify compliance with these principles; Code contributions must align with the established architecture and technology stack; Implementation deviations must be justified and approved.

Version: 1.0.0 | Ratified: 2025-12-21 | Last Amended: 2025-12-21
