#!/usr/bin/python2
"""
This script makes population statistics csv files from Avida analysis data.
"""
import json, os
import util.parse_avida_output as parse_utils

def binary(num, length=8):
    return format(num, '#0{}b'.format(length + 2))

def encode_phenotype(organism_x_environment, encoding):
    """
    """
    phenotype = []
    for i in range(0, len(encoding)):
        trait = None
        env = encoding[i]["env"]
        task = encoding[i]["task"]
        trait = int(int(organism_x_environment[env][task]) != 0)
        phenotype.append(trait)
    return phenotype

def main():
    """
    This script makes population stats csv files.
    """
    settings_fn = "param/settings.json"
    settings = None

    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    dump_loc = settings["experiment_data"]["script_analysis_dump"]
    pull_loc = settings["experiment_data"]["avida_analysis_dump"]
    experiment_treatments = settings["experiment_data"]["treatments"]
    treat_configs = settings["treatment_configs"]
    # Rummage through the data!
    for treatment in experiment_treatments:
        print treatment
        treat_pop_stats_csv_content = ""
        # Load up treat's config
        treat_config = treat_configs[treatment]
        # We want to pull data from the pull_loc
        treat_in = os.path.join(experiment_loc, treatment, pull_loc)
        # We want to push data from the dump_loc
        treat_out = os.path.join(experiment_loc, treatment, dump_loc)
        # Grap all of the reps
        reps = [rname for rname in os.listdir(treat_in) if os.path.isdir(os.path.join(treat_in, rname))]
        # Build list of all possible phenotypes for this treatment
        phenotype_table = [binary(i, 4).split("b")[-1] for i in range(0, len(treat_config["phenotype_encoding"])**2)]
        print ("I'll be looking at these phenotypes: " + str(phenotype_table))
        # Rummage through the reps!
        for rep in reps:
            print rep
            rep_in = os.path.join(treat_in, rep)
            rep_out = os.path.join(treat_out, rep)
            # Grab all of the population slices
            pops = [pname for pname in os.listdir(rep_in) if os.path.isdir(os.path.join(rep_in, pname))]
            updates = []
            # Do some work on each population
            for pop in pops:
                print pop
                pop_in = os.path.join(rep_in, pop)
                pop_out = os.path.join(rep_out, pop)
                # Grab this population's update
                update = pop.split("_")[-1]
                updates.append(update)
                # Initialize population stats
                pop_stats = {phenotype_table[i]:0 for i in range(0, len(phenotype_table))}
                pop_stats["population_size"] = 0
                # Pull in population data by environment
                population_x_env = {}
                for env in treat_config["environments"]:
                    det_file = "dom_" + env + "_detail.dat"
                    with open(os.path.join(pop_in, det_file)) as fp:
                        population_x_env[env] = parse_utils.detail_file_extract(fp)
                # Let's take a look at the information we pulled in
                oids = population_x_env[treat_config["environments"][-1]].keys()
                for oid in oids:
                    oid_x_env = {env:population_x_env[env][oid] for env in population_x_env.keys()}
                    encoding = treat_config["phenotype_encoding"]
                    phenotype = encode_phenotype(oid_x_env, encoding)
                    num_cpus = int(oid_x_env[treat_config["environments"][-1]]["Number of CPUs"])
                    pop_stats[''.join(map(str, phenotype))] += num_cpus
                    pop_stats["population_size"] += num_cpus
                # Add line to rep csv file for this population slice
                # Add line to treatment csv for this population slice
                #"treatment,replicate,update,population_size,[phenotypes]"

if __name__ == "__main__":
    main()
