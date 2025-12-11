from datetime import datetime, timedelta


def create_employee_with_history(employee_data):
    """Create employee record with salary and department history"""
    return {
        **employee_data,
        "father_name": employee_data.get("father_name", ""),  # NEW FIELD - ensure it exists
        "salary_history": [
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
        "hire_date": employee_data.get("hire_date", datetime.now().strftime("%Y-%m-%d"))
    }


def get_current_salary(employee, target_date=None):
    """Get effective salary for a specific date"""
    if target_date is None:
        target_date = datetime.now()

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")

    # Sort salary history by effective date
    salary_history = sorted(employee.get("salary_history", []),
                            key=lambda x: datetime.strptime(x["effective_date"], "%Y-%m-%d"))

    for salary_record in salary_history:
        effective_date = datetime.strptime(salary_record["effective_date"], "%Y-%m-%d")
        end_date = salary_record["end_date"]

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_date = datetime.now() + timedelta(days=365 * 10)  # Far future

        if effective_date <= target_date <= end_date:
            return salary_record["salary"]

    return employee.get("salary", 0)


def get_salary_on_date(employee, target_date):
    """Get salary effective on a specific date"""
    return get_current_salary(employee, target_date)


def calculate_proportional_salary(employee, year, month, working_days, salary_changes):
    """Calculate proportional salary for a month with salary changes"""
    # If no salary changes, return current salary
    if not salary_changes:
        return get_current_salary(employee, datetime(year, month, 15))  # Mid-month

    # Calculate weighted average based on working days
    total_weighted = 0

    for change in salary_changes:
        salary = change['salary']
        days_effective = change['days']
        total_weighted += salary * days_effective

    return total_weighted / working_days