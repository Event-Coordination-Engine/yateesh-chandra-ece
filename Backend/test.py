from datetime import datetime
i = ["19-09-2024", "01-09-2023", "09-12-2023"]
f = datetime.now().strftime("%H:%M")
print(f <= "17:30")
# for j in i:
#     if j < datetime.now().strftime("%d-%m-%Y") :
#         print(j)