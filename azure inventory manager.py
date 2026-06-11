from collections import deque
import heapq
import pandas as pd
from datetime import datetime

# ============================================================
# Azure-Inventory-Manager
# Developer: Terri | Cloud Infrastructure Tool
# Purpose: Track Azure VMs, manage status updates,
#          prioritize alerts, and generate cost reports
# ============================================================

# --- Data Structure 1: Hash Table (dictionary) ---
# Supports fast VM lookup and real-time status updates
vm_inventory = {}

# --- Data Structure 2: Queue (deque) ---
# Manages incoming status change requests in FIFO order
status_queue = deque()

# --- Data Structure 3: Heap (priority queue) ---
# Surfaces high-priority VM alerts (cost overruns, critical states)
alert_queue = []
alert_counter = 0

VALID_STATUSES = {"running", "stopped", "deallocated"}


def add_vm(vm_id, vm_name, resource_group, status, region, monthly_cost):
    """Add or update a VM in the inventory hash table."""
    try:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Valid statuses: {', '.join(sorted(VALID_STATUSES))}")
        if not isinstance(monthly_cost, (int, float)) or monthly_cost < 0:
            raise ValueError("Monthly cost must be a non-negative number.")

        vm_inventory[vm_id] = {
            "name": vm_name,
            "resource_group": resource_group,
            "status": status,
            "region": region,
            "monthly_cost": monthly_cost,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        print(f"VM added: {vm_id} - {vm_name} | Status: {status} | Region: {region} | Cost: ${monthly_cost}/mo")

    except ValueError as e:
        print(f"Error adding VM: {e}")


def get_vm(vm_id):
    """Retrieve a VM record from inventory by VM ID."""
    try:
        if vm_id not in vm_inventory:
            raise KeyError(f"VM ID '{vm_id}' not found in inventory.")
        vm = vm_inventory[vm_id]
        print(f"VM Found: {vm}")
        return vm
    except KeyError as e:
        print(f"Error: {e}")
        return None


def queue_status_update(vm_id, new_status):
    """Add a status change request to the FIFO deque queue."""
    try:
        if vm_id not in vm_inventory:
            raise KeyError(f"VM ID '{vm_id}' not found in inventory.")
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Valid statuses: {', '.join(sorted(VALID_STATUSES))}")

        request = {"vm_id": vm_id, "new_status": new_status}
        status_queue.append(request)
        print(f"Status update queued: {vm_id} -> {new_status}")

    except (KeyError, ValueError) as e:
        print(f"Error queuing status update: {e}")


def process_status_update():
    """Process the next status update request from the deque queue (FIFO)."""
    try:
        if len(status_queue) == 0:
            raise IndexError("No status updates in the queue.")

        request = status_queue.popleft()
        vm_id = request["vm_id"]
        new_status = request["new_status"]

        if vm_id not in vm_inventory:
            raise KeyError(f"VM ID '{vm_id}' not found in inventory.")

        old_status = vm_inventory[vm_id]["status"]
        vm_inventory[vm_id]["status"] = new_status
        vm_inventory[vm_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"Status updated: {vm_id} | {old_status} -> {new_status}")

    except (IndexError, KeyError) as e:
        print(f"Error processing status update: {e}")


def add_alert(priority, vm_id, alert_message):
    """Add a high-priority VM alert to the heap-based priority queue."""
    global alert_counter
    try:
        if not isinstance(priority, int) or priority < 1:
            raise ValueError("Priority must be a positive integer. Lower number = higher priority.")
        if vm_id not in vm_inventory:
            raise KeyError(f"VM ID '{vm_id}' not found in inventory.")

        alert = (priority, alert_counter, vm_id, alert_message)
        heapq.heappush(alert_queue, alert)
        alert_counter += 1
        print(f"Alert added: Priority {priority} | {vm_id} | {alert_message}")

    except (ValueError, KeyError) as e:
        print(f"Error adding alert: {e}")


def process_alert():
    """Process the highest priority alert from the heap."""
    try:
        if len(alert_queue) == 0:
            raise IndexError("No alerts in the queue.")

        priority, counter, vm_id, alert_message = heapq.heappop(alert_queue)
        print(f"Processing alert: Priority {priority} | {vm_id} | {alert_message}")
        return vm_id, alert_message

    except IndexError as e:
        print(f"Error processing alert: {e}")


def generate_cost_report():
    """Generate a real-time VM cost and usage report using pandas DataFrame."""
    try:
        if len(vm_inventory) == 0:
            raise ValueError("VM inventory is empty. No report to generate.")

        report_data = []
        for vm_id, details in vm_inventory.items():
            report_data.append({
                "VM ID": vm_id,
                "VM Name": details["name"],
                "Resource Group": details["resource_group"],
                "Status": details["status"],
                "Region": details["region"],
                "Monthly Cost ($)": details["monthly_cost"],
                "Last Updated": details["last_updated"]
            })

        df = pd.DataFrame(report_data)

        print("\n--- Azure VM Inventory & Cost Report ---")
        print(df.to_string(index=False))
        print(f"\nTotal VMs: {len(df)}")
        print(f"Running VMs: {len(df[df['Status'] == 'running'])}")
        print(f"Stopped VMs: {len(df[df['Status'] == 'stopped'])}")
        print(f"Deallocated VMs: {len(df[df['Status'] == 'deallocated'])}")
        print(f"Total Monthly Cost: ${df['Monthly Cost ($)'].sum():,.2f}")

        return df

    except ValueError as e:
        print(f"Error generating report: {e}")
        return None


# ============================================================
# TESTING ALL FUNCTIONS
# ============================================================

print("\n========== TESTING: add_vm ==========")
add_vm("VM001", "prod-web-01", "rg-production", "running", "East US", 150.00)
add_vm("VM002", "prod-db-01", "rg-production", "running", "East US", 300.00)
add_vm("VM003", "dev-app-01", "rg-development", "stopped", "West US", 75.00)
add_vm("VM004", "test-vm-01", "rg-testing", "deallocated", "Central US", 0.00)
add_vm("VM005", "invalid-vm", "rg-test", "unknown", "East US", 50.00)  # Error: invalid status
add_vm("VM006", "negative-vm", "rg-test", "running", "East US", -10.00)  # Error: negative cost

print("\n========== TESTING: get_vm ==========")
get_vm("VM001")
get_vm("VM999")  # Error: VM not found

print("\n========== TESTING: queue_status_update / process_status_update ==========")
queue_status_update("VM003", "running")
queue_status_update("VM004", "running")
queue_status_update("VM001", "invalid")   # Error: invalid status
queue_status_update("VM999", "stopped")   # Error: VM not found
process_status_update()
process_status_update()
process_status_update()  # Edge case: empty queue

print("\n========== TESTING: add_alert / process_alert ==========")
add_alert(1, "VM002", "Cost threshold exceeded - $300/mo")
add_alert(2, "VM001", "CPU usage above 90% for 30 minutes")
add_alert(3, "VM003", "Scheduled maintenance required")
add_alert(-1, "VM001", "Invalid priority test")  # Error: invalid priority
add_alert(1, "VM999", "VM not found test")        # Error: VM not found
process_alert()
process_alert()
process_alert()  # Edge case: empty alert queue

print("\n========== TESTING: generate_cost_report ==========")
generate_cost_report()

print("\n========== TESTING: empty inventory report ==========")
inventory_backup = vm_inventory.copy()
vm_inventory.clear()
generate_cost_report()  # Edge case: empty inventory
vm_inventory.update(inventory_backup)
