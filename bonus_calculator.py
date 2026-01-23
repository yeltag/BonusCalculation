from datetime import datetime, timedelta
import math
from PyQt6.QtWidgets import QMessageBox


class BonusCalculator:
    def __init__(self, database, config_manager):
        self.database = database
        self.config_manager = config_manager

    def calculate_monthly_bonus(self, employee_id, year, month, proportional_salary=None):
        """Calculate bonus for an employee for a specific month"""
        # Get employee data
        employees = self.database.get_all_employees()
        employee = next((emp for emp in employees if emp["id"] == employee_id), None)

        if not employee:
            return None

        # Use proportional salary if provided, otherwise use current salary
        if proportional_salary is not None:
            monthly_salary = proportional_salary
            print(f"DEBUG: Using proportional salary for {employee['first_name']}: ${monthly_salary:,.2f}")
        else:
            monthly_salary = employee["salary"]
            print(f"DEBUG: Using current salary for {employee['first_name']}: ${monthly_salary:,.2f}")

        # Get applicable KPIs
        kpis = self.config_manager.get_kpis()
        print(f"DEBUG: Found {len(kpis)} total KPIs")

        applicable_kpis = [kpi for kpi in kpis if self._is_kpi_applicable(kpi, employee)]

        print(f"DEBUG: {len(applicable_kpis)} KPIs applicable to {employee['first_name']} in {employee['department']}")

        # Get custom variables
        custom_variables = []
        if self.database:
            try:
                custom_variables = self.database.get_custom_variables()
            except Exception as e:
                print(f"Error loading custom variables: {e}")

        # Calculate bonus based on KPIs
        total_bonus = 0
        kpi_details = []

        for kpi in applicable_kpis:
            bonus_amount = self._calculate_kpi_bonus(kpi, monthly_salary, employee, custom_variables, year, month)
            print(f"DEBUG: KPI '{kpi['name']}' calculated bonus: ${bonus_amount:.2f}")
            total_bonus += bonus_amount

            kpi_details.append({
                "kpi_name": kpi['name'],
                "calculation_method": kpi["calculation_method"],
                "bonus_amount": bonus_amount
            })

        print(f"DEBUG: Total bonus for {employee['first_name']}: ${total_bonus:.2f}")

        return {
            "employee_id": employee_id,
            "employee_name": f"{employee['last_name']} {employee['first_name']} {employee['father_name']}",
            "department": employee['department'],
            "period_month": month,
            "period_year": year,
            "base_salary": monthly_salary,
            "calculated_bonus": total_bonus,
            "kpi_details": kpi_details
        }

    def _calculate_proportional_salary(self, employee, salary_history, year, month, working_days=None):
        """Calculate proportional salary based on salary changes during the month"""
        # If no working days specified, return current salary
        if not working_days or working_days <= 0:
            return employee["salary"]

        # Get first and last day of the month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        total_days = (last_day - first_day).days + 1

        # Convert working_days to actual days proportion
        # We assume working days are evenly distributed throughout the month
        daily_rate = employee["salary"] / working_days if working_days > 0 else 0

        # Find salary periods that overlap with the target month
        weighted_salary = 0

        for salary_record in salary_history:
            effective_date = datetime.strptime(salary_record["effective_date"], "%Y-%m-%d")

            end_date = salary_record["end_date"]
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_date = last_day  # Current salary

            # Calculate overlap period
            period_start = max(effective_date, first_day)
            period_end = min(end_date, last_day)

            if period_start <= period_end:
                # Calculate working days in this period
                # Simple approximation: proportion of calendar days
                period_calendar_days = (period_end - period_start).days + 1
                period_working_days = max(1, int(period_calendar_days * working_days / total_days))

                weighted_salary += salary_record["salary"] * period_working_days

        # Divide by total working days to get average
        proportional_salary = weighted_salary / working_days if working_days > 0 else employee["salary"]

        print(f"DEBUG: Proportional salary for {employee['first_name']}: ${proportional_salary:,.2f} "
              f"(based on {working_days} working days)")

        return proportional_salary

    def _is_kpi_applicable(self, kpi, employee):
        """Check if KPI applies to employee's department"""
        applicable_depts = kpi.get("applicable_departments", [])
        is_applicable = not applicable_depts or employee['department'] in applicable_depts
        print(f"DEBUG: KPI '{kpi['name']}' for department {employee['department']} - Applicable: {is_applicable}")
        return is_applicable

    def _calculate_kpi_bonus(self, kpi, base_salary, employee, custom_variables, year, month):
        """Calculate bonus for a specific KPI"""
        method = kpi["calculation_method"]
        print(f"DEBUG: Calculating KPI '{kpi['name']}' using method: {method}")

        if method == "percentage":
            percentage = kpi.get('percentage', 0.1)
            bonus = base_salary * percentage
            print(f"    Percentage Calculation: ${base_salary} * {percentage} = ${bonus:,.2f}")
            return bonus

        elif method == "fixed":
            fixed_amount = kpi.get("fixed_amount", 100)
            print(f"DEBUG: Fixed amount: ${fixed_amount}")
            return fixed_amount

        elif method == "formula":
            formula = kpi.get("formula", "base_salary * 0.05")
            print(f"DEBUG: Formula: {formula}")
            try:
                # Create evaluation environment with employee data
                eval_env = {
                    "base_salary": base_salary,
                    "min": min,
                    "max": max,
                    "round": round,
                    "sum": sum,
                    "abs": abs
                }

                # Add ACTUAL variable values from database
                if self.database:
                    variable_values = self.database.get_employee_variable_values(
                        employee['id'], year, month
                    )
                    eval_env.update(variable_values)
                    print(f"DEBUG: Loaded variable values: {variable_values}")

                # Add default values for any missing custom variables
                for var in custom_variables:
                    if var['name'] not in eval_env:  # Only add if not already set from database
                        if var['data_type'] in ['number', 'percentage', 'currency']:
                            try:
                                eval_env[var['name']] = float(var.get('default_value', 0))
                            except (ValueError, TypeError):
                                eval_env[var['name']] = 0
                        else:
                            eval_env[var['name']] = var.get('default_value', "")

                # Replace custom syntax
                formula = formula.replace(" then ", " if ").replace(" else ", " else ")

                result = eval(formula, {"__builtins__": {}}, eval_env)
                print(f"DEBUG: Formula result: {result:.2f}")
                return result
            except Exception as e:
                print(f"DEBUG: Formula error: {e}")
                return 0

        print(f"DEBUG: Unknown method, returning 0")
        return 0

    def _get_years_of_service(self, employee, calculation_date=None):
        """Calculate actual years of service"""
        if calculation_date is None:
            calculation_date = datetime.now()

        hire_date = datetime.strptime(employee['hire_date'], "%Y-%m-%d")
        years = (calculation_date - hire_date).days / 365.25
        return max(0, years)  # Ensure non-negative

    def are_variable_values_saved(self, year, month, department):
        """Check if variable values are saved in database for the given period and department"""
        try:
            employees = self.database.get_all_employees()
            custom_variables = self.database.get_custom_variables()
            kpis = self.config_manager.get_kpis()

            # Filter employees by department
            filtered_employees = []
            for employee in employees:
                if department == "All Departments" or employee['department'] == department:
                    filtered_employees.append(employee)

            # For each employee, check if all applicable variables have values
            for employee in filtered_employees:
                if employee["status"] != "Active":
                    continue

                # Get variables applicable to this employee
                applicable_vars = self._get_applicable_variables_for_employee(employee, kpis, custom_variables)

                for var_name in applicable_vars:
                    value = self.database.get_employee_variable_value(
                        employee['id'], var_name, year, month
                    )
                    if value is None:
                        print(f"DEBUG: Missing value for {employee['id']}, variable {var_name}")
                        return False

            return True

        except Exception as e:
            print(f"Error checking saved values: {e}")
            return False

    def _get_applicable_variables_for_employee(self, employee, kpis, custom_variables):
        """Get variables used in KPIs applicable to this employee"""
        applicable_vars = set()

        for kpi in kpis:
            # Check if KPI applies to employee's department
            applicable_depts = kpi.get('applicable_departments', [])
            if not applicable_depts or employee['department'] in applicable_depts:
                # Check which variables are used in this KPI's formula
                formula = kpi.get('formula', '')
                for var in custom_variables:
                    if var['name'] in formula:
                        applicable_vars.add(var['name'])

        return list(applicable_vars)

    def get_employees_with_salary_changes(self, year, month):
        """Get employees who had salary changes during the specified month - handles multiple changes"""
        employees = self.database.get_all_employees()
        employees_with_changes = []

        # Calculate month boundaries
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        for employee in employees:
            if employee["status"] != "Active":
                continue

            # Get salary history
            salary_history = self.database.get_employee_salary_history(employee["id"])

            if not salary_history or len(salary_history) <= 1:
                continue  # No history or only one salary record

            # Sort by effective date
            salary_history.sort(key=lambda x: x['effective_date'])

            # Collect all changes within this month
            month_changes = []

            for i in range(len(salary_history)):
                record = salary_history[i]
                effective_date = datetime.strptime(record["effective_date"], "%Y-%m-%d")

                # Check if this change happened within this month
                if first_day <= effective_date <= last_day:
                    # Get previous salary (either from previous record or current)
                    if i > 0:
                        prev_record = salary_history[i - 1]
                        prev_salary = prev_record["salary"]
                        prev_effective_date = datetime.strptime(prev_record["effective_date"], "%Y-%m-%d")
                    else:
                        # First record in history, use employee's current as previous?
                        prev_salary = record["salary"]  # This is tricky
                        prev_effective_date = first_day

                    # Only add if it's a real change (different salary)
                    if prev_salary != record["salary"]:
                        month_changes.append({
                            'change_date': effective_date,
                            'old_salary': prev_salary,
                            'new_salary': record["salary"]
                        })

            if month_changes:
                employees_with_changes.append({
                    'employee': employee,
                    'changes': month_changes,  # Now a list of changes
                    'salary_history': salary_history
                })

        return employees_with_changes

    def calculate_bonuses_with_validation(self, year, month, department, parent_dialog=None, working_days=None,
                                          salary_adjustments=None):
        """Calculate bonuses with validation for saved variable values"""
        # Check if values are saved
        if not self.are_variable_values_saved(year, month, department):
            if parent_dialog:
                reply = QMessageBox.warning(
                    parent_dialog,
                    "Unsaved Changes",
                    f"Variable values for {self._get_month_name(month)} {year} ({department}) have not been saved.\n\n"
                    f"Please save the values first before calculating bonuses.",
                    QMessageBox.StandardButton.Ok
                )
            return None

        # Calculate bonuses
        return self.calculate_bonuses_for_department(year, month, department, working_days, salary_adjustments)

    def calculate_bonuses_for_department(self, year, month, department, working_days=None, salary_adjustments=None):
        """Calculate bonuses for a specific department and period"""
        employees = self.database.get_all_employees()
        results = []

        for employee in employees:
            # Apply department filter
            if department != "All Departments" and employee["department"] != department:
                continue

            if employee["status"].lower() == "active":
                proportional_salary = None

                # Check if we have manual salary adjustments from dialog
                if salary_adjustments and employee['id'] in salary_adjustments:
                    proportional_salary = salary_adjustments[employee['id']]['proportional_salary']
                    print(f"DEBUG: Using manual adjustment for {employee['first_name']}: ${proportional_salary:,.2f}")
                # Otherwise, check if salary changed during the month and calculate proportional
                elif working_days and working_days > 0:
                    # Get salary history for this employee
                    salary_history = self.database.get_employee_salary_history(employee["id"])

                    # Check if there were any salary changes in this month
                    has_change_in_month = False
                    if salary_history and len(salary_history) > 1:
                        salary_history.sort(key=lambda x: x['effective_date'])
                        for record in salary_history:
                            effective_date = datetime.strptime(record["effective_date"], "%Y-%m-%d")
                            if effective_date.year == year and effective_date.month == month and effective_date.day != 1:
                                has_change_in_month = True
                                break

                    # If salary changed, calculate proportional salary
                    if has_change_in_month:
                        proportional_salary = self._calculate_proportional_salary(
                            employee, salary_history, year, month, working_days
                        )

                result = self.calculate_monthly_bonus(employee["id"], year, month, proportional_salary)
                if result:
                    results.append(result)

        return results

    def _get_month_name(self, month):
        """Get month name from month number"""
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return months[month - 1] if 1 <= month <= 12 else f"Month {month}"

    def validate_and_calculate_bonuses(self, year, month, department, parent_dialog=None):
        """Complete validation and calculation workflow - used by variable entry dialog"""
        print(f"DEBUG: validate_and_calculate_bonuses called with year={year}, month={month}, department={department}")

        # Check if values are saved
        are_saved = self.are_variable_values_saved(year, month, department)
        print(f"DEBUG: are_variable_values_saved returned: {are_saved}")

        if not are_saved:
            print("DEBUG: Values not saved, showing warning and returning None")
            if parent_dialog:
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.warning(
                    parent_dialog,
                    "Unsaved Changes",
                    f"Variable values for {self._get_month_name(month)} {year} ({department}) have not been saved.\n\n"
                    f"Please save the values first before calculating bonuses.",
                    QMessageBox.StandardButton.Ok
                )
            return None

        # Calculate and return bonuses (without working days for variable entry dialog)
        print("DEBUG: Values are saved, calculating bonuses...")
        results = self.calculate_bonuses_for_department(year, month, department)
        print(
            f"DEBUG: calculate_bonuses_for_department returned: {type(results)} with {len(results) if isinstance(results, list) else 'non-list'} items")
        return results