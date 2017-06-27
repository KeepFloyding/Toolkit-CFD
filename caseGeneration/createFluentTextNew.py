# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 13:30:21 2016

@author: ap4409

This is a python function file, that generates a scheme file that can be read by Fluent and will create a case file according 
to the specifications set in sim_config_file.py. 

The generate case file will create a zone of scalar and momentum source terms that denote the presence of a clot. 
Note that multiple clot zones can be specified in an array. 




"""


# ------------------------------------------------------------------------------
# HEADERS
# ------------------------------------------------------------------------------

import fileinput
import sys
import sim_config_file as config


def generateCaseFile():


    # ------------------------------------------------------------------------------
    # READING CONFIG FILE
    # ------------------------------------------------------------------------------

    # File details
    startName = config.File['case_name'];
    mesh_name = config.File['mesh_name'];
    CC = config.File['CC'];

    # Reading the name of each part 
    inlet_name = config.Mesh['inlet'];
    outlet_names = config.Mesh['outlet'];
    wall_names = config.Mesh['wall'];
    clot_names= config.Mesh['clot'];


    # Reading the material properties
    density = config.Materials['density'];
    viscosity = config.Materials['viscosity'];

    # User Defined Functions
    library_name = config.UDFs['library'];
    C_fileNames = config.UDFs['C_files'];
    initial_UDF = config.UDFs['UDF_ini'];
    execEnd_UDF = config.UDFs['UDF_execEnd'];
    ondemandUDF = config.UDFs['UDF_ondemand'];

    # User Defined Scalars
    scalar_indices = config.UDS['scalar_names'];
    diff_dict = config.UDS['diffusion_coefficients'];
    transport_options = config.UDS['transport_options'];
    scalar_BC = config.BCs['scalar'];


    NUM_SCALAR = len(scalar_indices);
    diff = []; scalar_options = []; concArray = [];

    for index in scalar_indices:
    
        scalar_name = scalar_indices[index];
    
        diff.append(diff_dict[scalar_name]);
        scalar_options.append(transport_options[scalar_name]);
        concArray.append(scalar_BC[scalar_name]);

    # Boundary Conditions
    UDF_inlet = config.BCs['hemo']['inlet'];
    UDF_outlet = config.BCs['hemo'];

    # Save Directory
    dir_name = config.File['dir_name'];

    # ------------------------------------------------------------------------------
    # CLEANING
    # ------------------------------------------------------------------------------

    # Source array has to list momentum and all scalar arrays
    mom_source_term =  config.mom['source'];
    scalar_source_term = config.UDS['source_terms'];
    source_array = [mom_source_term['x'],mom_source_term['y'],mom_source_term['z']];

    for index in scalar_indices:
        scalar_name = scalar_indices[index];

        source_array.append(scalar_source_term[scalar_name]);


    # ------------------------------------------------------------------------------
    # SETTING UP MESH AND MODEL 
    # ------------------------------------------------------------------------------

    text = [];

    # Creating mesh
    text.append('file/read ' + mesh_name)
    text.append('mesh/scale 0.001 0.001 0.001');

    # ------------------------------------------------------------------------------
    # UDF COMPILATION
    # ------------------------------------------------------------------------------

    # Model Set Up
    text.append('define/models/unsteady-2nd-order yes');
    text.append('define/materials/change-create air blood yes constant ' + str(density) 
    + ' no no yes constant ' +str(viscosity) +' no no no yes')

    # User defined functions
    text.append('define/user-defined/compiled-functions/compile ' + library_name + ' yes ' + ' '.join(C_fileNames))
    text.append('')
    text.append('')
    text.append('define/user-defined/compiled-functions/load ' + library_name);

    text.append('define/user-defined/function-hooks/initialization "' + initial_UDF + '::' + library_name +'"')
    text.append('')
        
    line = 'define/user-defined/function-hooks/execute-at-end ';
    for endUDF in execEnd_UDF:

        line += '"' + endUDF + '::' + library_name +'" ';
    text.append(line)
    text.append('')

    # ------------------------------------------------------------------------------
    # USER-DEFINED SCALARS/MEMORY
    # ------------------------------------------------------------------------------

    # User defined scalars
    line = 'define/user-defined/user-defined-scalars ' + str(NUM_SCALAR) + ' yes no ';

    for scalar in scalar_options:
        
        line += ' yes ' + scalar;

    text.append(line)

    # Scalar Diffusion
    line = 'define/materials/change-create blood blood no no no no no no yes defined-per-uds '

    for it in range(NUM_SCALAR-1):

        line += str(it) + ' constant ' + str(diff[it]) + ' '; 

    line += '-1 no'    

    text.append(line)

    # User defined memory
    text.append('define/user-defined/user-defined-memory 20')
    text.append('define/user-defined/user-defined-node-memory 20')

    # ------------------------------------------------------------------------------
    # BOUNDARY CONDITIONS
    # ------------------------------------------------------------------------------

    # Inlet
    line = 'define/boundary-conditions/velocity-inlet ' + inlet_name + ' no no yes yes yes yes "udf" "' + UDF_inlet + '::' + library_name+ '" no 0 '
    for conc in concArray:
        
        line += 'no yes '
        
    #line = line[0:len(line)-3]
    for conc in concArray:
        
        if type(conc) == str:
            line += 'yes yes "udf" "' + conc + '::' + library_name+ '" '; 

        else:

            line += 'no ' + str(conc) + ' ';

    text.append(line);

    # Outlets
    for outlet in outlet_names:
        
        text.append('define/boundary-conditions/pressure-outlet ' + outlet + ' yes yes "udf" "' 
        + UDF_outlet[outlet]  + '::' + library_name+ '" no yes ' 
        + 'yes '*len(concArray) + 'no 0 '*len(concArray) + 'no no no')
        
    # ------------------------------------------------------------------------------
    # CELL-ZONE CONDITIONS
    # ------------------------------------------------------------------------------

    # Cell Zone Conditions
    line = 'define/boundary-conditions/fluid ' + clot_names[0] + ' no yes 0'

    for source_UDF in source_array:
        line += ' 1 no yes "' + source_UDF + '::' + library_name + '"';


    line += 'no no no 0 no 0 no 0 no 0 no 0 no 1 no no no';

    text.append(line)

    if len(clot_names) > 1:
        
        line = 'define/boundary-conditions/copy-bc';
        
        for clot in clot_names:
            line += ' ' + clot;
            
        text.append(line);
        text.append('');
        
    # ------------------------------------------------------------------------------
    # SOLUTION METHODS/CONTROLS
    # ------------------------------------------------------------------------------

    # Solution Methods/ Solution Controls (URFs) 
    text.append('solve/set/discretization-scheme/pressure 14') # PRESTO Scheme

    for num in range(NUM_SCALAR-1):
        
        text.append('solve/set/discretization-scheme/uds-'+ str(num) + ' 1') # 2nd order Scheme
        text.append('solve/set/under-relaxation/uds-'+ str(num) + ' 0.7') # Under relaxation factor
        

    # ------------------------------------------------------------------------------
    # MONITORING
    # ------------------------------------------------------------------------------

    # Residuals
    text.append('solve/monitors/residual/convergence-criteria ' + (str(CC)+' ')*(NUM_SCALAR + 3))

    # ------------------------------------------------------------------------------
    # SCHEME PROGRAMMING, FIND ZONE NAMES
    # ------------------------------------------------------------------------------

    # Find zone IDS
    text.append("(rp-var-define 'a () 'list #f)")
    text.append("(rpsetvar 'a ())")
    text.append("(for-each (lambda (t) (rpsetvar 'a (list-add")
    text.append("(rpgetvar 'a) (thread-id t))))")
    text.append("(get-all-threads))")
    text.append("(rpgetvar 'a)")

    # Find zone names
    text.append("(rp-var-define 'b () 'list #f)")
    text.append("(rpsetvar 'b ())")
    text.append("(for-each (lambda (t) (rpsetvar 'b (list-add")
    text.append("(rpgetvar 'b) (thread-name t))))")
    text.append("(get-all-threads))")
    text.append("(rpgetvar 'b)")
        
    # ------------------------------------------------------------------------------
    # SOLUTION INITIALISATION
    # ------------------------------------------------------------------------------

    # Solution Initialisation
    text.append('define/user-defined/execute-on-demand "' + ondemandUDF + '::' + library_name + '"')
    text.append('solve/initialize/set-defaults/uds-2 2.2');
    text.append('solve/initialize/set-defaults/uds-8 1.0');
    text.append('/solve/initialize/initialize-flow ok');
        
    # Calculation Activities
    text.append('file/auto-save/append-file-name-with flow-time 6');
    text.append('file/auto-save/root-name ' + dir_name);

    # ------------------------------------------------------------------------------
    # SAVING CASE/DATA FILE
    # ------------------------------------------------------------------------------

    # Saving Case and File
    text.append('file/write-case-data ' + startName + '.cas');
    text.append('file/confirm-overwrite yes');

    # ------------------------------------------------------------------------------
    # WRITING FILE
    # ------------------------------------------------------------------------------

    text_file = open(startName + ".jou", "w");

    for line in text:
        text_file.write(line+'\n');
        
        
    text_file.close()



   
