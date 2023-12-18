import re 
import json
import ast
import csv
import glob

IMAGE_NAME_PATTERN = r"'([^']+):latest'"
VERSION_PATTERN = r'{0}:(\S+)'
RESULTS_PATTERN = '"Vulnerabilities": \[(.*?)\]'

TRIVY_DIR_PATH = "trivy-reports"
CSV_FILE_PATH = "csv-data/project_data.csv"


VERSION_RESULTS_DIR = "version_dict_file.txt"
VERSION_RELEASE_DIR = "version_release_dict.txt"
OLDEST_VERSION_FILE_NAME = "oldest_versions.txt"

version_dict = {}
# image_list = ["alpine", "nginx", "ubuntu", "redis", "postgres", "node", "httpd", "memcached", "python", "mongo",
#               "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby",
#               "haproxy", "tomcat", "kong", "neo4j", "amazonlinux", "caddy", "bash", "gradle", "plone", "fedora",
#               "groovy", "rust", "redmine", "amazoncorretto", "erlang", "elixir", "jruby", "jetty", "odoo", "xwiki",
#               "swift", "hylang", "archlinux", "tomee", "gcc", "monica", "varnish","orientdb", "julia"] 
image_list = ["odoo", "neo4j", "orientdb", "plone", "ubuntu", "Alpine"]

image_dicts = {}
oldest_for_date_dict = {}

def get_json(json_file):
    """
    :param json_file: a json file
    :type json_file: string
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        json_data_string = str(json_data)

    return json_data_string

def create_image_unique_version_dict():
    """
    Creates a dict with each image as a key and a empty list for the 
    """
    # global image_dicts
    for image in image_list:
        oldest_for_date_dict[image]= []
    print("oldest_for_date_dict : {0}".format(image_dicts))

def create_image_dicts():
    """
    Creates a dict with each image as a key and a empty list for the 
    """
    # global image_dicts
    for image in image_list:
        image_dicts[image]= []

    print("Image dict is : {0}".format(image_dicts))

def get_oldest_version_for_date_dict():
    """
    opens a text file and puts the data into a dictionary for easier use
    """
    with open(OLDEST_VERSION_FILE_NAME) as file: 
        Lines = file.readlines() 
        for line in Lines:
            day, image_data_str = line.split(": {'")
            image_data_str = image_data_str.rstrip("'}")  # Remove trailing characters

            # Split image data into individual image entries
            image_entries = image_data_str.split("', '")

            # Process each image entry
            for item in image_entries:
                for image_name in oldest_for_date_dict.keys():
                    if image_name in item:
                        item = item.strip("[]")
                        print("image_name {0} : item = {1}".format(image_name, item))
                        
                        # Split each item into key-value pairs
                        key, version_data = item.split(": ")
                        # print("key {0}".format(key))
                        # print("version_data {0}".format(version_data))
                        
                        # Extract version and date-time information
                        version, date_time = version_data.split(", ")
                        # print("version {0}".format(version))
                        # print("date_time {0}".format(date_time))
                        oldest_for_date_dict[image_name].append(version)
    print(oldest_for_date_dict)
            

def get_version_dict():
    """
    opens a text file and puts the data into a dictionary for easier use
    """  
    # reading the data from the file 
    with open(VERSION_RESULTS_DIR) as file: 
        Lines = file.readlines() 
        for line in Lines:
            split_data  = line.split(":")
            split_data[1] =split_data[1].replace('"', '').replace("\n", "").replace("]", "").replace("[", "")
            version_data = split_data[1]
            version_list = [item.strip() for item in version_data.split(',')]
            version_list = [item.strip("' ") for item in version_list]
            version_dict[split_data[0]] = version_list
        print("version_dict : {0}".format(version_dict))

def get_version_release_dict():
    """
    opens a text file and puts the data into a dictionary for easier use
    """
    with open(VERSION_RELEASE_DIR) as file: 
        Lines = file.readlines() 
        for line in Lines:
            key, value = line.split(':', 1)
            for image_name in image_dicts.keys():
                if image_name == key:
                    new_value = value.replace('"', '').replace("\n", "").replace("]", "").replace("[", "")
                    updated_list = new_value.split("',")
                    new_list = []
                    for item in updated_list:
                        item = item.replace("'", "")
                        new_list.append(item)
                    image_dicts[key] = new_list
    print("image_dicts : {0}".format(image_dicts))
            

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
    headers = ['Image Name, Version, Date, Low Severity, Medium Severity, High Severity, Critical Severity']

    with open(CSV_FILE_PATH, "w") as csv_file:
        csv_file.write(",".join(header.strip() for header in headers[0].split(',')))


def values_exist_in_file(image_name, image_version, version_date_published):
    """
    Checks if values already exist in the CSV file
    """
    with open(CSV_FILE_PATH, "r", newline='') as read_file:
        return any(image_name in line and image_version in line and version_date_published in line for line in read_file)
    

def write_parsed_data(image_name, image_version, version_date_published, low_count, medium_count, high_count, critical_count):
    """
    Writes data to csv_file
    """
    if not values_exist_in_file(image_name, image_version, version_date_published):
        with open(CSV_FILE_PATH, "a") as csv_file:
            csv_file.write("\n")
            print(image_name, image_version, version_date_published)
            csv_file.write("{0},{1},{2},{3},{4},{5},{6}".format(image_name, image_version, version_date_published, low_count, medium_count, high_count, critical_count))
    else:
        print("Values already exist {0}, {1}. {2}:".format(image_name, image_version, version_date_published))

def count_error_in_results(results_data):
    """
    This function checks the different Severitys 
    """
    low_count = results_data.count("LOW")
    medium_count = results_data.count("MEDIUM")
    high_count = results_data.count("HIGH") 
    critical_count = results_data.count("CRITICAL") 


    print("count_is : {0}, {1}, {2}, {3}".format(low_count, medium_count, high_count, critical_count))

    return low_count, medium_count, high_count, critical_count
    

def execute_flow():
    """
    This is the main function that will call every other function
    """
    create_image_dicts()
    create_image_unique_version_dict()
    get_oldest_version_for_date_dict()
    get_version_dict()
    get_version_release_dict()
    json_files_list = glob.glob(f'{TRIVY_DIR_PATH}/*.json')

    print("json_files_list {0}".format(json_files_list))

    for json_file in json_files_list:
        for image in image_list:
            # print("json file {0}:type {1}  Image is {2} : type{3}".format(json_file, type(json_file), image, type(image)))
            if image in json_file:
                # print("got here")
                json_string_data = get_json(json_file)
                # print("json_string_data {0}".format(json_string_data))
                # image_name, results_data = parse_string_data(json_string_data)
                # print("image name is {0} and type is {1}".format(image_name, type(image_name)))
                # print("image is {0} and type is {1}".format(image, type(image)))

                for version_dict_image_key, version_list in version_dict.items():
                    if image == version_dict_image_key:
                        for version in version_list:
                            for image_key, dict_version_list in oldest_for_date_dict.items():
                                if image == image_key:
                                    for the_version in dict_version_list:
                                        if version == the_version:
                                            if "trivy-reports/{0}_{1}.json".format(image, version) in json_file:
                                                for image_dicts_image, versions_dates_list in image_dicts.items():
                                                    if image == image_dicts_image:
                                                        for item in versions_dates_list:
                                                            # print("blah: {0}".format(versions_dates_list))
                                                            # print("version is: {0} , item is {1}".format(version, item))
                                                            if version in item:
                                                                version_and_date_list = item.split(',')
                                                                version_date_published = version_and_date_list[1]

                                                                print("Version is: {0}, Published: {1}".format(version, version_date_published))

                                                                # print("results_data is : {0}".format(results_data))

                                                                low_count, medium_count, high_count, critical_count = count_error_in_results(json_string_data)

                                                                if check_csv_file_empty():
                                                                    write_headers_to_file()
                                                                write_parsed_data(image, version, version_date_published, low_count, medium_count, high_count, critical_count)

