# Example how to use aps toolbox scripts
# The aps code is included in the plugin file and is unpacked before
# using the aps toolbox scripts.


from aps.toolbox import name_of_help_script
from aps.utils.constants.simple import Debug

# Define input parameters in dictionary.
# Specification depends on which aps script is choosen.
params = {
    'project': project,
    'debug_level': Debug.VERBOSE,
    # Fill in parameters for the script
}

name_of_help_script.run(params)
