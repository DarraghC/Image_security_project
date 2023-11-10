import re 
import json
import ast
import csv
import glob

#TODO These need to be tested 
IMAGE_NAME_PATTERN = r"'([^']+):latest'"
VERSION_PATTERN = r'{0}:(\S+)'
RESULTS_PATTERN = '"Vulnerabilities": \[(.*?)\]'

TRIVY_DIR_PATH = "trivy-reports"
CSV_FILE_PATH = "csv-data/project_data.csv"


VERSION_RESULTS_DIR = "version_dict_file.txt"
VERSION_RELEASE_DIR = "version_release_dict.txt"


version_dict = {}
image_list = ["alpine", "nginx", "ubuntu", "python", "redis", "postgres", "node", "httpd", "memcached", "mongo", "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby", "haproxy", "tomcat", "kong", "neo4j"]
image_dicts ={}

def get_json(json_file):
    """
    :param json_file: a json file
    :type json_file: string
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        json_data_string = str(json_data)

    return json_data_string

def create_image_dicts():
    """
    
    """
    # global image_dicts
    for image in image_list:
        image_dicts[image]= []

    print("Image dict is : {0}".format(image_dicts))


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
    create_image_dicts()
    get_version_dict()
    get_version_release_dict()
    json_files_list = glob.glob(f'{TRIVY_DIR_PATH}/*.json')

    print("json_files_list {0}".format(json_files_list))

    for json_file in json_files_list:
        for image in image_list:
            if image in json_file:
                print("got here")
                json_string_data = get_json(json_file)
                print("json_string_data {0}".format(json_string_data))
                image_name, results_data = parse_string_data(json_string_data)
                print("image_name: {0}".format(image_name))
                print("image {0}".format(image))
                
                print("Get image version from dict")

                print("Get the release date for the version")

                print("results_data is : {0}".format(results_data))

                low_count, medium_count, high_count = count_error_in_results(results_data)

                if check_csv_file_empty():
                    write_headers_to_file()



    #   write_parsed_data(image_name, image_version, results_data, low_count, medium_count, high_count)

