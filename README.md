# README

## How to Run the API
1. Clone the repository:
```bash
git clone https://github.com/eva81829/candidateFanYuLanternMaple666.git
cd candidateFanYuLanternMaple666
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the API server:
```
uvicorn interface.api:app --reload
```

## How to run tests
```
pytest -v tests/test.py  
```

## Short architecture and design rationale
The system is structured following the principles of **Clean Architecture**, divided into four layers: **Interface**, **Infrastructure**, **Application**, and **Domain**.

- **Interface**  
  The entry point of the program is `api.py`, which handles incoming requests from clients.

- **Infrastructure**  
  This layer manages data storage and persistence. `InMemoryProjection` keeps lockers, reservations, and compartments in memory for fast access, while `FileEventStore` handles reading and writing events to disk for durability.

- **Application**  
  This layer is responsible for handling events and providing query methods such as `get_locker_state`, `get_compartment_state`, and `get_reservation_state`. It coordinates between the interface and the domain.

- **Domain**  
  This layer defines entities and aggregates, encapsulating the core business logic and rules.

By separating responsibilities across these layers, the system keeps business rules independent of infrastructure and interface concerns.
