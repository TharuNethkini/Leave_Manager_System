from utils import validate_date

def admin_mode(emp_manager, db):
    # Function to display all admin commands available
    def show_commands():
        print("\nAdmin Commands:")
        print("1. Add Employee")
        print("2. Edit Employee")
        print("3. Delete Employee")
        print("4. Add Holiday")
        print("5. Approve Leave Requests")
        print("6. Quit Admin Mode\n")

    # Function to ask admin to input leave balances for different leave types
    # Accepts optional existing_balances to allow editing without losing old data
    def ask_leave_balances(existing_balances=None):
        leave_types = ["Sick Leave", "Annual Leave", "Maternity Leave"]
        balances = {}
        print("Enter leave balances for each leave type (leave empty to keep current balance):")
        for lt in leave_types:
            while True:
                prompt = f"  {lt}"
                if existing_balances:
                    prompt += f" (current: {existing_balances.get(lt,0)}): "
                else:
                    prompt += ": "
                val = input(prompt).strip()

                # If empty input given and editing, keep current balance
                if val == "" and existing_balances:
                    balances[lt] = existing_balances.get(lt, 0)
                    break

                # Prevent empty input when no existing balance
                if val == "":
                    print("This field cannot be empty. Please enter a number (0 if none).")
                    continue
                try:
                    num = int(val)
                    if num < 0:
                        print("Please enter a non-negative number.")
                        continue
                    balances[lt] = num
                    break
                except ValueError:
                    print("Invalid number. Please enter a valid integer.")
        return balances

    # Initially show the list of commands to admin
    show_commands()

    while True:
        choice = input("Enter command number: ").strip()

        # Add Employee workflow
        if choice == "1":
            name = input("Enter new employee name: ").strip()
            leave_balances = ask_leave_balances()  # Get initial leave balances
            is_manager_input = input("Is this employee a manager? (yes/no): ").strip().lower()
            is_manager = is_manager_input == "yes"
            result = emp_manager.add_employee(name, leave_balances, is_manager)
            print(result)
            db.log_action(f"Admin added employee {name} (Manager: {is_manager}) with leave balances {leave_balances}.")

        # Edit Employee workflow
        elif choice == "2":
            employee_names = list(db.data.get("employees", {}).keys())
            if not employee_names:
                print("No employees found.")
                show_commands()
                continue

            print("\nEmployees:")
            for i, name in enumerate(employee_names, 1):
                print(f"{i}. {name}")
            print("Type 'quit' to exit editing.")

            # Loop to select an employee for editing
            while True:
                selection = input("Select employee number to edit or 'quit': ").strip().lower()
                if selection == "quit":
                    break
                if not selection.isdigit() or int(selection) < 1 or int(selection) > len(employee_names):
                    print("Invalid input. Please enter a valid number or 'quit'.")
                    continue
                selected_name = employee_names[int(selection) - 1]
                break  # Valid selection, exit loop

            if selection == "quit":
                show_commands()
                continue

            current_balances = db.data["employees"][selected_name].get("leave_balance", {})
            print("Leave balances edit:")
            leave_balances = ask_leave_balances(current_balances)  # Get updated balances

            # Optionally change manager status
            is_manager_input = input("Change manager status? (yes/no/skip): ").strip().lower()
            is_manager = None
            if is_manager_input == "yes":
                is_manager = True
            elif is_manager_input == "no":
                is_manager = False

            result = emp_manager.edit_employee(selected_name, leave_balances, is_manager)
            print(result)
            db.log_action(f"Admin edited employee {selected_name} with leave balances {leave_balances}. Manager status: {is_manager}.")

        # Delete Employee workflow
        elif choice == "3":
            employee_names = list(db.data.get("employees", {}).keys())
            if not employee_names:
                print("No employees found to delete.")
                show_commands()
                continue

            print("\nEmployees:")
            for i, name in enumerate(employee_names, 1):
                print(f"{i}. {name}")
            print("Type 'quit' to cancel.")

            # Select employee by number or name to delete
            while True:
                selection = input("Select employee number or type employee name to delete or 'quit': ").strip()

                if selection.lower() == "quit":
                    break

                if selection.isdigit():
                    idx = int(selection)
                    if idx < 1 or idx > len(employee_names):
                        print("Invalid number. Please enter a valid number from the list.")
                        continue
                    selected_name = employee_names[idx - 1]
                else:
                    if selection not in employee_names:
                        print("Employee name not found. Please enter a valid name or number.")
                        continue
                    selected_name = selection

                # Confirm deletion before removing
                confirm = input(f"Are you sure you want to DELETE employee '{selected_name}' and all their records? (yes/no): ").strip().lower()
                if confirm == "yes":
                    db.data["employees"].pop(selected_name, None)
                    db.save()
                    print(f"Employee '{selected_name}' has been deleted from the system.")
                    db.log_action(f"Admin deleted employee {selected_name} and all their records.")
                else:
                    print("Deletion cancelled.")
                break

            show_commands()

        # Add Holiday workflow
        elif choice == "4":
            while True:
                date = input("Enter holiday date (YYYY-MM-DD): ").strip()
                if not validate_date(date):
                    print("Invalid date format. Please enter date in YYYY-MM-DD format.")
                    continue
                break

            confirm = input(f"Are you sure you want to add {date} as a holiday? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Holiday addition cancelled.")
                show_commands()
                continue

            result = emp_manager.add_holiday(date)
            print(result)
            db.log_action(f"Admin added holiday on {date}.")

        # Approve Leave Requests workflow
        elif choice == "5":
            users_with_pending = []
            # Find employees who have pending leave requests
            for user, data in db.data.get("employees", {}).items():
                pending = [l for l in data.get("leave_history", []) if l["status"] == "Pending"]
                if pending:
                    users_with_pending.append(user)

            if not users_with_pending:
                print("No pending leave requests from any employee.")
                show_commands()
                continue

            print("\nEmployees with pending leave requests:")
            for i, u in enumerate(users_with_pending, 1):
                print(f"{i}. {u}")
            print("Type 'quit' to cancel.")

            # Select employee to review leave requests
            while True:
                selection = input("Select employee number to review leave requests or 'quit': ").strip().lower()
                if selection == "quit":
                    break
                if not selection.isdigit() or int(selection) < 1 or int(selection) > len(users_with_pending):
                    print("Invalid input. Please enter a valid number or 'quit'.")
                    continue
                target = users_with_pending[int(selection) - 1]
                break

            if selection == "quit":
                show_commands()
                continue

            emp_data = db.data["employees"][target]
            pending = [l for l in emp_data.get("leave_history", []) if l["status"] == "Pending"]

            # For each pending leave request, approve or deny
            for i, req in enumerate(pending, 1):
                print(f"\nRequest {i}: {req['days']} days of {req['type']} leave starting {req['start_date']}.")
                while True:
                    decision = input("Approve or Deny? (a/d): ").strip().lower()
                    if decision == "a":
                        req["status"] = "Approved"
                        print("Request approved.")
                        db.log_action(f"Admin approved {req['days']} {req['type']} leave(s) for {target} starting {req['start_date']}.")
                        break
                    elif decision == "d":
                        req["status"] = "Denied"
                        # Refund leave balance on denial
                        emp_data["leave_balance"][req["type"]] = emp_data["leave_balance"].get(req["type"], 0) + req["days"]
                        print("Request denied and leave balance refunded.")
                        db.log_action(f"Admin denied {req['days']} {req['type']} leave(s) for {target} starting {req['start_date']}.")
                        break
                    else:
                        print("Invalid input. Please enter 'a' to approve or 'd' to deny.")

            db.data["employees"][target] = emp_data
            db.save()

        # Quit admin mode and exit the loop
        elif choice == "6":
            print("Exiting admin mode...")
            break

        else:
            print("Invalid command. Please try again.")
        
        # After processing a valid command (except quit), show commands again
        show_commands()
