# Leave Management System

This is a command-line Leave Management System for managing employee leave requests, leave balances, holidays, and approvals. The system supports two types of users: **admins** and **employees**. Admins can add/edit/delete employees, manage holidays, and approve leave requests. Employees can submit leave requests and query their leave balances.

---

## Features

- Add, edit, and delete employees (admin only)
- Manage employee leave balances (Sick, Annual, Maternity leaves)
- Add company holidays
- Employees can submit leave requests and view their status
- Admin approval or denial of leave requests with automatic leave balance adjustment
- User-friendly command-line interface with input validation
- Simple logging of admin actions for audit purposes
- AI-based intent recognition for user leave requests (via `ai.py` module)

---

## Project Structure

```
leave_management/
│
├── main.py              # Entry point of the application
├── admin.py             # Admin-related workflows (add/edit/delete/approve)
├── employee.py          # Employee management & intent handling
├── ai.py                # Intent detection from user input
├── database.py          # JSON-based data storage
├── utils.py             # Utility functions like date validation
├── config.py            # Stores OpenAI API key
├── employees.json       # Persistent database file
└── README.md            # Documentation and usage guide
```

---

## Setup Instructions

- Created in Python 3.10

- I installed the openai library by:

```bash
pip install openai
```

- If `employees.json` does not exist, it will be created automatically on first run.

---

## Running the Application

From the project root folder, run:

```bash
python main.py
```

You will be greeted with:

```
Welcome to the Leave Management System!
Are you an 'admin' or 'user'? (type 'quit' to exit):
```

- Type `admin` or `user` and press Enter.

- **Admin**: Full access to employee management and leave approvals.
- **User**: Limited access to request and view leave

- Enter your name when prompted.

---

## 🛠 Admin Functionalities

- Admins need to be listed in the `"admins"` section of `employees.json` (default: `["AdminUser"]`).

After logging in as an admin, you can perform all management tasks:

1. **Add Employee** – Add a new employee with leave balances and manager status.
2. **Edit Employee** – Modify leave balances or manager status of an existing employee.
3. **Delete Employee** – Remove an employee and all related records.
4. **Add Holiday** – Mark a date as a holiday (skips leave deductions).
5. **Approve Leave Requests** – Review pending leave requests and approve/deny them.
6. **Quit Admin Mode** – Exit admin dashboard.

Logs for admin actions are saved in the JSON file for traceability.

---

## User Functionalities

After logging in as a user (employee):

- Users can type natural language queries like:
  - `"I want to take 2 days of sick leave from 2024-08-10"`
  - `"How many annual leaves do I have left?"`
  - `"Show my leave history"`
- The system interprets queries using `ai.py` and performs actions via `employee.py`.

---

- Type `quit` at any prompt to exit or log out.

---

## API Key Configuration

The system uses OpenAI’s API to process natural language input from employees using GPT-based intent classification.

Set your OpenAI API key in `config.py`:

```python
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## Data Storage

- All data is stored in `employees.json`:
  - Employees and their leave balances
  - Leave request history
  - Admin user list
  - Holiday dates

---

## Assumptions Made

- Employee names are unique identifiers.
- Leave balances are maintained per leave type and are non-negative integers.
- Leave requests can have statuses: Pending, Approved, or Denied or cancelled.
- Holidays are stored as dates in `YYYY-MM-DD` format.
- Admin users are pre-defined in the `"admins"` list within the JSON data file.
- The AI module supports basic intent recognition for user leave requests.
- Data persistence is done through a JSON file (`employees.json`).
- Input validations are performed for dates, numbers, and selections.
- No password authentication implemented for simplicity.
- Leave balances are refunded automatically if a leave request is denied after being deducted.

---

**Thank you for using the Leave Management System!**
