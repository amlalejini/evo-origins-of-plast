#!/usr/bin/python2
from utilities.utilities import mkdir_p
import json, sys, os, shutil

"""
This module reads from main and composes a run_list file for the experiment.
"""

def main():
    """
    main script functionality
    """
    run_list_content = ""
    # Grab config specifications
    specs = None
    with open("param/ss_exp_specs.json", "r") as fp:
        specs = json.load(fp)
    # Go ahead and extract experiment name and list of treatment specifications
    experiment = specs["experiment"]
    treatments = specs["treatments"]
    local_config_src = specs["config_source_dir"] # Directory containing all relevant config files (where I'll drop the run_list)
    print "Analyzing treatments: %s" % str(treatments.keys())
    # Grab everything that belongs in the run list header
    description = "experiment: %s" % experiment
    class_pref = specs["run_list_header"]["class_pref"]
    mem_request = specs["run_list_header"]["mem_request"]
    email_when = specs["run_list_header"]["email_when"]
    email = specs["run_list_header"]["email"]
    walltime = specs["run_list_header"]["walltime"]
    config_dir = specs["run_list_header"]["config_dir"]
    dest_dir = specs["run_list_header"]["dest_dir"]
    # Create the run_list header
    run_list_header = '''set description %s
set class_pref %s
set mem_request %s
set email_when %s
set email %s
set walltime %s
set config_dir %s
set dest_dir %s

''' % (description, class_pref, mem_request, email_when, email, walltime, config_dir, dest_dir)
    run_list_body = ""
    for treatment in treatments:
        #############
        # Build run list commands for each treatment!
        ############
        # First, define treatment specs and inherited specs
        TSPEC = specs["treatments"][treatment]
        ISPEC = specs[specs["treatments"][treatment]["inherit_from"]]
        def _get_spec(spec = None):
            """
            useful helper function for getting the correct parameter value
            """
            if spec in TSPEC.keys():
                return TSPEC[spec]
            elif spec in TSPEC["-set"].keys():
                return TSPEC["-set"][spec]
            elif spec in ISPEC.keys():
                return ISPEC[spec]
            elif spec in ISPEC["-set"].keys():
                return ISPEC["-set"][spec]
            else:
                return None
        # Collect parts for this treatment's command
        start_seed = _get_spec("replicates_begin-end")[0]
        end_seed = _get_spec("replicates_begin-end")[1]
        avida_config = _get_spec("avida_config")
        # Collect args for avida
        #  - Initialize arg dictionary with shared arguments
        args = {key:ISPEC["-set"][key] for key in ISPEC["-set"]}
        #  - Then, overwrite/add where necessary with treatment-specific arguments
        for arg in TSPEC["-set"]: args[arg] = TSPEC["-set"][arg]
        # Build the arg str using collected args
        arg_str = ""
        for arg in args: arg_str += "-set %s %s " % (arg, args[arg])
        # Finally, put together the avida run command for this treatment
        name = "%s__rep" % treatment
        avida_cmd = "%d..%d %s ./avida -c %s -s $seed %s \n \n" % (start_seed, end_seed, name, avida_config, arg_str)
        run_list_body += avida_cmd
    run_list_content = run_list_header + run_list_body
    with open(os.path.join(local_config_src, "run_list"), "w") as fp:
        fp.write(run_list_content)

if __name__ == "__main__":
    main()
