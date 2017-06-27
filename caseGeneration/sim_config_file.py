
# File details
import os

File = dict(

	# Name of the case file (as taken from the generateAll.csh file)
	case_name = os.environ["file_name"],

	# Mesh name
	mesh_name = 'mesh1.msh',

	# Name of the save directory for data files
	dir_name = 'results/dataFile' + 'trial',

	# Simulation details
	CC = 1E-5,

)


# Geometry Parts
Mesh = dict(
	inlet = 'inlet',
	outlet = ['mca_1_outlet','mca_2_outlet','aca_outlet'],
	clot = ['clot1','clot2'],
    	wall = ['wall','clot_wall','ext_mca_1','ext_mca_2','ext_aca','ext_ica'],
)

# Material Properties
Materials = dict(
    density = 1060,
    viscosity = 3.5E-3,
)

# Details regarding user defined functions (UDFs)

UDFs = dict(
     library =  'libudf',
     C_files = ['flowAt0p1007.c','windkessel_2_MCA_outlet.c','Initialise_clot_domain_Nov_2016.c','lysisKineticsSlowx1.c','Mom_source_term_Feb_2016_change.c','calculateVars.c','tPA_inject_UDF.c'],
     UDF_ini = 'initialise_clot_domain',
     UDF_execEnd = ['execute','calcVar','calculate_tPA_injection'],
     UDF_ondemand = 'variable_initialization',
     fileName_UDF_outlet = 'windkessel_2_MCA_outlet.c',
     fileName_UDF_ini = 'Initialise_clot_domain_Nov_2016.c', 
)

# Details regarding user defined scalars (UDSs)

UDS = dict(

    # Scalar names along with their ordering
    scalar_names = {0: 'free_tPA',
	  	    1: 'bound_tPA',
                    2: 'free_PLG', 
	            3: 'bound_PLG',
		    4: 'free_PLS',
		    5: 'bound_PLS',
		    6: 'L_PLS',
	            7: 'n_tot',
	            8: 'AP'},

    # Transport options for each scalar (mass flow rate for convection or none)
    transport_options = { 'free_tPA': '"mass flow rate" "default"',
		   	  'bound_tPA': '"none" "default"',
		   	  'free_PLG': '"mass flow rate" "default"',
		   	  'bound_PLG': '"none" "default"',
                   	  'free_PLS': '"mass flow rate" "default"',
                   	  'bound_PLS': '"none" "default"',
                   	  'L_PLS': '"none" "default"',
                   	  'n_tot': '"none" "default"',
                   	  'AP': '"mass flow rate" "default"'},

     # Name of the source UDF terms for each scalar 
     source_terms = {'free_tPA': 'free_tPA',
		     'bound_tPA': 'bound_tPA',
	             'free_PLG': 'free_PLG',
		     'bound_PLG': 'bound_PLG',
		     'free_PLS': 'free_PLS',
		     'bound_PLS': 'bound_PLS',
		     'L_PLS': 'tot_BS',
		     'n_tot':'L_PLS_woof',
		     'AP': 'AP'},

     # Diffusion coefficients (if species not in here, assumed to be zero)
    diffusion_coefficients = {'free_tPA' : 5.3E-8, 
			      'free_PLG' : 5.3E-8,
			      'free_PLS' : 5.3E-8,
			      'bound_tPA' : 0, 
			      'bound_PLG' : 0,
			      'bound_PLS' : 0,
			      'n_tot' :0,
                              'L_PLS' : 0,
			       'AP' : 5.3E-8},

)

# Details regarding boundary conditions

BCs = dict(

	# Scalar boundary conditions (value or UDF name)
	scalar = {'free_tPA':'tPA_inlet_profile',
		'bound_tPA':0,
		'free_PLG':'PLG_inlet_profile',
		'bound_PLG':0,
		'free_PLS':'PLS_inlet_profile',
		'bound_PLS': 0,
		'L_PLS': 0,
		'n_tot': 0,
		'AP': 'AP_inlet_profile'},

	# Hemodynamics boundary conditions (value or UDF name)
	hemo = {Mesh['inlet']:'flowAt0p1007',
		Mesh['outlet'][0]:'pressure',
		Mesh['outlet'][1]:'pressure',
		Mesh['outlet'][2]:'pressure'},

	# Terms to replace in text for Wibndkessel condition
	text_replace = {'mca_1_outlet':'#define MCA_OUTLET_NAME_1',
			'mca_2_outlet':'#define MCA_OUTLET_NAME_2',
			'aca_outlet':'#define ACA_OUTLET_NAME'},


)

# Details regarding momentum source terms

mom = dict(

# Name of the source terms (or none) in each direction
source = {'x':'Darcian_x',
	 'y':'Darcian_y',
	 'z':'Darcian_z'},
)




