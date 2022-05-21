from datetime import datetime


# print(datetime.now().isoformat())
# print(datetime.now())

dateRange = {"from" : "2022-05-10T11:02:40.705+00:00", "to" : "2022-05-20T11:02:40.705+00:00"}
schedules = [
    {"from" : "2022-05-11T11:02:40.705+00:00", "to" : "2022-05-12T11:02:40.705+00:00"},
    {"from" : "2022-05-13T11:02:40.705+00:00", "to" : "2022-05-14T11:02:40.705+00:00"},
    {"from" : "2022-05-14T11:02:40.705+00:00", "to" : "2022-05-16T11:02:40.705+00:00"},
    {"from" : "2022-05-16T11:02:40.705+00:00", "to" : "2022-05-17T11:02:40.705+00:00"},
]

availableTimes = [dateRange]

for schedule in schedules:
    fromDate = datetime.fromisoformat(schedule["from"])
    toDate = datetime.fromisoformat(schedule["to"])
    
    for availableTime in availableTimes:
        availableTimeFrom = datetime.fromisoformat(availableTime["from"])
        availableTimeTo = datetime.fromisoformat(availableTime["to"])
        if fromDate >= availableTimeFrom and toDate <= availableTimeTo:
            # print(availableTimes)
            newFreeTimeA = {"from" : availableTimeFrom.isoformat(), "to" : fromDate.isoformat()}
            newFreeTimeB = {"from" : toDate.isoformat(), "to" : availableTimeTo.isoformat()}

            availableTimes.remove(availableTime) # removing the old time

            if availableTimeFrom != fromDate:
                availableTimes.append(newFreeTimeA)

            if toDate != availableTimeTo:    
                availableTimes.append(newFreeTimeB)
            

print(availableTimes)
