# Project Summary: Peer-to-Peer Delivery System

## Status Overview

| Requirements | Status | Notes |
| :--- | :--- | :--- |
| **P0 Features** | **COMPLETED** | Core flow (Onboard -> Order -> Assign -> Deliver) |
| **Bonus Features** | **COMPLETED** | Dashboard, Notifications, Timeout Cancellation |

## Detailed Feature Status

### P0 Features (Core)
- [x] **Onboard Customers & Drivers**: Implemented via `CustomerService` and `DriverService`.
- [x] **Place & Cancel Orders**: `OrderService` handles creation and cancellation.
- [x] **Driver Availability**: Drivers can pick up only one order. `DriverStatus.BUSY` ensures exclusivity.
- [x] **Auto-Assignment**: `AssignmentService` automatically assigns orders to available drivers using a strategy.
- [x] **Queueing**: Orders generally queue when no drivers are available and auto-assign when one becomes free.
- [x] **Status Visibility**: Customers/Drivers can query order status.
- [x] **Cancellation Polices**: 
    - Cancelled orders are removed from the driver (driver becomes free).
    - Orders picked up cannot be cancelled.
- [x] **Concurrency**: Thread-safe implementation using `RLock` in repositories and services.

### Bonus Features
- [x] **Notifications**: `NotificationService` logs events for order updates (simulation of Email/SMS).
- [x] **Driver Rating**: Customers can rate drivers; ratings are aggregated.
- [x] **Dashboard**: Ability to view top drivers by rating or order count.
- [x] **Auto-Cancellation (Timeout)**: Orders not picked up within 30 minutes can be cancelled via `cleanup_expired_orders`.
- [x] **Payment System**: Integrated `PaymentService` handling CASH, UPI, WALLET modes with transaction logging.
- [x] **Configuration**: Externalized constants (timeouts, limits) to `config.json` via `ConfigLoader`.
- [x] **Enhanced Notifications**: Separated Email/SMS channels in `NotificationService` and hooked into order lifecycle.
- [x] **Professional Logging**: Replaced `print` with Python's standard `logging` module for timestamped, leveled logs.
- [x] **Background Scheduler**: `SchedulerService` runs on a separate thread to automatically clean up expired orders.
- [x] **Unit & Stress Tests**: Comprehensive suite (`sumits/tests/`) covering mocks, real integration flows, and concurrency stress testing.
### Code Quality
- [x] **Custom Exceptions**: Specific exception classes for all error scenarios.
- [x] **Service Interfaces**: Abstract base classes defining contracts.
- [x] **Input Validation**: Item type and rating validation.
- [x] **Docstrings**: All public methods documented.

## Assumptions & Rationale

| Assumption / Decision | Rationale |
| :--- | :--- |
| **In-Memory Storage** | Used Dictionary + RLock to simulate a database without external dependencies, ensuring P0 requirement of "Standalone application". |
| **Geo-Boundary** | Assumed the system operates within a single region (e.g., Bangalore). No geospatial distance calculation logic was added to keep scope manageable within 2 hours. |
| **Polling vs Event** | For the "Queue" processing, we used a direct trigger (`on_driver_available`) when a driver finishes an order, rather than a background polling loop, for better efficiency and immediate assignment. |
| **Thread Safety** | Used `RLock` (Reentrant Lock) extensively in Repositories and `AssignmentService` to handle concurrency test cases where multiple requests come in simultaneously. |
| **Project Structure** | Refactored into `services/`, `models/`, `enums/` to ensure Separation of Concerns and Extensibility (Flipkart coding standard). |
| **Strict Typing** | Enforced `ItemType` enum usage in `OrderService` to strictly validate allowed delivery items, preventing invalid inputs. |
| **Config Management** | Used `ConfigLoader` singleton to read from `config.json`, allowing non-code updates to system parameters. |
| **Robustness** | Addressed code review feedback: Validated `driver_id`, synced assignment, improved queue processing, and added strict status checks. |

## File Structure
```
peer-to-peer/
├── enums/
│   ├── driver_status.py
│   ├── item_type.py
│   ├── order_status.py
│   └── payment_mode.py
├── exceptions/
│   ├── __init__.py
│   └── custom_exceptions.py
├── models/
│   ├── customer.py
│   ├── driver.py
│   ├── order.py
│   └── payment.py
├── repositories/
│   └── in_memory_repository.py
├── services/
│   ├── interfaces.py
│   ├── assignment_service.py
│   ├── customer_service.py
│   ├── dashboard_service.py
│   ├── driver_service.py
│   ├── notification_service.py
│   ├── order_service.py
│   ├── payment_service.py
│   └── scheduler_service.py
├── strategies/
│   └── matching_strategy.py
├── utils/
│   ├── config_loader.py
│   └── logger.py
├── config.json
├── main.py
├── problem_statement.md
└── project_summary.md
```

## Execution Guide
Run the main demonstration script:
```bash
python3 main.py
```
This script runs a comprehensive scenario covering happy paths, edge cases (no driver), concurency, and bonus features.

## Running Unit Tests
To run the mock-based unit tests for OrderService and AssignmentService:
```bash
PYTHONPATH=sumits python3 -m unittest discover sumits/tests
```
(This gathers and runs Unit, Integration, and Stress tests automatically)
