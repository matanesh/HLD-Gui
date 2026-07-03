# UML & Diagram Prompt Pack

## System Architecture Diagram Prompt
Draw a clean enterprise architecture diagram:

Components:
- React + Vite frontend
- FastAPI BFF
- RabbitMQ message broker
- Python Core backend

Show:
- REST command path
- SSE event stream path
- Separation of UI, BFF, Core

## Command Flow UML Prompt
Sequence diagram:

User -> React UI -> FastAPI (REST)
FastAPI -> RabbitMQ -> Python Core
Python Core -> RabbitMQ -> FastAPI
FastAPI -> SSE -> UI

Label as:
Run Command Flow

## Event Flow UML Prompt
Sequence diagram:

Python Core emits events ->
RabbitMQ ->
FastAPI ->
SSE stream ->
Frontend UI updates

Focus:
- logs
- status updates
- progress updates

## Attack / Tool Flow (generic flow extension)
Two-stage flow:

1. Selection phase:
User selects target + config in GUI
FastAPI validates + sends command via RabbitMQ

2. Execution phase:
Core system executes tool/operation
Events streamed back via SSE

## Future Extension Flow
Optional:
WebSocket bidirectional upgrade path
Microservice expansion via RabbitMQ routing keys
