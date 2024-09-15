from datetime import datetime, timedelta
i = ["19-09-2024", "01-09-2023", "09-12-2023"]
# f = datetime.now().strftime("%d-%m-%Y") - 1

# Format it as a string in the desired format (day-month-year)
date_to_show = (datetime.now() - timedelta(days=2)).strftime("%d-%m-%Y")

print(formatted_yesterday)
# print(f)