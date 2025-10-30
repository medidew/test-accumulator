import datetime
import csv
import sys
import os

CSV_DATE_FORMAT = "%d %B %Y"

def read_csv(file_path) -> dict[str, list[dict[str]]]:
    with open(file_path, mode='r', newline='', encoding='utf-8', errors='ignore') as csvfile:

        station_tests: dict[str, list[dict[str]]] = {}
        test: dict[str] = {}
        current_station_id: str = ""

        reader = csv.reader(csvfile)
        
        for row in reader:  # reads file from top -> bot
            if len(row) == 0:
                continue
            match row[0]:
                case "Tested":
                    test["test_date"] = datetime.datetime.strptime(row[2], CSV_DATE_FORMAT)
                case "Station ID":
                    current_station_id = row[1]
                    if station_tests.get(current_station_id) == None:
                        station_tests[current_station_id] = []
                case "Test Time":
                    row_info = row[1].split(" ")
                    test["test_duration"] = float(row_info[0])
                    station_tests[current_station_id].append(test.copy())
                    
    return station_tests

def weekCommencing(date: datetime.datetime) -> datetime.datetime:
    adjust = datetime.timedelta(days=date.weekday())
    return date - adjust

def monthCommencing(date: datetime.datetime) -> datetime.datetime:
    adjust = datetime.timedelta(days=date.day-1)
    return date - adjust

def getCorrectDate(date: datetime.datetime, flag: str) -> datetime.datetime:
    match flag:
        case "d":
            return date
        case "w":
            return weekCommencing(date)
        case "m":
            return monthCommencing(date)
    
    print(f"Error: getCorrectDate() given invalid flag '{flag}'.")
    sys.exit(1)

############
#   MAIN   #
############

if len(sys.argv) > 3 or len(sys.argv) < 3:
    print("Usage: python ta.py [csv_directory_path] -[d|w|m]\nExisting flags:\n   -d : groups cumulative test times by day\n   -w : groups cumulative test times by week\n   -m : groups cumulative test times by month")
    sys.exit(1)

csv_directory_path = sys.argv[1]
if not os.path.isdir(csv_directory_path):
    print(f"Error: The path '{csv_directory_path}' is not a valid directory.")
    sys.exit(1)
    
stations_tests_cumulative: dict[str, dict] = {}

for entry in os.listdir(csv_directory_path):
    if not entry.endswith('.csv'):
        continue

    file_path = os.path.join(csv_directory_path, entry)
    print(file_path)
    station_tests = read_csv(file_path)

    for stationid in station_tests.keys():
        if stations_tests_cumulative.get(stationid) == None:
            stations_tests_cumulative[stationid] = {}
        
        for test in station_tests[stationid]:
            test_date = getCorrectDate(test["test_date"], sys.argv[2].lstrip("-"))
            if stations_tests_cumulative[stationid].get(test_date) == None:
                stations_tests_cumulative[stationid][test_date] = 0
            
            stations_tests_cumulative[stationid][test_date] += test["test_duration"]

result_file = open("result.csv", "w")
result_file.write("Station ID,Date Tested,Total Test Duration\n")

for station_id, tests in stations_tests_cumulative.items():
    sorted_station_data: list[tuple[datetime.datetime, float]] = sorted(tests.items())
    for day_info in sorted_station_data:
        result: str = station_id + "," + day_info[0].strftime("%d/%m/%Y,") + str(round(day_info[1])) + "\n"
        result_file.write(result)