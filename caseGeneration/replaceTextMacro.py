import sim_config_file as config
import fileinput
import sys

# Function to replace text

def replaceText(file,searchExp,replaceExp):
	for line in fileinput.input(file, inplace=1):
		if searchExp in line:
			line = line.replace(line,searchExp + ' ' + replaceExp + '\n')
		sys.stdout.write(line)

# ------------------------------------------------------------------------------
# REPLACING NAMES IN C FILES 
# ------------------------------------------------------------------------------

# Inputs from config file

ini_UDF_file = config.UDFs['fileName_UDF_ini'];
outlet_UDF_file = config.UDFs['fileName_UDF_outlet'];
clot_names = config.Mesh['clot'];

outlet_names = config.Mesh['outlet'];
outlet_text_replace = config.BCs['text_replace'];


# Windkessel file (replaces the name of the outlet in the C-file with the outlet names specified in sim_config_file

for outlet in outlet_names:
	replaceText(outlet_UDF_file,outlet_text_replace[outlet],'"' + outlet + '"')

# Clot Initialisation File (adds in all of the names of the clot zones to the initialisation C file)

clot_line = '{"' + '","'.join(clot_names) + '"};';
replaceText(ini_UDF_file,'char *clot_name[] =',clot_line)















