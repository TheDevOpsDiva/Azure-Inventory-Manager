# Azure-Inventory-Manager

**Tech Stack**

- Python 3.9+
- pandas (reporting and analytics)
- collections.deque (status update queue)
- heapq (priority-based alert management)


**Data Structures Used**

Data Structure	Implementation	Why I Used It
Hash Table	Python Dictionary	Fast VM lookups and status updates
Queue	collections.deque	Processes status updates in the order they’re received
Priority Queue	heapq	Keeps critical alerts at the top of the queue
DataFrame	pandas	Generates inventory and cost reports


**Core Functions**

add_vm()

Adds a new VM to inventory or updates an existing one. VM IDs are used as dictionary keys, which allows for fast lookups and updates.

**Supported statuses:**

- running
- stopped
- deallocated

get_vm()

Retrieves VM details using the VM ID.

queue_status_update()

Adds a VM status change request to the update queue for processing.

process_status_update()

Processes the next status update in the queue and updates the VM record.

add_alert()

Adds infrastructure alerts to a priority queue so higher-priority issues are surfaced first.

process_alert()

Processes the most critical alert currently in the queue.

generate_cost_report()

Builds a real-time inventory and cost report using pandas, including VM counts, status breakdowns, and total monthly spend.


**Setup**

- git clone https://github.com/TheDevOpsDiva/azure-inventory-manager.git
- cd azure-inventory-manager
- pip install pandas
- python3 azure_inventory_manager.py


**Example Usage**

import azure_inventory_manager as aim
aim.add_vm("VM001", "prod-web-01", "rg-production", "running", "East US", 150.00)
aim.get_vm("VM001")
aim.queue_status_update("VM001", "stopped")
aim.process_status_update()
aim.add_alert(1, "VM001", "Cost threshold exceeded")
aim.process_alert()
aim.generate_cost_report()


**Error Handling**

The application validates common issues including:

-  Invalid VM statuses
- Negative monthly costs
- Missing VM IDs
- Invalid alert priorities
- Empty status queues
- Empty alert queues
- Empty inventory reports


**Why These Data Structures?**

**Dictionary (Hash Table)** - VM lookups happen frequently, so using a dictionary provides near constant-time access instead of searching through a list.

**Deque** - Status updates need to be processed in the same order they’re received. Deque is optimized for queue operations and performs better than a standard list for this use case.

**Heap** - Infrastructure alerts don’t all have the same urgency. A heap allows critical alerts to be surfaced without repeatedly sorting the entire collection.

**Pandas** - Reporting becomes much easier when inventory data is structured in a DataFrame. It simplifies aggregation, filtering, and cost calculations while keeping the code cleaner.
