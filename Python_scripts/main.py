import sys
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the module directory to sys.path
module_dir = os.path.join(script_dir, 'Python_scripts')
sys.path.append(module_dir)

# Now you should be able to import the module
from version_tags_and_dates_flow import execute_flow

def main():
    execute_flow()

if __name__ == "__main__":
    main()
