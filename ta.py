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
                test_date = getCorrectDate(test_instance["test_date"], sys.argv[2].lstrip("-"))
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

duration_result_file = open("duration_result.csv", "w")
duration_result_file.write("Station ID,Date Tested,Total Test Duration\n")

for station_id, tests in station_tests_duration_cumulative.items():
    sorted_station_data: list[tuple[datetime.datetime, float]] = sorted(tests.items())
    print(sorted_station_data)
    for day_info in sorted_station_data:
        result: str = station_id + "," + day_info[0].strftime("%d/%m/%Y,") + str(round(day_info[1])) + "\n"
        duration_result_file.write(result)

duration_result_file.close()

quantity_result_file = open("quantity_result.csv", "w")
quantity_result_file.write("Product,Test Quantity\n")
total_tests = 0

for product, quantity in product_test_quantity.items():
    total_tests += quantity
    quantity_result_file.write(product + "," + str(quantity) + "\n")

quantity_result_file.write("\nTotal Test Quantity\n" + str(total_tests) + "\n")