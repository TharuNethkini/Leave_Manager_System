from employee import EmployeeManager
from ai import process_input
from database import Database
from admin import admin_mode  

def main():
    print("Welcome to the Leave Management System!")  
    db = Database("employees.json")  # Load employee data from JSON file
    emp_manager = EmployeeManager(db)  # Initialize employee manager with database

    admins = db.data.get("admins", ["AdminUser"])  # Get list of admins, default to ["AdminUser"]
    
    while True:
        user_type = input("Are you an 'admin' or 'user'? (type 'quit' to exit): ").strip().lower()  
        # Ask if user is admin or regular user or wants to quit
        
        if user_type in ['quit', 'exit']:  # Exit program on 'quit' or 'exit'
            print("Exiting the system. Goodbye!")
            break
        
        if user_type not in ["admin", "user"]:  # Validate input
            print("Invalid choice. Please type 'admin', 'user', or 'quit'.")
            continue

        name = input("Enter your name: ").strip()  # Prompt for user name

        if user_type == "admin":
            if name not in admins:  # Check if name is in admins list
                print("Admin not found. Try again.")
                continue
            admin_mode(emp_manager, db)  # Enter admin mode if valid admin

        elif user_type == "user":
            if not emp_manager.employee_exists(name):  # Check if user exists
                print("User not found. Try again.")
                continue

            print(f"\nHello {name}! You are now logged in.")  # Greeting message
            print("Type your request. Type 'quit' to log out and return to main menu.")

            while True:  # Loop for user input handling
                user_input = input(">> ").strip()
                if user_input.lower() == "quit":  # User logs out
                    print("Logging out...\n")
                    break

                intent, entities = process_input(user_input)  # Extract intent and entities using AI
                response = emp_manager.handle_intent(name, intent, entities)  # Process intent via EmployeeManager
                print(response)  # Output the response


if __name__ == "__main__":
    main()  # Run main program loop
