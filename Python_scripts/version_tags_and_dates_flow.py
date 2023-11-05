import requests

version_dict = {}
version_release_dict = {}

def get_version_tags():
    repository_list = ["alpine", "nginx", "ubuntu", "python", "redis", "postgres", "node", "httpd", "memcached", "mongo", "mysql", "traefik", "mariadb", "docker", "rabbitmq", "golang", "wordpress", "php", "sonarqube", "ruby", "haproxy", "tomcat", "kong", "neo4j"]  # Replace with your desired repository and image name

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
    print("version_dict : {0}".format(version_dict))
    print("version_release_dict : {0}".format(version_release_dict))


def execute_flow():
    """
    This is the main function that will call every other function
    """
    get_version_tags()