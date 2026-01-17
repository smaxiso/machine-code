
# Peer-to-Peer Delivery System

A flexible, thread-safe delivery management system implemented in Python.

## Features Implemented
*   **Core Flow**: User Onboarding, Order Creation, Driver Assignment, Pickup, Delivery.
*   **Assignment**: Auto-assigns orders to available drivers. queues orders if all drivers busy.
*   **Cancellation**: Supports cancelling orders (unless already picked up).
*   **Payment**: Supports multiple payment modes (UPI, Cash, Wallet).
*   **Scheduler**: Background thread to clean up/cancel expired orders (older than 30 mins).
*   **Dashboard**: View top drivers by rating.
*   **Thread Safety**: Handles concurrent order requests safely.

## Project Structure
*   `models/`: Data classes (Order, Driver, Customer).
*   `services/`: Business logic (OrderService, AssignmentService, etc.).
*   `repositories/`: In-memory storage.
*   `strategies/`: Assignment strategies (e.g., FirstAvailable).
*   `main.py`: Interactive demo script covering all scenarios.

## How to Run
Run the demonstration script which executes the full lifecycle including concurrency tests:

```bash
python main.py
```

## How to Test
Run the full test suite (Unit + Integration + Stress tests):

```bash
python -m unittest discover tests
```

## Design Notes
*   **In-Memory Storage**: Uses Python dictionaries with `RLock` for concurrency.
*   **Architecture**: Service-Layer pattern with Dependency Injection.
*   **Extensibility**: Enums used for types/statuses to allow easy extension.
