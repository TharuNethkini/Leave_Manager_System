from datetime import datetime
from utils import validate_date

class EmployeeManager:
    def __init__(self, db):
        # Initialize with a reference to the database object
        self.db = db

    def employee_exists(self, name):
        # Check if an employee exists in the database by their name
        return name in self.db.data.get("employees", {})

    def is_manager(self, name):
        # Determine if a given employee has manager privileges
        return self.db.data["employees"].get(name, {}).get("is_manager", False)

    def handle_intent(self, name, intent, entities):
        # Main method to process an employee's request based on intent and extracted entities

        # Confirm the employee exists in the system
        if name not in self.db.data["employees"]:
            return "Employee not found in the system."

        emp = self.db.data["employees"][name]

        if intent == "check_balance":
            # Handle request to check leave balance
            leave_type = entities.get("leave_type")

            # If no specific leave type requested, return all leave balances
            if not leave_type:
                balances = emp.get("leave_balance", {})
                response_lines = ["Your current leave balances are:"]
                for ltype, balance in balances.items():
                    response_lines.append(f"- {ltype}: {balance} days")
                return "\n".join(response_lines)

            # Return balance for the specified leave type
            balance = emp.get("leave_balance", {}).get(leave_type, 0)
            return f"You have {balance} {leave_type} remaining."

        elif intent == "request_leave":
            # Handle leave request

            leave_type = entities.get("leave_type")
            num_days = entities.get("num_days")
            start_date = entities.get("start_date")

            # Validate that leave type is provided
            if not leave_type:
                return "Please specify the type of leave you want to request."

            # Validate number of days is provided and a positive integer
            if not num_days:
                return "Please specify how many days you want to take."

            try:
                num_days = int(num_days)
                if num_days <= 0:
                    return "Number of leave days must be a positive integer."
            except (ValueError, TypeError):
                return "Invalid number of leave days."

            # Validate start date presence and format
            if not start_date:
                return "Please provide a valid start date."

            if not validate_date(start_date):
                return "Invalid start date format. Use YYYY-MM-DD."

            # Check if requested start date falls on a holiday
            if start_date in self.db.data["holidays"]:
                return f"{start_date} is a holiday. Choose another date."

            # Verify if the employee has enough leave balance
            balance = emp.get("leave_balance", {}).get(leave_type, 0)
            if balance < num_days:
                return f"Sorry, you only have {balance} {leave_type} leave left."

            # Deduct leave days from balance and add leave request to history with Pending status
            emp["leave_balance"][leave_type] -= num_days
            leave_entry = {
                "type": leave_type,
                "days": num_days,
                "start_date": start_date,
                "status": "Pending",
                "requested_on": str(datetime.today().date())
            }

            # Initialize leave history list if it doesn't exist
            if "leave_history" not in emp:
                emp["leave_history"] = []
            emp["leave_history"].append(leave_entry)

            # Save changes to database and log the action
            self.db.data["employees"][name] = emp
            self.db.save()
            self.db.log_action(f"{name} requested {num_days} {leave_type} leave(s) from {start_date}. Pending approval.")

            return f"{num_days} {leave_type} leave(s) requested from {start_date}. Pending manager approval."

        elif intent == "cancel_leave":
            # Handle leave cancellation requests

            date = entities.get("start_date")
            leave_type = entities.get("leave_type")
            history = emp.get("leave_history", [])

            # No leave history means nothing to cancel
            if not history:
                return "You have no leave history."

            # Require both leave type and start date for cancellation to avoid ambiguity
            if not leave_type or not date:
                return "Please specify both the type of leave and the start date to cancel a leave request."

            # Validate the start date format
            if not validate_date(date):
                return "Invalid start date format. Use YYYY-MM-DD."

            cancelled_any = False
            # Look for matching leave requests with status Approved or Pending to cancel
            for req in history:
                if req["status"] in ["Approved", "Pending"]:
                    if req["start_date"] == date and req["type"] == leave_type:
                        req["status"] = "Cancelled"
                        # Restore leave days back to employee's balance
                        emp["leave_balance"][req["type"]] += req["days"]
                        cancelled_any = True
                        break

            # If cancellation successful, save and log; otherwise, notify no match found
            if cancelled_any:
                self.db.data["employees"][name] = emp
                self.db.save()
                self.db.log_action(f"{name} cancelled a leave request for {leave_type} starting on {date}.")
                return "Leave cancelled successfully."
            return "No matching leave found to cancel."

        elif intent == "view_history":
            # Display the employee's leave history
            history = emp.get("leave_history", [])
            if not history:
                return "You have no leave history."
            # Format the leave records for display
            return "\n".join([
                f"{h['type']} leave on {h['start_date']} for {h['days']} day(s) - {h['status']}"
                for h in history
            ])

        elif intent == "approve_leave" and self.is_manager(name):
            # Manager approval for leave requests

            target = entities.get("employee_name")
            # Check if target employee exists
            if not target or target not in self.db.data["employees"]:
                return "Employee not found."

            emp_target = self.db.data["employees"][target]
            # Filter for pending leave requests for the target employee
            pending = [l for l in emp_target.get("leave_history", []) if l["status"] == "Pending"]

            # No pending requests means nothing to approve
            if not pending:
                return "No pending requests for this employee."

            # Approve all pending requests
            for req in pending:
                req["status"] = "Approved"

            # Save changes and log approval action
            self.db.save()
            self.db.log_action(f"{name} approved all pending leaves for {target}.")
            return f"All pending leaves for {target} have been approved."

        # Return default message if intent not recognized
        return "Sorry, I didn't understand that."

    def add_employee(self, name, leave_balances, is_manager=False):
        # Add a new employee record with leave balances and optional manager status
        if name in self.db.data["employees"]:
            return "Employee already exists."
        self.db.data["employees"][name] = {
            "leave_balance": leave_balances,
            "is_manager": is_manager,
            "leave_history": []
        }
        # Save changes and log the addition
        self.db.save()
        self.db.log_action(f"Admin added new employee {name}.")
        return f"Employee {name} added successfully."

    def edit_employee(self, name, leave_balances=None, is_manager=None):
        # Edit existing employee's leave balances and/or manager status
        if name not in self.db.data["employees"]:
            return "Employee not found."
        emp = self.db.data["employees"][name]

        if leave_balances is not None:
            emp["leave_balance"] = leave_balances
        if is_manager is not None:
            emp["is_manager"] = is_manager

        # Save changes and log the edit
        self.db.data["employees"][name] = emp
        self.db.save()
        self.db.log_action(f"Admin edited employee {name}.")
        return f"Employee {name} updated successfully."

    def add_holiday(self, date):
        # Add a new holiday date to the system to block leave requests on that date
        if date in self.db.data["holidays"]:
            return "Holiday already exists."
        self.db.data["holidays"].append(date)
        # Save changes and log the new holiday
        self.db.save()
        self.db.log_action(f"Admin added holiday {date}.")
        return f"Holiday {date} added."
