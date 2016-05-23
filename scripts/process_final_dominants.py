#!/usr/bin/python2
from utilities.utilities import mkdir_p
from utilities.parse_avida_output import detail_file_extract
import json, os

"""
Using parameters defined in specified .json settings file, loads final dominant analysis data
 from each rep of each treatment and processes this data.

Expected output:
 * final_dom_csv
    - plastic
    - optimally plastic
    - nand cnt
    - not cnt
    - gest time
    - rep efficiency
    - genome length
    - fitness
"""
def characterize_org(org_x_env):
    """
    Given dictionary of organism by environment, return dictionary of characteristics.
     * Characteristics: plastic, optiml
     * NOTE: this function is written specifically for stepping_stones_of_plasticity data (not generalized)
    """
    # Environments: nand+not- nand-not+
    # Tasks: Nand Not
    traits = ["Nand", "Not"]
    envs = {}
    for env in org_x_env:
        envs[env] = {}
        for trait in traits:
            envs[env][trait] = int(org_x_env[env][trait])
    is_plastic = envs["nand+not-"] != envs["nand-not+"]
    nand_opt = envs["nand+not-"]["Nand"] > 0 and envs["nand-not+"]["Nand"] == 0
    not_opt = envs["nand+not-"]["Not"] == 0 and envs["nand-not+"]["Not"] > 0
    optimal = nand_opt and not_opt
    print envs
    return {"plastic": is_plastic, "optimal": optimal}


def main():
    """
    main script functionality
    """
    settings_fn = "param/stepping_stones_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    analysis_loc = settings["experiment_data"]["avida_analysis_dump"]
    dump = settings["experiment_data"]["script_analysis_dump"]
    # Pull out some other neato things
    treats_to_process = settings["analysis_processing_config"]["treatments_to_process"]
    # Create csv content
    final_dom_csv_content = "treatment,replicate,plastic,optimal\n"
    plasticity_overview_csv_content = "treatment,total_plastic,total_optimal,total\n"
    for treatment in treats_to_process:
        print "Processing %s" % treatment
        treatment_analysis_loc = os.path.join(experiment_loc, treatment, analysis_loc)
        treatment_dump = os.path.join(experiment_loc, treatment, dump)
        # Get reps
        reps = [r for r in os.listdir(treatment_analysis_loc) if "single_runs_" in r]
        total_opt = 0
        total_plastic = 0
        total = 0
        for rep in reps:
            rep_id = rep.split("_")[-1]
            rep_loc = os.path.join(treatment_analysis_loc, rep, "final_dominant")
            # Get environments
            envs = [e for e in os.listdir(rep_loc)]
            dom_by_env = {}
            for env in envs:
                fd_loc = os.path.join(rep_loc, env, "final_dom_gen.dat")
                orgs = None
                with open(fd_loc, "r") as fp:
                    orgs = detail_file_extract(fp)
                dom_by_env[env] = orgs[0]
            # Is plastic?
            char_org =  characterize_org(dom_by_env)
            plastic = char_org["plastic"]
            if plastic: total_plastic += 1
            optimal = char_org["optimal"]
            if optimal: total_opt += 1
            total += 1
            final_dom_csv_content += "%s,%s,%s,%s\n" % (treatment, rep, plastic, optimal)
        plasticity_overview_csv_content += "%s,%d,%d,%d\n" % (treatment, total_plastic, total_opt, total)
    with open(os.path.join("stats_dump", "final_dom_plasticity.csv"), "w") as fp:
        fp.write(final_dom_csv_content)
    with open(os.path.join("stats_dump", "final_dom_plasticity_overview.csv"), "w") as fp:
        fp.write(plasticity_overview_csv_content)


if __name__ == "__main__":
    main()
