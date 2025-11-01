import datetime
import matplotlib.pyplot as plt
import math
import csv
import sys
import os

CSV_DATE_FORMAT = "%d %B %Y"
MAX_MONTH_TESTING_HOURS = 160
MAX_WEEK_TESTING_HOURS = 37
MAX_DAY_TESTING_HOURS = 37/5

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
                case "Product":
                    test["product"] = row[1]
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

def getMaxTime(flag: str) -> float:
    match flag:
        case "d":
            return MAX_DAY_TESTING_HOURS
        case "w":
            return MAX_WEEK_TESTING_HOURS
        case "m":
            return MAX_MONTH_TESTING_HOURS
    
    print(f"Error: getMaxTime() given invalid flag '{flag}'.")
    sys.exit(1)

############
#   MAIN   #
############

if len(sys.argv) > 4 or len(sys.argv) < 4:
    print("Usage: python ta.py [csv_directory_path] [graph_threshold%] [d|w|m]\n")
    sys.exit(1)

csv_directory_path = sys.argv[1]
if not os.path.isdir(csv_directory_path):
    print(f"Error: The path '{csv_directory_path}' is not a valid directory.")
    sys.exit(1)

threshold_flag: float = 0.0

try:
    threshold_flag = int(sys.argv[2]) / 100
    if threshold_flag > 1:
        print(f"Error: graph_threshold% must be a positive integer less than or equal to 100.")
        sys.exit(1)
    elif threshold_flag < 0:
        print(f"Error: graph_threshold% must be a positive integer less than or equal to 100.")
        sys.exit(1)
except ValueError:
    print(f"Error: graph_threshold% must be a positive integer less than or equal to 100.")
    sys.exit(1)
    
time_flag = sys.argv[3]

if time_flag != "d" and time_flag != "w" and time_flag != "m":
    print(f"Error: must select one of d|w|m (days|weeks|months).")
    sys.exit(1)

station_tests_duration_cumulative: dict[str, dict] = {}
product_test_quantity: dict[str, int] = {}

def searchAndGroupByDate(csv_directory_path):
    for entry in os.listdir(csv_directory_path):
        file_path = os.path.join(csv_directory_path, entry)

        if os.path.isdir(file_path):
            searchAndGroupByDate(file_path)
            continue
        elif not entry.endswith(".csv"):
            print("skipping non-csv/non-dir: " + file_path)
            continue
        else:
            print(file_path)
        
        station_tests = read_csv(file_path)

        # get total test duration on station for given time period
        for stationid in station_tests.keys():
            if station_tests_duration_cumulative.get(stationid) == None:
                station_tests_duration_cumulative[stationid] = {}

            for test_instance in station_tests[stationid]:
                test_date = getCorrectDate(test_instance["test_date"], time_flag)
                if station_tests_duration_cumulative[stationid].get(test_date) == None:
                    station_tests_duration_cumulative[stationid][test_date] = 0

                station_tests_duration_cumulative[stationid][test_date] += test_instance["test_duration"]
        
        # get how many tests ran on each product
        for test_list in station_tests.values():
            for test_instance in test_list:
                product = test_instance["product"]
                if product_test_quantity.get(product) == None:
                    product_test_quantity[product] = 0
                product_test_quantity[product] += 1


searchAndGroupByDate(csv_directory_path)

def padDateLabels(sorted_station_data: list[tuple[datetime.datetime, float]], flag: str) -> list[tuple[datetime.datetime, float]]:
    pad = datetime.timedelta()

    match flag:
        case "d":
            pad = datetime.timedelta(days=1)
        case "w":
            pad = datetime.timedelta(weeks=1)
        case "m":
            pad = datetime.timedelta(weeks=5)
    
    if len(sorted_station_data) == 0:
        return sorted_station_data
    
    padded_station_data = sorted_station_data.copy()

    index = 0
    pads = 1
    while index < len(sorted_station_data):
        next_interval = getCorrectDate(sorted_station_data[index][0] + pad, flag)

        if index + 1 == len(sorted_station_data):
            index += 1
            continue
        
        if sorted_station_data[index + 1][0] != next_interval:
            padded_station_data.insert(index + pads, (next_interval, 0))
            pads += 1
        
        index += 1
    
    return padded_station_data

duration_result_file = open("duration_result.csv", "w")
duration_result_file.write("Station ID,Date Tested,Total Test Duration\n")

for station_id, tests in station_tests_duration_cumulative.items():
    sorted_station_data: list[tuple[datetime.datetime, float]] = sorted(tests.items())
    sorted_station_data = padDateLabels(sorted_station_data, time_flag)

    date_results = []
    duration_results = []

    for date_info in sorted_station_data:
        date_results.append(date_info[0].strftime("%d/%m/%Y"))
        duration_results.append(date_info[1]/3600)

        result: str = station_id + "," + date_info[0].strftime("%d/%m/%Y,") + str(round(date_info[1])) + "\n"
        duration_result_file.write(result)
    
    n = len(date_results)
    plt.figure(figsize=(15, 9))
    plt.bar(date_results, duration_results)
    max_test_time = getMaxTime(time_flag)
    plt.axhline(y=max_test_time, color="red")
    plt.axhline(y=max_test_time * threshold_flag, color="green")
    plt.title("Cumulative Test Duration")
    plt.ylabel("Hours")
    plt.xticks(date_results[::math.ceil(n/30)], rotation=45, ha="right")
    plt.savefig("graphs/" + station_id + ".pdf")
    plt.close()


duration_result_file.close()

quantity_result_file = open("quantity_result.csv", "w")
quantity_result_file.write("Product,Test Quantity\n")
total_tests = 0

sorted_quantity_data = sorted(product_test_quantity.items())

for product, quantity in sorted_quantity_data:
    total_tests += quantity
    quantity_result_file.write(product + "," + str(quantity) + "\n")

quantity_result_file.write("\nTotal Test Quantity\n" + str(total_tests) + "\n")
quantity_result_file.close()
