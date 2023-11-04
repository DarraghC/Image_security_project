import re 
import json
import csv
import glob
import requests

#TODO These need to be tested 
IMAGE_NAME_PATTERN = r"'([^']+):latest'"
VERSION_PATTERN = r'{0}:(\S+)'
RESULTS_PATTERN = '"Vulnerabilities": \[(.*?)\]'

TRIVY_DIR_PATH = "trivy-reports"
INSPECT_JSON_DIR_PATH = "trivy-version-reports"
CSV_FILE_PATH = "csv-data/project_data.csv"

# IMAGE_VERSION_DICT = os.getenv("VERSION_DICT")

def get_version_tags():
    repository_list = ["alpine", "nginx", "ubuntu", "python", "redis", "postgres", "node", "httpd", "memcached", "mongo", "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby", "haproxy", "tomcat", "kong", "neo4j"]  # Replace with your desired repository and image name

    # Make a GET request to the Docker Hub API
    for image in repository_list:
        tags_url = f"https://hub.docker.com/v2/repositories/library/{image}/tags/"
        response = requests.get(tags_url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            # Extract and print the tags and last updated dates
            for tag_info in results:
                tag_name = tag_info["name"]
                last_updated = tag_info["last_updated"]
                print(f"Tag: {tag_name}, Last Updated: {last_updated}")
        else:
            print(f"Failed to retrieve tags. Status code: {response.status_code}")

def get_json(json_file):
    """
    :param json_file: a json file
    :type json_file: string
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        json_data_string = str(json_data)

    return json_data_string

def parse_version_data(json_inspect_string_data, image_name):
    """
    Gets image version from 
    """
    print("my_version_pattern : {0}".format(VERSION_PATTERN.format(image_name)))
    image_version = re.findall(VERSION_PATTERN.format(image_name), str(json_inspect_string_data))
    print("meh : {0}".format(image_version))
    image_version = str(image_version[0])
    image_version = image_version.replace("'", '').replace(',', '')
    
    return image_version


def parse_string_data(json_string_data):
    """
    This function will pick the data I want from the json string data

    :param json_string_data: json data converted to string
    :type json_string_data: string
    """
    image_name = re.findall(IMAGE_NAME_PATTERN, str(json_string_data))
    image_name = str(set(image_name))
    image_name = image_name.replace('{', '').replace('}', '').replace("'", '')
    # image_name = image_name.upper()
    # the_version_patter = VERSION_PATTERN.format(image_name)
    # print(str(json_string_data))
    results_data = re.findall(RESULTS_PATTERN, str(json_string_data))

    return image_name, results_data

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

# def testing_something(my_image_name):
#     # Specify the image name
#     image_name = "{0}:latest"

#     # Run the 'docker inspect' command to get image details
#     command = f'docker inspect --format="{{.Id}} {{.Created}}" {image_name.format(my_image_name)}'
#     output = subprocess.check_output(command, shell=True, universal_newlines=True)

#     # Extract the image ID and created date
#     image_id, created_date = output.strip().split()

#     print(f"Image ID: {image_id}")
#     print(f"Created Date: {created_date}")
    

def execute_flow():
    """
    This is the main function that will call every other function
    """
    get_version_tags()
    # json_files_list = glob.glob(f'{TRIVY_DIR_PATH}/*.json')
    # json_inspect_file_list = glob.glob(f'{INSPECT_JSON_DIR_PATH}/*.json')

    # # print("json_files_list {0}".format(json_files_list))
    # # print("json_files_list_type {0}".format(type(json_files_list)))

    # for json_file in json_files_list:
    #     json_string_data = get_json(json_file)
    #     # print("json_string_data {0}".format(json_string_data))
    #     # print("json_string_data_type {0}".format(type(json_string_data)))

    #     image_name, results_data = parse_string_data(json_string_data)

    #     for file in json_inspect_file_list:

    #         inspect_file_string = "{0}_latest"
    #         # print(json_inspect_file_list)
    #         # print(inspect_file_string.format(image_name))
    #         # print(file)
    #         if inspect_file_string.format(image_name) in file:
    #             print("got here")
    #             json_inspect_string_data = get_json(file)
    #             # print("inspect_data : {0}".format(json_inspect_string_data))
    #             image_version = parse_version_data(json_inspect_string_data, image_name)
    #             # testing_something(image_name)

    #             # print("image_name is : {0}".format(image_name))
    #             print("image_version_is : {0}".format(image_version))
    #             print("results_data is : {0}".format(results_data))

    #             low_count, medium_count, high_count = count_error_in_results(results_data)

    #             if check_csv_file_empty():
    #                 write_headers_to_file()



                # write_parsed_data(image_name, image_version, results_data, low_count, medium_count, high_count)

