#!/usr/bin/python2
"""
This script will run avida in analysis mode for each treatment and each avida analysis script specified in the
 param/settings.json file.

Once running avida analyze mode for treatment, this script will move the data dumped (dumped in the config location)
 to the specified analysis dump location.
"""
import json, os, subprocess

def main():
    """
    Main script
    """
    settings_fn = "param/ss200_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    configs_loc = settings["avida_analysis_config"]["avida_configs_loc"]
    analysis_scripts_src = settings["avida_analysis_config"]["analysis_scripts_source"]
    # Pull out some other settings
    treats_to_analyze = settings["avida_analysis_config"]["treatments_to_analyze"]
    analyses = settings["avida_analysis_config"]["analysis_scripts_to_run"]

    # Read run_list file for run settings for args by treatment
    avida_cmd_args = None
    with open(os.path.join(configs_loc, "run_list"), "r") as fp:
        avida_cmd_args = {line.split(" ")[1].split("__")[0]:line.split("./avida")[-1].replace("-s $seed ", "").strip() for line in fp if "./avida" in line}

    for treatment in treats_to_analyze:
        print "Analyzing %s" % treatment
        # First, define treatment specs and inherited specs
        TSPEC = settings["treatment_configs"][treatment]
        ISPEC = settings["treatment_configs"][settings["treatment_configs"][treatment]["inherit_from"]]
        def _get_treatment_param(setting = None):
            """
            useful helper function for getting the correct parameter value
            """
            if setting in TSPEC.keys():
                return TSPEC[setting]
            elif setting in ISPEC.keys():
                return ISPEC[setting]
            else:
                return None
        # Make and run each analysis script specified in settings file
        for ascript in analyses:
            print "  Running %s" % ascript
            ascript_fpath = os.path.join(analysis_scripts_src, ascript)
            ## BUILD ANALYSIS FILE ##
            modified_ascript = ""
            ascript_content = ""
            with open(ascript_fpath, "r") as fp:
                for line in fp:
                    if line.strip() == "SET d":
                        modified_ascript += "SET d %s\n" % experiment_loc
                    elif line.strip() == "FOREACH t":
                        modified_ascript += "FOREACH t %s\n" % treatment
                    elif line.strip() == "SET s":
                        modified_ascript += "SET s %d\n" % _get_treatment_param("replicates_begin-end")[0]
                    elif line.strip() == "SET f":
                        modified_ascript += "SET f %d\n" % _get_treatment_param("replicates_begin-end")[1]
                    else:
                        modified_ascript += line
            ## WRITE ANALYSIS FILE TO RUN LOCATION ##
            with open(os.path.join(configs_loc, ascript), "w") as fp:
                fp.write(modified_ascript)
            ## BUILD ANALYSIS COMMAND ##
            cmd = "./avida %s -a -set ANALYZE_FILE %s" % (avida_cmd_args[treatment], ascript)
            ## RUN AVIDA ANALYSIS ##
            #print cmd
            #subprocess.call("pwd", shell = True, cwd = configs_loc)
            return_code = subprocess.call(cmd, shell = True, cwd = configs_loc)
            ## CLEAN UP ANALYSIS SCRIPT ##
            return_code = subprocess.call("rm %s" % ascript, shell = True, cwd = configs_loc)

if __name__ == "__main__":
    main()
