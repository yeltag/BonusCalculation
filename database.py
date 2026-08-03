import sqlite3
from datetime import datetime
import json
from PyQt6.QtCore import Qt

class Database:
    def __init__(self, db_path = "bonus_system.db",username = None):
        self.db_path = db_path
        self.username = username
        self.init_database()
        #self.fix_orders_table_constraint()


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
                father_name TEXT DEFAULT '',
                hire_date TEXT NOT NULL,
                current_department TEXT NOT NULL,
                current_salary REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Check if father_name column exists, if not, add it
        cursor.execute("PRAGMA table_info(employees)")
        columns_after_create = [column[1] for column in cursor.fetchall()]


        # Check if father_name column exists, if not, add it
        if 'father_name' not in columns_after_create:

            try:
                cursor.execute("ALTER TABLE employees ADD COLUMN father_name TEXT DEFAULT ''")

            except Exception as e:
                print(f"DEBUG: Error executing ALTER TABLE: {e}")

        # Check final schema
        cursor.execute("PRAGMA table_info(employees)")
        columns_final = [column[1] for column in cursor.fetchall()]


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
            applicable_employees TEXT,    
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            effective_date TEXT DEFAULT CURRENT_DATE,
            weight REAL NOT NULL,
            created_by TEXT NOT NULL    
            )
            """)

        # KPI to Department mapping with start date

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_id INTEGER NOT NULL,
            department_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,    
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            apply_to_all INTEGER,
            check_state TEXT,
            enddate_combobox TEXT,
            enddate_check INTEGER,
            created_by TEXT NOT NULL,
            version INTEGER NOT NULL,    
            FOREIGN KEY (kpi_id) REFERENCES kpis(id) ON DELETE CASCADE
            
            )
        """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS new_kpi_departments (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           kpi_id INTEGER NOT NULL,
                           department_name TEXT NOT NULL,
                           start_date TEXT NOT NULL,
                           end_date TEXT,
                           created_at TEXT NOT NULL,
                           updated_at TEXT NOT NULL,
                           apply_to_all INTEGER,
                           check_state TEXT,
                           enddate_combobox TEXT,
                           enddate_check INTEGER,
                           created_by TEXT NOT NULL,
                           version INTEGER NOT NULL,
                           FOREIGN KEY (kpi_id) REFERENCES kpis (id) ON DELETE CASCADE

                           )
                       """)

        # KPI to Employee mapping with start date

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id INTEGER NOT NULL,
                employee_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                kpi_name TEXT NOT NULL,
                combo_text TEXT,
                FOREIGN KEY (kpi_id) REFERENCES kpis(id) ON DELETE CASCADE,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                UNIQUE(kpi_id, employee_id, start_date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS new_kpi_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id INTEGER NOT NULL,
                kpi_name TEXT NOT NULL,
                employee_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                combo_text TEXT NOT NULL,
                created_by TEXT NOT NULL,
                version INTEGER NOT NULL,
                FOREIGN KEY (kpi_id) REFERENCES kpis (id) ON DELETE CASCADE,
                FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
            )
        """)

        # Department-Employee exceptions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_excluded_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kpi_id INTEGER NOT NULL,
                employee_id TEXT NOT NULL,
                excluded_from_date TEXT NOT NULL,
                excluded_until_date TEXT,
                reason TEXT,
                order_number TEXT NOT NULL,
                order_id TEXT NOT NULL,
                FOREIGN KEY (kpi_id) REFERENCES kpis(id) ON DELETE CASCADE,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                UNIQUE(kpi_id, employee_id, excluded_from_date)
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
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL
            )
         ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_variable_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                variable_name TEXT NOT NULL,
                period_year INTEGER NOT NULL,
                period_month INTEGER NOT NULL,
                value REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(employee_id, variable_name, period_year, period_month),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                employee_id TEXT NOT NULL,
                order_date TEXT NOT NULL,
                effective_date TEXT NOT NULL,
                order_action TEXT NOT NULL, --"employment", "salary change", "department change", 'termination", "exclusion_from_kpi", "new kpi applicability"
                new_department TEXT,
                new_salary TEXT,
                new_applicability TEXT
                
                
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS new_orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                employee_id TEXT DEFAULT NULL,
                department TEXT,
                order_date TEXT NOT NULL,
                effective_date TEXT NOT NULL,
                order_action TEXT NOT NULL, --"employment", "salary change", "department change", "termination", "exclusion_from_kpi", "new kpi applicability"
                new_department TEXT,
                new_salary TEXT,
                new_applicability TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE SET NULL
            )
        ''')

        # FOREIGN KEY (employee_id) REFERENCES employees (id)

        # Create indexes for better performance
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_departments_kpi_id'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_departments_kpi_id ON kpi_departments(kpi_id)")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_departments_dates'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_departments_dates ON kpi_departments(start_date, end_date)")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_employees_kpi_id'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_employees_kpi_id ON kpi_employees(kpi_id)")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_employees_employee_id'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_employees_employee_id ON kpi_employees(employee_id)")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_employees_dates'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_employees_dates ON kpi_employees(start_date, end_date)")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_excluded_employees_kpi_id'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_excluded_employees_kpi_id ON kpi_excluded_employees(kpi_id)")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_kpi_excluded_employees_employee_id'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_kpi_excluded_employees_employee_id ON kpi_excluded_employees(employee_id)")


        conn.commit()
        conn.close()

    def save_employee(self, employee_data):
        """Save employee to database - handles both old and new schemas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        # First check if employee exists and is active
        cursor.execute("SELECT id, status FROM employees WHERE id = ?", (employee_data["id"],))
        existing_employee = cursor.fetchone()

        # If employee exists and is active, we should not overwrite
        # if existing_employee and existing_employee[1].lower() == "active":
        #     conn.close()
        #     raise ValueError(f"Active employee with ID '{employee_data['id']}' already exists")

        # Check if father_name column exists
        cursor.execute("PRAGMA table_info(employees)")
        columns = [column[1] for column in cursor.fetchall()]
        has_father_name = 'father_name' in columns

        if has_father_name:
            # New schema with father_name
            cursor.execute("""
                INSERT OR REPLACE INTO employees
                (id, first_name, last_name, father_name, hire_date, current_department, current_salary, status, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                employee_data["id"],
                employee_data["first_name"],
                employee_data["last_name"],
                employee_data.get("father_name", ""),
                employee_data["hire_date"],
                employee_data["department"],
                float(employee_data["salary"]),  # Ensure it's float
                employee_data["status"],
                current_time,
                current_time
            ))
        else:
            # Old schema without father_name
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
                float(employee_data["salary"]),  # Ensure it's float
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
                               VALUES (?, ?, ?, ?)
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
                               VALUES (?, ?, ?, ?)
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

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Create column index mapping
        col_index = {name: idx for idx, name in enumerate(column_names)}



        # Convert to list of dictionaries
        employee_list = []
        for emp in employees:


            # Get salary value and ensure it's a float
            salary_raw = emp[col_index["current_salary"]]


            try:
                # Try to convert salary to float
                if salary_raw is None:
                    salary = 0.0
                elif isinstance(salary_raw, (int, float)):
                    salary = float(salary_raw)
                elif isinstance(salary_raw, str):
                    # Remove any currency symbols or commas
                    salary_str = salary_raw.replace('$', '').replace(',', '').strip()
                    salary = float(salary_str) if salary_str else 0.0
                else:
                    salary = 0.0
            except (ValueError, TypeError) as e:

                salary = 0.0

            # Create employee dictionary
            employee_dict = {
                "id": str(emp[col_index["id"]]),
                "first_name": str(emp[col_index["first_name"]]),
                "last_name": str(emp[col_index["last_name"]]),
                "father_name": str(emp[col_index.get("father_name", -1)]) if "father_name" in col_index else "",
                "hire_date": str(emp[col_index["hire_date"]]),
                "department": str(emp[col_index["current_department"]]),
                "salary": salary,  # This is now a float
                "status": str(emp[col_index["status"]])
            }



            employee_list.append(employee_dict)

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
        """Get salary history for an employee"""
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

        return [{"salary": h[0], "effective_date": h[1], "end_date": h[2]} for h in history]

    def save_kpi(self, kpi_data):
        """Save KPI to database - properly handles updates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        # Check if this is an update (has ID) or insert (no ID)
        if 'id' in kpi_data and kpi_data['id'] is not None:

            # UPDATE existing record
            cursor.execute('''
                UPDATE kpis SET 
                name=?, description=?, calculation_method=?, formula=?, 
                applicable_departments=?, applicable_employees=?,weight=?, is_active=?, effective_date=?
                WHERE id=?
            ''', (
                kpi_data['name'],
                kpi_data.get('description', ''),
                kpi_data['calculation_method'],
                kpi_data.get('formula', ''),
                json.dumps(kpi_data.get('applicable_departments', [])),
                json.dumps(kpi_data.get('applicable_employees', [])),
                kpi_data.get('weight', 1.0),
                1 if kpi_data.get('is_active', True) else 0,
                kpi_data.get('effective_date', datetime.now().strftime('%Y-%m-%d')),
                kpi_data['id']  # WHERE condition
            ))

        else:

            # INSERT new record
            cursor.execute('''
                INSERT INTO kpis 
                (name, description, calculation_method, formula, applicable_departments, applicable_employees, weight, is_active, created_at, effective_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?)
            ''', (
                kpi_data['name'],
                kpi_data.get('description', ''),
                kpi_data['calculation_method'],
                kpi_data.get('formula', ''),
                json.dumps(kpi_data.get('applicable_departments', [])),
                json.dumps(kpi_data.get('applicable_employees', [])),
                kpi_data.get('weight', 1.0),
                1 if kpi_data.get('is_active', True) else 0,
                current_time,
                kpi_data.get('effective_date',datetime.now().strftime('%Y-%m-%d'))
            ))

        conn.commit()
        conn.close()
        return True

    def get_all_kpis(self):
        """Get all KPIs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM kpis WHERE is_active = 1 ORDER BY name')
        kpis = cursor.fetchall()
        print("kpis: ",kpis)

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
                'applicable_employees':json.loads(kpi[6]) if kpi[6] else [],

                'is_active': bool(kpi[7]),
                'created_at': kpi[8],
                'effective_date': kpi[9] if len(kpi) > 9 else None,
                'weight': kpi[10],
                'created_by': kpi[11]
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
            (name, display_name, data_type, default_value, description, is_active, created_at,created_by)
            VALUES (?,?,?,?,?,?,?,?)
            """, (
            variable_data["name"],
            variable_data["display_name"],
            variable_data["data_type"],
            variable_data.get("default_value",""),
            variable_data.get("description",""),
            1 if variable_data.get("is_active", True) else 0,
            current_time,
            variable_data.get("created_by","")
        ))

        conn.commit()
        conn.close()

    def get_custom_variables(self):
        """Get all custom variables from database FIXED VERSION"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()


            # First, check if table exists
            # cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_variables'")
            # table_exists = cursor.fetchone()
            #
            # if not table_exists:
            #
            #     self.init_database() # Re-initialize to create missing table
            #     return [] # Return empty list since we just created the table

            cursor.execute('SELECT * FROM custom_variables WHERE is_active = 1 ORDER BY display_name')
            variables = cursor.fetchall()

            # Convert to list of dictionaries
            variable_list = []
            for var in variables:
                variable_list.append({
                    "id": var[0],
                    "name": var[1],
                    "display_name": var[2],
                    "data_type": var[3],
                    "default_value": var[4],
                    "description": var[5],
                    "is_active": bool(var[6]),
                    "created_at": var[7],
                    "created_by": var[8]

                })


            conn.close()

            return variable_list

        except Exception as e:

            return []  # Return empty list instead of None

    def delete_custom_variable(self,variable_id):
        """Delete a custom variable by ID - FIXED VERSION"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM custom_variables WHERE id = ?", (variable_id,))
            conn.commit()

            # Check if any row was actually deleted
            if cursor.rowcount > 0:

                conn.close()
                return True
            else:

                conn.close()
                return False

        except Exception as e:

            return False

    def save_employee_variable_value(self, value_data):
        """Save employee variable value for a specific period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO employee_variable_values
            (employee_id, variable_name, period_year, period_month, value, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            value_data["employee_id"],
            value_data["variable_name"],
            value_data["period_year"],
            value_data["period_month"],
            value_data["value"],
            current_time,
            current_time
        ))

        conn.commit()
        conn.close()
        return True

    def get_employee_variable_values(self, employee_id, period_year, period_month):
        """Get variable values for an employee in a specific period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT variable_name, value 
            FROM employee_variable_values 
            WHERE employee_id = ? AND period_year = ? AND period_month = ?
        """, (employee_id, period_year, period_month))

        values = cursor.fetchall()
        conn.close()

        return {row[0]: row[1] for row in values}

    def get_employee_variable_value(self, employee_id, variable_name, period_year, period_month):
        """Get specific variable value for an employee in a period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value 
            FROM employee_variable_values 
            WHERE employee_id = ? AND variable_name = ? AND period_year = ? AND period_month = ?
        """, (employee_id, variable_name, period_year, period_month))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def get_employee_salary_on_date(self, employee_id, target_date):
        """Get employee's salary on a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert target_date to string if it's a datetime object
        if isinstance(target_date, datetime):
            target_date = target_date.strftime("%Y-%m-%d")

        cursor.execute("""
        SELECT salary 
        FROM salary_history
        WHERE employee_id = ? 
        AND effective_date <= ?
        AND (end_date IS NULL OR end_date >= ?)
        ORDER BY effective_date DESC
        LIMIT 1
        """, (employee_id, target_date, target_date))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        # Fallback to current salary
        cursor.execute("SELECT current_salary FROM employees WHERE id = ?", (employee_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_employee_by_id(self, employee_id):
        """Get a specific employee by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        emp = cursor.fetchone()

        if not emp:
            conn.close()
            return None

        # Get column names
        column_names = [description[0] for description in cursor.description]
        col_index = {name: idx for idx, name in enumerate(column_names)}

        employee = {
            "id": emp[col_index["id"]],
            "first_name": emp[col_index["first_name"]],
            "last_name": emp[col_index["last_name"]],
            "father_name": emp[col_index.get("father_name", -1)] if "father_name" in col_index else "",
            "hire_date": emp[col_index["hire_date"]],
            "department": emp[col_index["current_department"]],
            "salary": float(emp[col_index["current_salary"]]),
            "status": emp[col_index["status"]]
        }

        # Rest of the method remains the same...
        # Get salary history
        cursor.execute("""
                       SELECT salary, effective_date, end_date
                       FROM salary_history
                       WHERE employee_id = ?
                       ORDER BY effective_date
                       """, (employee_id,))

        salary_history = []
        for salary_record in cursor.fetchall():
            salary_history.append({
                "salary": salary_record[0],
                "effective_date": salary_record[1],
                "end_date": salary_record[2]
            })

        employee["salary_history"] = salary_history

        # Get department history
        cursor.execute("""
                       SELECT department, effective_date, end_date
                       FROM department_history
                       WHERE employee_id = ?
                       ORDER BY effective_date
                       """, (employee_id,))

        department_history = []
        for dept_record in cursor.fetchall():
            department_history.append({
                "department": dept_record[0],
                "effective_date": dept_record[1],
                "end_date": dept_record[2]
            })

        employee["department_history"] = department_history

        conn.close()
        return employee

    def update_employee_father_name(self, employee_id, father_name):
        """Update only the father's name for an employee"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now().isoformat()

        cursor.execute("""
                       UPDATE employees
                       SET father_name = ?,
                           updated_at  = ?
                       WHERE id = ?
                       """, (father_name, current_time, employee_id))

        conn.commit()
        conn.close()
        return True

    def check_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()


        for table in tables:

            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()


        conn.close()

    def get_all_orders(self):
        """Get all orders from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM new_orders ORDER BY order_date")
            orders = cursor.fetchall()

            # Set column names
            column_names = [description[0] for description in cursor.description]

            # Create column index mapping
            col_index = {name: idx for idx, name in enumerate(column_names)}

            # Convert to list of dictionaries
            order_list = []

            for ord in orders:
                # Create orders dictionary
                orders_dict = {
                    "id": str(ord[col_index["id"]]),
                    "order_number": str(ord[col_index["order_number"]]),
                    "employee_id": str(ord[col_index["employee_id"]]),
                    "department":str(ord[col_index["department"]]),
                    "order_date": str(ord[col_index["order_date"]]),
                    "effective_date": str(ord[col_index["effective_date"]]),
                    "order_action": str(ord[col_index["order_action"]]),
                    "new_department": str(ord[col_index["new_department"]]),
                    "new_salary":str(ord[col_index["new_salary"]]),
                    "new_applicability":str(ord[col_index["new_applicability"]])
                }

                order_list.append(orders_dict)

            return order_list
        except Exception as e:

            return []
        finally:
            conn.close()

    def fix_orders_table_constraint(self):
        """Remove UNIQUE constraint from order_number if it exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if cursor.fetchone():
                # Backup the data
                cursor.execute("SELECT * FROM orders")
                orders_data = cursor.fetchall()

                # Get column names (excluding the id for autoincrement)
                cursor.execute("PRAGMA table_info(orders)")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info if col[1] != 'id']

                # Drop the old table
                cursor.execute("DROP TABLE orders")

                # Recreate table without UNIQUE constraint
                cursor.execute('''
                               CREATE TABLE orders
                               (
                                   id             INTEGER PRIMARY KEY AUTOINCREMENT,
                                   order_number   TEXT NOT NULL,
                                   employee_id    TEXT NOT NULL,
                                   order_date     TEXT NOT NULL,
                                   effective_date TEXT NOT NULL,
                                   order_action   TEXT NOT NULL,
                                   new_department TEXT,
                                   new_salary TEXT,
                                   FOREIGN KEY (employee_id) REFERENCES employees (id)
                               )
                               ''')

                # Restore data
                if orders_data:
                    placeholders = ','.join(['?' for _ in range(len(columns) + 1)])  # +1 for id
                    for row in orders_data:
                        cursor.execute(f"INSERT INTO orders VALUES ({placeholders})", row)

                conn.commit()


        except Exception as e:

            conn.rollback()
        finally:
            conn.close()

    def add_kpi_department(self, kpi_id, department_name, start_date, end_date = None, apply_to_all = Qt.CheckState.Unchecked, check_state = Qt.CheckState.Unchecked, enddate_combobox = "Open date", enddate_check = 0, created_by = None, version = 1):
        """Add a department to a KPI with start date"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()

        check_state_value = check_state

        version = version + 1

        if created_by is None:
            created_by = self.username

        try:
            cursor.execute("""
               INSERT INTO new_kpi_departments (kpi_id, department_name, start_date, end_date, created_at, updated_at,apply_to_all,check_state,enddate_combobox, enddate_check, created_by, version)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (kpi_id, department_name, start_date, end_date, current_time, current_time,apply_to_all,check_state, enddate_combobox, enddate_check, created_by, version))
            conn.commit()
            return True
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_kpi_department(self, kpi_id, department_name):
        """ Remove a department from a KPI (set end_date to today)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            cursor.execute("""
               UPDATE kpi_departments
               SET end_date = ?, updated_at = ?
               WHERE kpi_id = ? AND department_name = ? AND end_date IS NULL""", (today, current_time, kpi_id, department_name))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def get_kpi_departments(self, kpi_id, as_of_date = None):
        """Get all departments for a KPI, optionally as of a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        self.kpi_id = kpi_id
        self.as_of_date = as_of_date


        #if as_of_date is None:
            #as_of_date = datetime.now().strftime("%Y-%m-%d")

        try:
            if as_of_date != None:
                cursor.execute("""
                           SELECT * 
                           FROM new_kpi_departments 
                           WHERE kpi_id = ? 
                           AND start_date <=? 
                           AND (end_date IS NULL OR end_date >=?)
                        """, (kpi_id,as_of_date,as_of_date))
            else:
                cursor.execute("""
                            SELECT *
                            FROM new_kpi_departments
                            WHERE kpi_id = ?
                        """, (kpi_id,))


            departments = cursor.fetchall()
            dep_vers = [departments[0][2],departments[0][12]]
            last_version = max(d[12] for d in departments)
            print(last_version)
            selected_departments = []
            for d in departments:
                if d[12] == last_version:
                    selected_departments.append(d)

                    print (d)
                    print({"id":d[0],"kpi_id":d[1],"department_name": d[2], "start_date": d[3], "end_date": d[4],"created_at":d[5],"updated_at":d[6], "apply_to_all": d[7],
                     "check_state": d[8], "enddate_combobox": d[9], "enddate_check": d[10],"created_by":d[11],"version":d[12]})
            return [{"id":d[0],"kpi_id":d[1],"department_name": d[2], "start_date": d[3], "end_date": d[4],"created_at":d[5],"updated_at":d[6], "apply_to_all": d[7],
                     "check_state": d[8], "enddate_combobox": d[9], "enddate_check": d[10],"created_by":d[11],"version":d[12]} for d in selected_departments]
        except Exception as e:

            return[]
        finally:
            conn.close()

    def add_kpi_employee(self, kpi_id, kpi_name, employee_id, start_date, end_date = "1900-01-01", combo_text = "Open date", created_by = None, version = 1):
        """Add a specific employee to a KPI with start date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        version = version + 1

        if created_by is None:
            created_by = self.username

        try:
            cursor.execute("""
                INSERT INTO new_kpi_employees (kpi_id, kpi_name, employee_id, start_date, end_date, created_at, updated_at,combo_text,created_by, version)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (kpi_id, kpi_name, employee_id, start_date, end_date, current_time, current_time,combo_text, created_by, version))
            conn.commit()
            return True
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_kpi_employee(self,kpi_id,employee_id):
        """Remove a specific employee from a KPI (set end_date to today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            cursor.execute("""
                UPDATE kpi_employees
                SET end_date = ?, updated_at = ?
                WHERE kpi_id = ? AND employee_id = ? AND end_date IS NULL
            """, (today, current_time, kpi_id, employee_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def get_kpi_employees(self,kpi_id, as_of_date = None):
        """Get all specific employees for a KPI, optionally as of a specific date"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SELECT ke.employee_id, ke.start_date, ke.end_date, e.first_name, e.last_name

        try:
            if as_of_date != None:
                cursor.execute("""
                
                SELECT ke.*, e.first_name, e.last_name
                FROM new_kpi_employees ke
                JOIN employees e ON ke.employee_id = e.id
                WHERE ke.kpi_id = ?
                    AND ke.start_date <= ?
                    AND (ke.end_date IS NULL OR ke.end_date >= ?)
                ORDER BY e.last_name, e.first_name
                """, (kpi_id, as_of_date, as_of_date))
            else:
                cursor.execute("""
                SELECT * FROM new_kpi_employees ke
                WHERE ke.kpi_id = ?
                """, (kpi_id,))

            employees = cursor.fetchall()
            print("employees: ", employees)
            last_version = max(e[10] for e in employees)
            selected_employees = []
            for e in employees:
                if e[10] == last_version:
                    selected_employees.append(e)

            for e in selected_employees:
                print({
                "kpi_id": e[1],
                "kpi_name": e[2],
                "employee_id": e[3],
                "start_date": e[4],
                "end_date": e[5],
                #"first_name":e[3],
                #"last_name":e[4],
                "check_state": 2,
                "combo_text":e[8],
                'created_by':e[9],
                'version':e[10]

            })

            return [{
                'id':e[0],
                'kpi_id':e[1],
                "kpi_name": e[2],
                "employee_id": e[3],
                "start_date": e[4],
                "end_date": e[5],
                #"first_name":e[3],
                #"last_name":e[4],
                "check_state": 2,
                "combo_text":e[8],
                'created_by':e[9],
                'version':e[10]
            } for e in selected_employees]
        except Exception as e:

            return[]
        finally:
            conn.close()

    def get_kpi_list_for_employee(self,employee_id,as_of_date = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if as_of_date != None:
                cursor.execute("""
                SELECT * FROM new_kpi_employees ke
                JOIN employees e ON ke.employee_id = e.id 
                WHERE ke.employee_id = ?
                      AND ke.start_date <= ?
                      AND (ke.end_date IS NULL OR ke.end_date >= ?)
                """, (employee_id,as_of_date,as_of_date))
            else:
                cursor.execute("""
                SELECT * FROM new_kpi_employees ke
                WHERE ke.employee_id = ?
                """, (employee_id,))

            kpis = cursor.fetchall()
            last_version = max(e[10] for e in kpis)
            selected_kpis = []
            for e in kpis:
                if e[10] == last_version:
                    selected_kpis.append(e)
            return [{"id": kpi[1], "kpi": kpi[2], "employee": kpi[3], "department":kpi[16]} for kpi in selected_kpis]
        except Exception as e:

            return []
        finally:
            conn.close()

    def exclude_employee_from_kpi(self, kpi_id, employee_id, excluded_from_date, order_number, order_id, excluded_until_date = None, reason=""):
        """Exclude an employee from a KPI for a period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO kpi_excluded_employees
                (kpi_id, employee_id, excluded_from_date, excluded_until_date, order_number, order_id)
                VALUES (?,?,?,?,?,?)
                """, (kpi_id, employee_id, excluded_from_date, excluded_until_date, order_number,order_id))
            conn.commit()
            return True
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_excluded_employee(self, kpi_id,employee_id):
        """Remove an employee from exclusion list"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
               DELETE FROM kpi_excluded_employees
               WHERE kpi_id = ? AND employee_id = ?
            """, (kpi_id, employee_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def get_excluded_employees(self, kpi_id, as_of_date = None):
        """Get all excluded employees for a KPI, optionally as of a specific date"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if as_of_date is None:
            as_of_date = datetime.now().strftime("%Y-%m-%d")

        try:
            cursor.execute("""
                SELECT kee.employee_id,kee.excluded_from_date, kee.excluded_until_date, kee.reason,
                    e.first_name, e.last_name
                FROM kpi_excluded_employees kee 
                JOIN employees e ON kee.employee_id = e.id
                WHERE kee.kpi_id = ?
                    AND kee.excluded_from_date <=?
                    AND (kee.excluded_until_date IS NULL OR kee.excluded_until_date >= ?)
                ORDER BY e.last_name, e.first_name
            """, (kpi_id, as_of_date, as_of_date))

            excluded = cursor.fetchall()
            return [{
                "employee_id": e[0],
                "excluded_from_date": e[1],
                "excluded_until_date": e[2],
                "reason": e[3],
                "first_name": e[4],
                "last_name": e[5]
            } for e in excluded]
        except Exception as e:

            return []
        finally:
            conn.close()

    def get_eligible_employees_for_kpi(self, kpi_id, calculation_date):
        """Get all employees eligible for a KPI on a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Step 1: Get eligible departments for this KPI on the calculation date

            cursor.execute("""
                SELECT department_name
                FROM kpi_departments
                WHERE kpi_id = ?
                    AND start_date <= ?
                    AND (end_date IS NULL OR end_date >= ?)
            """, (kpi_id, calculation_date, calculation_date))

            eligible_depts = [row[0] for row in cursor.fetchall()]

            eligible_employees = set()

            # Step 2:  Get employees in those departments
            if eligible_depts:
                placeholders = ','.join(['?' for _ in eligible_depts])
                cursor.execute(f"""
                    SELECT id FROM employees
                    WHERE current_department IN ({placeholders})
                    AND status = "active"
                """, eligible_depts)
                eligible_employees.update([row[0] for row in cursor.fetchall()])

            # Step 3: Add specific employees (overrides)
            cursor.execute("""
                SELECT employee_id FROM kpi_employees
                WHERE kpi_id = ?
                    AND start_date <= ?
                    AND (end_date IS NULL OR end_date >= ?)
            """, (kpi_id, calculation_date, calculation_date))

            eligible_employees.update([row[0] for row in cursor.fetchall()])

            # Step 4: Remove excluded employees
            if eligible_employees:
                placeholders = ','.join(['?' for _ in eligible_employees])
                cursor.execute(f"""
                    SELECT employee_id FROM kpi_excluded_employees
                    WHERE kpi_id = ?
                        AND employee_id IN ({placeholders})
                        AND excluded_from_date <= ?
                        AND (excluded_until_date IS NULL OR excluded_until_date >= ?)
                """, (kpi_id, *eligible_employees, calculation_date, calculation_date))

                excluded_employees = set([row[0] for row in cursor.fetchall()])

                eligible_employees -=excluded_employees

            # Get full employee details
            if eligible_employees:
                placeholders = ",".join(['?' for _ in eligible_employees])
                cursor.execute(f"""
                    SELECT id, first_name, last_name, current_department, current_salary
                    FROM employees
                    WHERE id IN ({placeholders})
                    AND status = 'active'
                    ORDER BY last_name, first_name
                """, list(eligible_employees))

                employees = cursor.fetchall()
                return [{
                    "id": e[0],
                    "first_name": e[1],
                    "last_name": e[2],
                    "department": e[3],
                    "salary": e[4]
                } for e in employees]

            return[]

        except Exception as e:

            return[]
        finally:
            conn.close()

    def clear_kpi_applicability(self,kpi_id):
        """Clear all applicability settings for a KPI (departments, employees, exclusions)"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM kpi_departments WHERE kpi_id = ?", (kpi_id,))
            cursor.execute("DELETE FROM kpi_employees WHERE kpi_id = ?", (kpi_id,))
            cursor.execute("DELETE FROM kpi_excluded_employees WHERE kpi_id = ?", (kpi_id,))
            conn.commit()
            return True
        except Exception as e:

            conn.rollback()
            return False
        finally:
            conn.close()

    def save_kpi_with_applicability(self,kpi_data,departments=None,employees=None,excluded_employees=None,new_order = False, username = None):
        """Save KPI with its applicability settings"""
        # First save the KPI
        #if not self.save_kpi(kpi_data):
         #   return False
        self.departments = departments
        self.username = username

        # Get the KPI ID (either from data or retreive it)
        kpi_id = kpi_data.get('id')
        if kpi_id:
            existing_kpi = self.get_kpi_by_id(kpi_id)
            if existing_kpi:

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE kpis SET
                    name=?, description=?, calculation_method=?, formula=?, applicable_departments=?, applicable_employees=?, is_active = ?, effective_date = ?,weight=?, created_by=?
                    WHERE id = ?
                
                ''', (
                    kpi_data['name'],
                    kpi_data.get('description',''),
                    kpi_data['calculation_method'],
                    kpi_data.get('formula',''),
                    json.dumps(kpi_data.get('applicable_departments',[])),
                    json.dumps(kpi_data.get('applicable_employees',[])),
                    1 if kpi_data.get('is_active', True) else 0,
                    kpi_data.get('effective_date', datetime.now().strftime('%Y-%m-%d')),
                    kpi_data.get('weight',1.0),
                    kpi_data.get('created_by'),
                    kpi_data['id']
                ))



                conn.commit()
                conn.close()



            #else:

                #print(f"DEBUG: KPI ID {kpi_id} not found, will insert as new")
                #kpi_id = None

        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            current_time = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO kpis
                (name, description, calculation_method, formula,
                applicable_departments, applicable_employees, is_active, created_at, effective_date, weight, created_by)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ''',(
                kpi_data['name'],
                kpi_data.get('description',''),
                kpi_data['calculation_method'],
                kpi_data.get('formula',''),
                json.dumps(kpi_data.get('applicable_departments',[])),
                json.dumps(kpi_data.get('applicable_employees',[])),
                1 if kpi_data.get('is_active', True) else 0,
                kpi_data.get('weight',1.0),
                current_time,
                kpi_data.get('effective_date', datetime.now().strftime('%Y-%m-%d')),
                kpi_data.get('created_by')


            ))



            kpi_id = cursor.lastrowid

            conn.commit()
            conn.close()

            kpi_data['id']=kpi_id



        # Clear existing applicability
        #self.clear_kpi_applicability(kpi_id)

        # Add departments
        if new_order:

            if departments:
                for dept in departments:
                    dept_name = dept.get('department_name')
                    start_date = dept.get('start_date')
                    apply_to_all = dept.get('apply_to_all')
                    check_state = dept.get('check_state')
                    version = dept.get('version')
                    enddate_combobox = dept.get('enddate_combobox')
                    enddate_check = dept.get('enddate_check')
                    end_date = dept.get('end_date')


                    if dept_name and start_date:

                        self.add_kpi_department(
                            kpi_id,
                            dept_name,
                            start_date,
                            dept.get('end_date'),
                            apply_to_all,
                            check_state,
                            enddate_combobox,
                            enddate_check,
                            self.username,
                            version
                    )

        # Add specific employees
            if employees:
                for emp in employees:
                    employee_id = emp.get('employee_id')
                    start_date = emp.get('start_date')
                    kpi_name = kpi_data.get('name')
                    if employee_id and start_date:
                        self.add_kpi_employee(
                            kpi_id,
                            kpi_name,
                            employee_id,
                            start_date,
                            emp.get('end_date'),
                            emp.get('combo_text'),
                            emp.get('created_by'),
                            emp.get('version')
                        )

        # Add excluded employees
        if excluded_employees:
            for excluded in excluded_employees:
                emp_id = excluded.get('employee_id')
                excluded_from = excluded.get('excluded_from_date')
                if emp_id and excluded_from:
                    self.exclude_employee_from_kpi(
                        kpi_id,
                        emp_id,
                        excluded_from,
                        excluded.get('excluded_until_date'),
                        excluded.get('reason',"")
                )

        return True

    def get_kpi_with_applicability(self,kpi_id,as_of_date=None):
        """Get KPI with all its applicability settings"""
        kpi=self.get_kpi_by_id(kpi_id)
        if not kpi:
            return None

        kpi['departments'] = self.get_kpi_departments(kpi_id, as_of_date)
        kpi['employees'] = self.get_kpi_employees(kpi_id, as_of_date)
        kpi['excluded_employees'] = self.get_excluded_employees(kpi_id, as_of_date)

        return kpi

    def get_kpi_by_id(self,kpi_id):
        """Get a specific KPI by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM kpis WHERE id = ?', (kpi_id,))
            kpi = cursor.fetchone()

            if not kpi:
                return None

            return {
                'id': kpi[0],
                'name': kpi[1],
                'description': kpi[2],
                'calculation_method': kpi[3],
                'formula': kpi[4],
                'applicable_departments': json.loads(kpi[5]) if kpi[5] else [],
                'applicable_employees': json.loads(kpi[6]) if kpi[6] else [],
                'weight': kpi[7],
                'is_active': bool(kpi[8]),
                'created_at': kpi[9],
                'effective_date': kpi[10] if len(kpi) > 10 else None
            }

        except Exception as e:

            return None
        finally:
            conn.close()

    def save_order_record(self, order_number, employee_id, department, order_date, effective_date, order_action, new_department,
                          new_salary,new_applicability):
        """Save order to the orders table"""
        conn = None
        try:
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO new_orders (order_number, employee_id, department, order_date, effective_date, order_action,
                                               new_department, new_salary,new_applicability)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (order_number, employee_id, department, order_date, effective_date, order_action, new_department,
                                 new_salary, new_applicability))

            order_id = cursor.lastrowid
            conn.commit()
            self.order_id = order_id
            print(f"DEBUG: Order saved - Number: {order_number}, Employee: {employee_id}, Action: {order_action}")
            return True
        except Exception as e:
            print(f"Error saving order: {e}")
            return False
        finally:
            if conn:
                conn.close()




if __name__ == "__main__":
    database = Database()
