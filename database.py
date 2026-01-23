import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path = "bonus_system.db"):
        self.db_path = db_path
        self.init_database()
        self.fix_orders_table_constraint()

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
        print(f"DEBUG: After CREATE TABLE - columns: {columns_after_create}")

        # Check if father_name column exists, if not, add it
        if 'father_name' not in columns_after_create:
            print("DEBUG: Adding missing father_name column to employees table")
            try:
                cursor.execute("ALTER TABLE employees ADD COLUMN father_name TEXT DEFAULT ''")
                print("DEBUG: ALTER TABLE executed successfully")
            except Exception as e:
                print(f"DEBUG: Error executing ALTER TABLE: {e}")

        # Check final schema
        cursor.execute("PRAGMA table_info(employees)")
        columns_final = [column[1] for column in cursor.fetchall()]
        print(f"DEBUG: Final columns: {columns_final}")

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
                order_action TEXT NOT NULL, --"employment", "salary change", "department change", 'termination"
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

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

        # DEBUG: Print column mapping for verification
        print(f"DEBUG get_all_employees: Column mapping:")
        for name, idx in col_index.items():
            print(f"  {name}: {idx}")

        # Convert to list of dictionaries
        employee_list = []
        for emp in employees:
            # DEBUG: Print raw data for each employee
            print(f"DEBUG: Raw employee data: {emp}")

            # Get salary value and ensure it's a float
            salary_raw = emp[col_index["current_salary"]]
            print(f"DEBUG: Raw salary value: {salary_raw}, type: {type(salary_raw)}")

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
                print(f"DEBUG: Error converting salary '{salary_raw}' to float: {e}")
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

            # DEBUG: Print processed employee data
            print(
                f"DEBUG: Processed employee: {employee_dict['first_name']} {employee_dict['last_name']}, Salary: {employee_dict['salary']} (type: {type(employee_dict['salary'])})")

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
            print(f"DEBUG: Updating existing KPI with ID: {kpi_data['id']}")
            # UPDATE existing record
            cursor.execute('''
                UPDATE kpis SET 
                name=?, description=?, calculation_method=?, formula=?, 
                applicable_departments=?, weight=?, is_active=?, created_at=?
                WHERE id=?
            ''', (
                kpi_data['name'],
                kpi_data.get('description', ''),
                kpi_data['calculation_method'],
                kpi_data.get('formula', ''),
                json.dumps(kpi_data.get('applicable_departments', [])),
                kpi_data.get('weight', 1.0),
                1 if kpi_data.get('is_active', True) else 0,
                current_time,
                kpi_data['id']  # WHERE condition
            ))
            print(f"DEBUG: Updated {cursor.rowcount} rows")
        else:
            print("DEBUG: Inserting new KPI (no ID)")
            # INSERT new record
            cursor.execute('''
                INSERT INTO kpis 
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
        return True

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
                variable_list.append({
                    "id": var[0],
                    "name": var[1],
                    "display_name": var[2],
                    "data_type": var[3],
                    "default_value": var[4],
                    "description": var[5],
                    "is_active": bool(var[6])
                })


            conn.close()
            print(f"DEBUG  database get_custom_variable line 329: Returning {len(variable_list)} custom variables")
            return variable_list

        except Exception as e:
            print(f"ERROR in get_custom_variables get_custom_variables  line 333: {e}")
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
                print(f"DEBUG: Successfully deleted variable with ID: {variable_id}")
                conn.close()
                return True
            else:
                print(f"DEBUG: No variable found with ID: {variable_id}")
                conn.close()
                return False

        except Exception as e:
            print(f"Error deleting custom variable: {e}")
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

        print("Database schema:")
        for table in tables:
            print(f"\n  {table[0]}:")
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            for col in columns:
                print(f" {col[1]} ({col[2]}")

        conn.close()

    def get_all_orders(self):
        """Get all orders from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM orders ORDER BY order_date")
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
                    "order_date": str(ord[col_index["order_date"]]),
                    "effective_date": str(ord[col_index["effective_date"]]),
                    "order_action": str(ord[col_index["order_action"]]),
                }

                order_list.append(orders_dict)

            return order_list
        except Exception as e:
            print(f"Error in get_all_orders: {e}")
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
                                   FOREIGN KEY (employee_id) REFERENCES employees (id)
                               )
                               ''')

                # Restore data
                if orders_data:
                    placeholders = ','.join(['?' for _ in range(len(columns) + 1)])  # +1 for id
                    for row in orders_data:
                        cursor.execute(f"INSERT INTO orders VALUES ({placeholders})", row)

                conn.commit()
                print("Fixed orders table constraint - removed UNIQUE from order_number")

        except Exception as e:
            print(f"Error fixing orders table: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    database = Database()
    print(database.get_all_employees())
    #database.check_schema()