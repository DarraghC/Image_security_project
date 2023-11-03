import re 
import json
import csv
import glob

#TODO These need to be tested 
IMAGE_NAME_PATTERN = '"ArtifactName": "(.*?)",'
VERSION_PATTERN = '"Env": \[(.*?)\],"'
RESULTS_PATTERN = '"Vulnerabilities": \[(.*?)\]'

TRIVY_DIR_PATH = "trivy-reports"
CSV_FILE_PATH = "csv-data/project_data.csv"

def get_json(json_file):
    """
    :param json_file: a json file
    :type json_file: string
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        # print("json_data : {0}".format(json_data))
        # print("json_data_type : {0}".format(type(json_data)))
        json_data_string = str(json_data)

    return json_data_string

def parse_string_data(json_string_data):
    """
    This function will pick the data I want from the json string data

    :param json_string_data: json data converted to string
    :type json_string_data: string
    """
    image_name = re.findall(IMAGE_NAME_PATTERN, str(json_string_data))

    image_version = re.findall(VERSION_PATTERN, str(json_string_data))

    results_data = re.findall(RESULTS_PATTERN, str(json_string_data))

    return image_name, image_version, results_data

def check_csv_file_empty():
    """
    Checks whether csv file already exists
    """
    with open(CSV_FILE_PATH, 'r') as file:
        csv_reader = csv.reader(file)
        # Check if there are any rows in the CSV file
        return not any(row for row in csv_reader)

def write_headers_to_file():
    """
    This function writes the first line to the csv
    """
    headers = ['Image Name, Version, Low Severity, Medium Severity, High Severity, Results']

    with open(CSV_FILE_PATH, "w") as csv_file:
        csv_file.write(",".join(header.strip() for header in headers[0].split(',')))



def write_parsed_data(image_name, image_version, low_count, medium_count, high_count, results_data):
    """
    Writes data to csv_file
    """
    with open(CSV_FILE_PATH, "a") as csv_file:
        csv_file.write("\n")
        csv_file.write("{0},{1},{2},{3},{4},{5}".format(image_name, image_version, low_count, medium_count, high_count, results_data))


def count_error_in_results(results_data):
    """
    This function checks the different Severitys 
    """
    low_count = results_data.count("LOW")
    medium_count = results_data.count("MEDIUM")
    high_count = results_data.count("HIGH") 

    print("count_is : {0}, {1}, {2}".format(low_count, medium_count, high_count))

    return low_count, medium_count, high_count
    

def execute_flow():
    """
    This is the main function that will call every other function
    """
    json_files_list = glob.glob(f'{TRIVY_DIR_PATH}/*.json')

    # print("json_files_list {0}".format(json_files_list))
    # print("json_files_list_type {0}".format(type(json_files_list)))

    for json_file in json_files_list:
        json_string_data = get_json(json_file)
        print("json_string_data {0}".format(json_string_data))
        print("json_string_data_type {0}".format(type(json_string_data)))

        image_name, image_version, results_data = parse_string_data(json_string_data)

        print("image_name is : {0}".format(image_name))
        print("image_version is : {0}".format(image_version))
        print("results_data is : {0}".format(results_data))

        low_count, medium_count, high_count = count_error_in_results(results_data)

        if check_csv_file_empty():
            write_headers_to_file()



        write_parsed_data(image_name, image_version, results_data, low_count, medium_count, high_count)

