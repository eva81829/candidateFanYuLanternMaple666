# DECISIONS

This file documents the key design decisions for the Locker/Reservation system, including trade-offs and reasoning.

## Repository Pattern
- **Decision**: Define abstract repositories in the domain layer such as `EventStore(ABC)` and `Projection(ABC)` with abstract methods.
- **Why**: The application layer receives `projection` and `event_store` instances and can use their abstract methods directly, without knowing about the underlying storage implementation.
- **Implementation**: Concrete implementations of these repositories are defined in the infrastructure layer.
- **Trade-off**: Adds some abstraction code, but allows the application to remain independent of infrastructure and prevents direct database access.
