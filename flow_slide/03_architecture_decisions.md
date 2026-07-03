# Architecture Decision Records Summary

ADR-001: React + Vite
- Chosen for simplicity and maintainability
- Avoid Angular overhead

ADR-002: No Next.js (current phase)
- No SSR or SEO needs
- Internal system only
- Simpler architecture preferred

ADR-003: FastAPI BFF
- Python ecosystem alignment
- Direct RabbitMQ integration

ADR-004: REST + SSE
- REST for commands (discrete actions)
- SSE for events (streaming updates)
- WebSocket reserved for future needs

ADR-005: Network Independence
- RabbitMQ enables cross-zone communication
- Future deployment flexibility
