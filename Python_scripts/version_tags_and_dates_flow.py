import requests

VERSION_RESULTS_DIR = "version_dict_file.txt"
VERSION_RELEASE_DIR = "version_release_dict.txt"

version_dict = {}
version_release_dict = {}


def get_version_tags():
    # repository_list = ["alpine", "nginx", "ubuntu", "redis", "postgres", "node", "httpd", "memcached", "python", "mongo",
    #                     "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby",
    #                     "haproxy", "tomcat", "kong", "neo4j", "amazonlinux", "caddy", "bash", "gradle", "plone", "fedora",
    #                     "groovy", "rust", "redmine", "amazoncorretto", "erlang", "elixir", "jruby", "jetty", "odoo", "xwiki",
    #                     "swift", "hylang", "archlinux", "tomee", "gcc", "monica", "varnish","orientdb", "julia"]

    repository_list = ["odoo", "neo4j", "orientdb", "plone", "ubuntu", "Alpine"]

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
                print(type(string_tag_info))
                print(string_tag_info)
                # Check if the tag is for Linux (amd64)
                if 'linux' or 'arm' or 'amd64' in string_tag_info:
                    last_updated = tag_info["last_updated"]
                    # just_version_date = last_updated.split('T')[0]
                    print(last_updated)
                    version_release_dict[image].append("{0}, {1}".format(tag_name, last_updated))
                    version_dict[image].append(tag_name)


                    # print(f"Image_Name: {image}, Tag: {tag_name}, Last Updated: {last_updated}")
        else:
            print(f"Failed to retrieve tags for {image}. Status code: {response.status_code}")

# def get_oldest_if_duplicates():
#     """
#     Getting the oldest version on a day if multiple are put out in a day 
#     """
#     for image_name in version_dict.keys():
#         for the_image_name, version_list in version_dict.keys():
#             if image_name == the_image_name:



def write_version_release_dict_to_file(file_path):
    """
    Writes the dicts to text files so they can be used by the pipeline
    """        
    with open(file_path, 'w') as file:
        for key, value in version_release_dict.items():
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
    print("version_release_dict".format(version_release_dict))  
    print("version_dict".format(version_dict))

    # get_oldest_if_duplicates()
    write_version_release_dict_to_file(VERSION_RELEASE_DIR)
    write_version_dict_to_file(VERSION_RESULTS_DIR)