import requests

VERSION_RESULTS_DIR = "version_dict_file.txt"
VERSION_RELEASE_DIR = "version_release_dict.txt"

version_dict = {}
version_release_dict = {}


def get_version_tags():
    repository_list = ["alpine", "nginx", "ubuntu", "python", "redis", "postgres", "node", "httpd", "memcached", "mongo",
                        "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby",
                          "haproxy", "tomcat", "kong", "neo4j", "amazonlinux", "caddy", "bash", "gradle", "logstash", "fedora",
                          "groovy", "rust", "redmine", "amazoncorretto", "erlang", "elixir", "jruby", "jetty", "odoo", "xwiki",
                          "swift", "haxe", "hylang", "archlinux", "tomee", "gcc", "monica", "varnish","orientdb", "julia"] 
    
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

            # Extract and print the tags and last updated dates
            for tag_info in results:
                tag_name = tag_info["name"]
                last_updated = tag_info["last_updated"]
                # version_release_dict[tag_name] = last_updated
                version_release_dict[image].append("{0}, {1}".format(tag_name, last_updated))
                version_dict[image].append(tag_name)


                # print(f"Image_Name: {image}, Tag: {tag_name}, Last Updated: {last_updated}")
        
        else:
            print(f"Failed to retrieve tags. Status code: {response.status_code}")

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
    write_version_release_dict_to_file(VERSION_RELEASE_DIR)
    write_version_dict_to_file(VERSION_RESULTS_DIR)