from datetime import datetime

def create_employee_with_history(employee_data):
    """Create employee record with salary and department history"""
    return {
        **employee_data,
        "salary_history":[
            {
                "salary": employee_data["salary"],
                "effective_date": employee_data.get("hire_date", datetime.now().strftime("%Y-%m-%d")),
                "end_date": None

            }
        ],
        "department_history": [
            {
                "department": employee_data["department"],
                "effective_date": employee_data.get("hire_date", datetime.now().strftime("%Y-%m-%d")),
                "end_date": None
            }
        ],
        "hire_date":employee_data.get("hire_date", datetime.now().strftime("%Y-%m-%d"))
        }

def get_current_salary(employee,target_date = None):
    """Get effective salary for a specific date"""
    if target_date is None:
        target_date = datetime.now()

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    for salary_record in employee.get("salary_history",[]):
        effective_date = datetime.strptime(salary_record["effective_date"], "%Y-%m-%d")
        end_date = salary_record["end_date"]

        if end_date:
            end_date <= datetime.strptime(end_date, "%Y-%m-%d")

        if effective_date <= target_date and (end_date is None or target_date <= end_date):

            return salary_record["salary"]

    return employee.get("salary", 0)

def get_current_department(employee, target_date = None):
    """Get effective department for a specific date"""
    if target_date is None:
        target_date = datetime.now()

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    for dept_record in employee.get("department_history", []):
        effective_date = datetime.strptime(dept_record["effective_date"], "%Y-%m-%d")

        end_date = dept_record["end_date"]

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if effective_date <= target_date and (end_date is None or target_date <= end_date):

            return dept_record["department"]

    return employee.get("department","")