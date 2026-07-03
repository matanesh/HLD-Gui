# System Architecture Overview

Project: Modern GUI for existing Python Core system

Stack:
- Frontend: React + Vite
- BFF: FastAPI
- Messaging: RabbitMQ
- Backend: Existing Python Core

Flows:
Command Flow:
Browser -> REST -> FastAPI -> RabbitMQ -> Python Core

Event Flow:
Python Core -> RabbitMQ -> FastAPI -> SSE -> Browser

Principles:
- Frontend = UI only
- Business logic remains in backend
- BFF is translation layer
- Minimal backend changes
