import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path = "bonus_system.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                hire_date TEXT NOT NULL,
                current_department TEXT NOT NULL,
                current_salary REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Salary history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            salary REAL NOT NULL,
            effective_date TEXT NOT NULL,
            end_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
            """)

        # Department history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS department_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            department TEXT NOT NULL,
            effective_date TEXT NOT NULL,
            end_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
            """)

        # KPI definitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            calculation_method TEXT NOT NULL,
            formula TEXT,
            applicable_departments TEXT,
            weight REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
            )
            """)

        # Bonus calculation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bonus_calculations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            calculation_date TEXT NOT NULL,
            period_month INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            base_salary REAL NOT NULL,
            calculated_bonus REAL NOT NULL,
            kpi_details TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
            """)

        conn.commit()
        conn.close()

    def save_employee(self, employee_data):
        """Save employee to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        # Insert or replace employee
        cursor.execute("""
            INSERT OR REPLACE INTO employees
            (id, first_name, last_name, hire_date, current_department, current_salary, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?)
            """, (
            employee_data["id"],
            employee_data["first_name"],
            employee_data["last_name"],
            employee_data["hire_date"],
            employee_data["department"],
            employee_data["salary"],
            employee_data["status"],
            current_time,
            current_time
        ))

        # Save salary history if provided
        if "salary_history" in employee_data:
            for salary_record in employee_data["salary_history"]:
                cursor.execute("""
                INSERT INTO salary_history
                (employee_id, salary, effective_date, end_date)
                VALUES (?,?,?,?)
                """, (
                employee_data["id"],
                salary_record['salary'],
                salary_record["effective_date"],
                salary_record.get("end_date")
                ))

        # Save department history if provided
        if "department_history" in employee_data:
            for dept_record in employee_data["department_history"]:
                cursor.execute("""
                INSERT INTO department_history
                (employee_id, department, effective_date, end_date)
                VALUES (?,?,?,?)
                """, (

                employee_data["id"],
                dept_record['department'],
                dept_record["effective_date"],
                dept_record.get("end_date")
                ))
        conn.commit()
        conn.close()

    def get_all_employees(self):
        """Get all employees from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM employees ORDER BY first_name, last_name")
        employees = cursor.fetchall()

        # Conver to list of dictionaries
        employee_list = []
        for emp in employees:
            employee_list.append({
                "id": emp[0],
                "first_name":emp[1],
                "last_name":emp[2],
                "hire_date":emp[3],
                "department":emp[4],
                "salary":emp[5],
                "status":emp[6]
            })

        conn.close()
        return employee_list

    def delete_employee(self, employee_id):
        """Delete employee from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM employees WHERE id = ?",(employee_id,))
        cursor.execute("DELETE FROM salary_history WHERE employee_id = ?", (employee_id,))
        cursor.execute("DELETE FROM department_history WHERE employee_id = ?", (employee_id,))

        conn.commit()
        conn.close()

    def get_employee_salary_history(self, employee_id):
        """Get salary history for and employee"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT salary, effective_date, end_date
        FROM salary_history
        WHERE employee_id = ?
        ORDER BY effective_date
        """, (employee_id,))

        history = cursor.fetchall()
        conn.close()

        return [{"salary":h[0],"effective_date":h[1],"end_date":h[2]} for h in history]