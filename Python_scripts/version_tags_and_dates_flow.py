import requests
from datetime import datetime , timezone
from collections import defaultdict

VERSION_RESULTS_DIR = "version_dict_file.txt"
VERSION_RELEASE_DIR = "version_release_dict.txt"
OLDEST_VERSION_FILE_NAME = "oldest_versions.txt"

version_dict = {}
version_release_dict = {}
oldest_for_date_dict = {}



def get_version_tags():
    # repository_list = ["alpine", "nginx", "ubuntu", "redis", "postgres", "node", "httpd", "memcached", "python", "mongo",
    #                     "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby",
    #                     "haproxy", "tomcat", "kong", "neo4j", "amazonlinux", "caddy", "bash", "gradle", "plone", "fedora",
    #                     "groovy", "rust", "redmine", "amazoncorretto", "erlang", "elixir", "jruby", "jetty", "odoo", "xwiki",
    #                     "swift", "hylang", "archlinux", "tomee", "gcc", "monica", "varnish","orientdb", "julia"]

# "orientdb", "plone", "ubuntu", "alpine"
    repository_list = ["odoo", "neo4j"]

    # Make a GET request to the Docker Hub API
    for image in repository_list:
        tags_url = f"https://hub.docker.com/v2/repositories/library/{image}/tags/"
        response = requests.get(tags_url)
        version_dict[image] = []
        version_release_dict[image] = []

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            # Extract and print the tags and last updated dates for Linux images
            for tag_info in results:
                tag_name = tag_info["name"]
                # print(tag_info)
                string_tag_info = str(tag_info)
                # print(type(string_tag_info))
                # print(string_tag_info)
                # Check if the tag is for Linux (amd64)
                if 'linux' or 'arm' or 'amd64' in string_tag_info:
                    last_updated = tag_info["last_updated"]
                    # just_version_date = last_updated.split('T')[0]
                    # print(last_updated)
                    version_release_dict[image].append("{0}, {1}".format(tag_name, last_updated))
                    version_dict[image].append(tag_name)


                    # print(f"Image_Name: {image}, Tag: {tag_name}, Last Updated: {last_updated}")
        else:
            print(f"Failed to retrieve tags for {image}. Status code: {response.status_code}")
    print("version_release_dict {0}".format(version_release_dict))  
    print("version_dict {0}".format(version_dict))

def get_oldest_if_duplicates():
    """
    Function gets the oldest image for each date 
    """

    for image, releases in version_release_dict.items():
        for item in releases:
            version, mydatetime = item.split(', ')
            date, time = mydatetime.split('T')
            
            # Truncate milliseconds and convert to datetime
            time_without_ms = time.split('.')[0]  # Remove milliseconds
            datetime_obj = datetime.fromisoformat(f'{date}T{time_without_ms}').replace(tzinfo=timezone.utc)

            # Ensure that each date has an associated dictionary
            if date not in oldest_for_date_dict:
                oldest_for_date_dict[date] = {}

            if image not in oldest_for_date_dict[date] or datetime_obj < datetime.fromisoformat(oldest_for_date_dict[date][image].split(', ')[1]).replace(tzinfo=timezone.utc):
                oldest_for_date_dict[date][image] = f'{version}, {mydatetime}'


def write_oldest_for_date_dict(file_path):
    """
    Writes the dicts to text files so they can be used by the pipeline
    """
    with open(file_path, 'w') as file:
        for key, value in version_release_dict.items():
            file.write(f'{key}: {value}\n')


def write_version_release_dict_to_file(file_path):
    """
    Writes the dicts to text files so they can be used by the pipeline
    """        
    with open(file_path, 'w') as file:
        for key, value in oldest_for_date_dict.items():
            file.write(f'{key}: {value}\n')


def write_version_dict_to_file(file_path):
    """
    Writes the dicts to text files so they can be used by the pipeline
    """        
    with open(file_path, 'w') as file:
        for key, value in version_dict.items():
            file.write(f'{key}: {value}\n')

def execute_flow():
    """
    This is the main function that will call every other function
    """
    get_version_tags()

    get_oldest_if_duplicates()
    write_oldest_for_date_dict(OLDEST_VERSION_FILE_NAME)
    write_version_release_dict_to_file(VERSION_RELEASE_DIR)
    write_version_dict_to_file(VERSION_RESULTS_DIR)