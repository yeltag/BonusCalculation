from datetime import datetime, timedelta
import math

class BonusCalculator:
    def __init__(self, database, config_manager):
        self.database = database
        self.config_manager = config_manager

    def calculate_monthly_bonus(self, employee_id, year, month):
        """Calculate bonus for an employee for a specific month"""
        # Get employee data
        employees = self.database.get_all_employees()
        employee = next((emp for emp in employees if emp["id"] == employee_id), None)

        if not employee:
            return None


        monthly_salary = employee["salary"]

        # Get applicable KPIs
        kpis = self.config_manager.get_kpis()
        print(f"DEBUG: Found {len(kpis)} total KPIs")

        applicable_kpis = [kpi for kpi in kpis if self._is_kpi_applicable(kpi, employee)]

        print(f"DEBUG: {len(applicable_kpis)} KPIs applicable to {employee['first_name']} in {employee['department']}")

        # Calculate bonus based on KPIs
        total_bonus = 0
        kpi_details = []

        for kpi in applicable_kpis:
            bonus_amount = self._calculate_kpi_bonus(kpi, monthly_salary, employee)
            print(f"DEBUG: KPI '{kpi['name']}' calculated bonus: ${bonus_amount:.2f}")
            total_bonus +=bonus_amount

            kpi_details.append({
                "kpi_name": kpi['name'],
                "calculation_method": kpi["calculation_method"],
                "bonus_amount": bonus_amount
            })

        print(f"DEBUG: Total bonus for {employee['first_name']}: ${total_bonus:.2f}")

        return {
            "employee_id": employee_id,
            "employee_name": f"{employee["first_name"]} {employee['last_name']}",
            "period_month": month,
            "period_year": year,
            "base_salary": monthly_salary,
            "calculated_bonus": total_bonus,
            "kpi_details": kpi_details
        }

    def _calculate_proportional_salary(self, employee, salary_history, year, month):
        """Calculate proportional salary based on salary changes during the month"""
        return employee["salary"]
        # Get first and last day of the month
        # first_day = datetime(year, month,1)
        # if month == 12:
        #     last_day = datetime(year+1,1,1) - timedelta(days = 1)
        # else:
        #     last_day = datetime(year, month +1,1) - timedelta(days =1)
        #
        # total_days = (last_day - first_day).days +1
        # weighted_salary = 0
        #
        # # Find salary periods that overlap with the target month
        #
        # for salary_record in salary_history:
        #     effective_date = datetime.strptime(salary_record["effective_date"], "%Y-%m-%d")
        #
        #     end_date = salary_record["end_date"]
        #
        #     if end_date:
        #         end_date = datetime.strptime(end_date, "%Y-%m-%d")
        #
        #     else:
        #         end_date = last_day # Current salary
        #
        #     # Calculate overlap period
        #     period_start = max(effective_date, first_day)
        #     period_end = min(end_date, last_day)
        #
        #     if period_start <= period_end:
        #         period_days = (period_end - period_start).days +1
        #         daily_salary = salary_record["salary"] / total_days
        #         weighted_salary += daily_salary * period_days
        #
        # return weighted_salary

    def _is_kpi_applicable(self, kpi, employee):
        """Check if KPI applies to employee's department"""
        applicable_depts = kpi.get("applicable)_departments",[])
        is_applicable = not applicable_depts or employee['department'] in applicable_depts
        print(f"DEBUG: KPI '{kpi['name']}' for department {employee['department']} - Applicable: {is_applicable}")
        return is_applicable

    def _calculate_kpi_bonus(self, kpi,base_salary, employee):
        """Calculate bonus for a spesific KPI"""
        method = kpi["calculation_method"]
        print(f"DEBUG: Calculating KPI '{kpi['name']}' using method: {method}")

        if method == "percentage":
            percentage = kpi.get('percentage', 0)
            bonus = base_salary * percentage
            print(f"    Percentage: {percentage}")
            print(f"    Calculation: ${base_salary} * {percentage} = ${bonus:,.2f}")
            return bonus

        elif method == "fixed":
            # Fixed amount per achivement
            fixed_amount = kpi.get("fixed_amount", 100)  # Default $100
            print(f"DEBUG: Fixed amount: ${fixed_amount}")
            return fixed_amount

        elif method == "formula":
            # Custom formula - simplified for now
            formula = kpi.get("formula", "base_salary * 0.05")
            print(f"DEBUG: Formula: {formula}")
            try:
                # In real implementation, you'd use a safe formula evaluator
                # This is a simplified version
                if "base_salary" in formula:
                    result = eval(formula.replace("base_salary", str(base_salary)))
                    return result
                else:
                    result = eval(formula)
                print(f"DEBUG: Formula result: ${result:.2f}")
                return result

            except Exception as e:
                print(f"DEBUG: Formula error: {e}")
                return 0

        print(f"DEBUG: Unknown method, returning 0")
        return 0