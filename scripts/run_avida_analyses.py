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
    settings_fn = "param/settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    treats_configs_loc = settings["avida_analysis_config"]["configs_loc"]
    # Pull out some other settings
    treats_to_analyze = settings["avida_analysis_config"]["treatments_to_analyze"]
    analyses = settings["avida_analysis_config"]["analysis_scripts_to_run"]

    for treatment in treats_to_analyze:
        print "Analyzing %s" % treatment
        treat_config = os.path.join(treats_configs_loc, treatment)
        for ascript in analyses:
            print "  Running %s" % ascript
            return_code = subprocess.call("pwd", shell = True, cwd = treat_config)
            # Build avida analyze command and run it
            cmd = "./avida -set ANALYZE_FILE %s -a" % ascript
            return_code = subprocess.call(cmd, shell = True, cwd = treat_config)
            # Move analyze files to destination
            # mv treatment_config/data/analysis base_location/treatment
            src = os.path.join(treat_config, "data", "analysis")
            dest = os.path.join(experiment_loc, treatment)
            cmd = "rsync -r %s %s" % (src, dest)
            return_code = subprocess.call(cmd, shell = True, cwd = treat_config)
            # remove crusty data
            return_code = subprocess.call("rm -rf %s" % src, shell = True, cwd = treat_config)

if __name__ == "__main__":
    main()
