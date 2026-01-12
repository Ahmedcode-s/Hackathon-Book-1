# Architecture Plan: FastAPI RAG Agent Integration

## 1. Scope and Dependencies

### In Scope:
- Create `backend/api.py` with FastAPI endpoints for RAG agent communication
- Integrate with existing RAG agent in `backend/agent.py`
- Add chatbot UI component to existing Docusaurus frontend in `book_robotic_minds/`
- Enable communication between frontend and backend via API
- Support passing user queries and optional selected text to the RAG agent
- Return grounded responses with source metadata to the frontend

### Out of Scope:
- Complete redesign of the existing Docusaurus site
- Authentication or user management features
- Advanced chat history persistence
- Real-time streaming responses (though this could be a future enhancement)
- Full-scale production deployment considerations

### External Dependencies:
- FastAPI: Web framework for backend API
- Pydantic: Data validation for request/response models
- React: Frontend component framework (already in Docusaurus)
- Existing RAG agent implementation in `backend/agent.py`
- Qdrant Cloud: Vector database for retrieval
- OpenRouter: LLM provider for agent responses

## 2. Key Decisions and Rationale

### Options Considered:
1. **API Framework Choice**: FastAPI vs Flask vs Django Rest Framework
   - Trade-offs: FastAPI offers automatic API documentation and better performance, but Flask is simpler
   - Rationale: FastAPI chosen for its automatic OpenAPI/Swagger documentation, async support, and type validation

2. **Frontend Integration Approach**: New page vs Chat widget overlay vs Sidebar component
   - Trade-offs: New page is isolated but harder to access; Widget is convenient but might impact UX
   - Rationale: Chat widget approach for seamless integration with existing content

3. **Data Transfer Format**: JSON vs GraphQL vs gRPC
   - Trade-offs: JSON is simpler and more compatible; GraphQL offers flexibility; gRPC is efficient
   - Rationale: JSON over HTTP for maximum compatibility with web frontend

### Principles:
- Maintain backward compatibility with existing RAG agent functionality
- Use type hints and Pydantic models for data validation
- Implement proper error handling and logging
- Keep the API lightweight and responsive

## 3. Interfaces and API Contracts

### Public APIs:

#### POST /api/chat
**Inputs:**
- `query`: string (required) - The user's natural language question
- `selected_text`: string (optional) - Additional context from user selection
- `top_k`: integer (optional, default: 5) - Number of results to retrieve from Qdrant
- `min_score`: float (optional, default: 0.3) - Minimum similarity threshold

**Outputs:**
- `answer`: string - The agent's response to the query
- `confidence_score`: float - Confidence level in the response (0.0-1.0)
- `sources_used`: array of strings - URLs of sources used in the response
- `processing_time`: float - Time taken to process the request in seconds
- `grounding_validation_passed`: boolean - Whether response passed grounding validation

**Errors:**
- 400: Bad Request - Missing required parameters or invalid input
- 422: Unprocessable Entity - Validation errors
- 500: Internal Server Error - Agent processing failure

#### GET /api/health
**Outputs:**
- `status`: string - "healthy" if all services are available
- `timestamp`: string - ISO timestamp of the health check

### Versioning Strategy:
- Use semantic versioning for API endpoints
- Start with v1 endpoints: `/api/v1/chat`
- Maintain backward compatibility for minor versions

### Error Taxonomy:
- 400: Client-side errors (invalid input, missing parameters)
- 422: Validation errors (malformed data, out-of-range values)
- 500: Server-side errors (service unavailability, processing failures)

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance:
- p95 latency: < 5 seconds for API responses under normal load
- Throughput: Support up to 10 concurrent requests
- Resource caps: API should use < 512MB memory under normal load

### Reliability:
- SLOs: 99% uptime during business hours
- Error budget: Allow 1% error rate
- Degradation strategy: Graceful degradation when Qdrant or OpenRouter is unavailable

### Security:
- AuthN/AuthZ: No authentication required for this phase (public access)
- Data handling: No sensitive user data stored
- Secrets: API keys managed via environment variables only
- Auditing: Log API requests for debugging (no PII)

### Cost:
- Unit economics: Minimize API calls to external services
- Optimize query frequency to reduce costs with OpenRouter

## 5. Data Management and Migration

### Source of Truth:
- Frontend: Docusaurus React components in `book_robotic_minds/`
- Backend: FastAPI application in `backend/api.py`
- Agent: RAG agent logic in `backend/agent.py`

### Schema Evolution:
- Use Pydantic models for request/response validation
- Version API endpoints to handle schema changes

### Data Retention:
- No persistent data retention planned for this phase
- Session data maintained client-side

## 6. Operational Readiness

### Observability:
- Logs: Structured logging for API requests and errors
- Metrics: Response times, error rates, request counts
- Traces: Request tracing for debugging

### Alerting:
- Thresholds: Alert on >5% error rate or >10s response time
- On-call owners: Not applicable for this development phase

### Runbooks:
- Startup procedures for FastAPI server
- Troubleshooting guide for common issues

### Deployment and Rollback:
- Local development setup with environment variables
- Simple restart for rollback

### Feature Flags:
- Not implemented in this phase

## 7. Risk Analysis and Mitigation

### Top 3 Risks:

1. **Service Availability Risk**: Qdrant or OpenRouter service downtime affects functionality
   - Blast radius: All API requests fail
   - Mitigation: Implement circuit breaker pattern and graceful degradation
   - Kill switch: Health check endpoint to detect service availability

2. **Performance Risk**: Long response times affect user experience
   - Blast radius: Poor user experience, potential timeouts
   - Mitigation: Set reasonable timeouts, implement request queuing if needed
   - Kill switch: Ability to disable API temporarily

3. **Integration Risk**: Issues connecting the existing RAG agent with new API layer
   - Blast radius: API returns errors or incorrect responses
   - Mitigation: Thorough testing of the integration layer
   - Kill switch: Ability to bypass new API layer and call agent directly

## 8. Evaluation and Validation

### Definition of Done:
- [ ] FastAPI server with `/api/chat` endpoint successfully created
- [ ] Endpoint connects to existing RAG agent and returns responses
- [ ] Frontend chatbot UI component implemented and functional
- [ ] API returns proper JSON responses with all required fields
- [ ] Error handling implemented for common failure scenarios
- [ ] Health check endpoint available
- [ ] Frontend successfully communicates with backend API
- [ ] All tests pass (unit and integration)

### Output Validation:
- Format: Responses match the defined API contract
- Requirements: All functional requirements from spec are satisfied
- Safety: No exposure of sensitive information or system internals

## 9. Implementation Phases

### Phase 1: Backend API Development
1. Create `backend/api.py` with FastAPI application
2. Define Pydantic models for request/response validation
3. Implement `/api/chat` endpoint connecting to RAG agent
4. Add health check endpoint
5. Implement error handling

### Phase 2: Frontend Chat Component
1. Create React component for chat interface
2. Implement API communication logic
3. Display responses with source citations
4. Add loading states and error handling

### Phase 3: Integration and Testing
1. Connect frontend to backend API
2. Test end-to-end functionality
3. Validate all edge cases
4. Performance testing