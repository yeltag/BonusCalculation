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

        # Variables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                data_type TEXT NOT NULL, --"number", "text", "percentage", "currency"
                default_value TEXT,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
         ''')

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



    def save_kpi(self, kpi_data):
        """Save KPI to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO kpis 
            (name, description, calculation_method, formula, applicable_departments, weight, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kpi_data['name'],
            kpi_data.get('description', ''),
            kpi_data['calculation_method'],
            kpi_data.get('formula', ''),
            json.dumps(kpi_data.get('applicable_departments', [])),
            kpi_data.get('weight', 1.0),
            1 if kpi_data.get('is_active', True) else 0,
            current_time
        ))

        conn.commit()
        conn.close()

    def get_all_kpis(self):
        """Get all KPIs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM kpis WHERE is_active = 1 ORDER BY name')
        kpis = cursor.fetchall()

        # Convert to list of dictionaries
        kpi_list = []
        for kpi in kpis:
            kpi_list.append({
                'id': kpi[0],
                'name': kpi[1],
                'description': kpi[2],
                'calculation_method': kpi[3],
                'formula': kpi[4],
                'applicable_departments': json.loads(kpi[5]) if kpi[5] else [],
                'weight': kpi[6],
                'is_active': bool(kpi[7])
            })

        conn.close()
        return kpi_list

    def delete_kpi(self, kpi_id):
        """Soft delete KPI (set is_active = 0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE kpis SET is_active = 0 WHERE id = ?', (kpi_id,))
        conn.commit()
        conn.close()

    def save_custom_variable(self, variable_data):
        """Save custom variable to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO custom_variables
            (name, display_name, data_type, default_value, description, is_active, created_at)
            VALUES (?,?,?,?,?,?,?)
            """, (
            variable_data["name"],
            variable_data["display_name"],
            variable_data["data_type"],
            variable_data.get("default_value",""),
            variable_data.get("description",""),
            1 if variable_data.get("is_active", True) else 0,
            current_time
        ))

        conn.commit()
        conn.close()


    def get_custom_variables(self):
        """Get all custom variables from database FIXED VERSION"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()


            # First, check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_variables'")
            table_exists = cursor.fetchone()

            if not table_exists:
                print("DEBUG: custom_variables table does not exist, ctreating it...")
                self.init_database() # Re-initialize to create missing table
                return [] # Return empty list since we just created the table

            cursor.execute('SELECT * FROM custom_variables WHERE is_active = 1 ORDER BY display_name')
            variables = cursor.fetchall()

            # Convert to list of dictionaries
            variable_list = []
            for var in variables:
                variable_list = []
                for var in variables:
                    variable_list.append({
                        "id": var[0],
                        "name": var[1],
                        "display_name": var[2],
                        "data_type": var[3],
                        "description": var[5],
                        "is_active": bool(var[6])
                    })


            conn.close()
            print(f"DEBUG: Returning {len(variable_list)} custom variables")
            return variable_list

        except Exception as e:
            print(f"ERROR in get_all_custom_variables: {e}")
            return []  # Return empty list instead of None