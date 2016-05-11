#!/usr/bin/python2
"""

"""
import json, os, subprocess

def main():
    """
    Main script
    """
    settings_fn = "param/stepping_stones_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)

    dqsub_loc = settings["experiment_submission"]["dist_qsub_path"]
    experiment_loc = settings["experiment_data"]["base_location"]
    treats_to_sub = settings["experiment_submission"]["treatments_to_sub"]

    for treatment in treats_to_sub:
        print "Submitting %s" % treatment
        # find the run list for this treatment
        treat_config_loc = os.path.join(experiment_loc, treatment, "configs")
        fnames = os.listdir(treat_config_loc)
        rl_file = None
        for name in fnames:
            if "run_list" in name:
                rl_file = name
                break
        if rl_file == None:
            print("Could not find run list file")
            continue
        rl_loc = os.path.join(treat_config_loc, rl_file)
        # Run the clean up command
        cleanup = os.path.join(dqsub_loc, "cleanup.py")
        cmd = "python %s %s" % (cleanup, rl_file)
        return_code = subprocess.call(cmd, shell = True, cwd = treat_config_loc)
        print cmd
        distqsub = os.path.join(dqsub_loc, "dist_qsub.py")
        cmd = "python %s %s" % (distqsub, rl_file)
        return_code = subprocess.call(cmd, shell = True, cwd = treat_config_loc)
        print cmd

if __name__ == "__main__":
    main()
