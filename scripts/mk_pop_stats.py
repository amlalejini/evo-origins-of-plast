#!/usr/bin/python2
"""
This script makes population statistics csv files from Avida analysis data.
"""
import json, os
import utilities.parse_avida_output as parse_utils
from utilities.utilities import mkdir_p, binary

def _encode_phenotype(organism_x_environment, encoding):
    """
    Given org X environment dictionary and an encoding scheme (specified in settings file),
     return the encoded phenotype.
    """
    phenotype = []
    for i in range(0, len(encoding)):
        trait = None
        env = encoding[i]["env"]
        task = encoding[i]["task"]
        trait = int(int(organism_x_environment[env][task]) != 0)
        phenotype.append(trait)
    return phenotype

def _generate_environment_reference(environments, cycle_length, updates):
    """
    Given a list of cyclic environments (in order of encountered) and the cycle length,
     this function will construct a reference array that indicates the environment at any given point in time.
    """
    envs = [None for u in range(0, updates + 1)]
    eid = 0
    cu = 0
    for u in range(0, updates + 1):
        if (cu >= cycle_length):
            cu = 0
            eid = (eid + 1) % len(environments)
        envs[u] = environments[eid]
        cu += 1
    return envs

def main():
    """
    This script makes population stats csv files.
    """
    settings_fn = "param/stepping_stones_settings.json"
    settings = None

    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    dump_loc = settings["experiment_data"]["script_analysis_dump"]
    pull_loc = settings["experiment_data"]["avida_analysis_dump"]
    # Pull out some other relevant settings
    experiment_treatments = settings["experiment_data"]["treatments"]
    treat_configs = settings["treatment_configs"]
    # Rummage through the data!
    for treatment in experiment_treatments:
        print treatment
        # Load up treat's config
        treat_config = treat_configs[treatment]
        # Build environment reference
        env_ref = _generate_environment_reference(treat_config["environments"], treat_config["cycle_length"], treat_config["total_updates"])
        # We want to pull data from the pull_loc
        treat_in = os.path.join(experiment_loc, treatment, pull_loc)
        # We want to push data from the dump_loc
        treat_out = os.path.join(experiment_loc, treatment, dump_loc)
        # Grap all of the reps
        reps = [rname for rname in os.listdir(treat_in) if os.path.isdir(os.path.join(treat_in, rname))]
        # Build list of all possible phenotypes for this treatment
        phenotype_table = [binary(i, 4).split("b")[-1] for i in range(0, len(treat_config["phenotype_encoding"])**2)]
        print ("I'll be looking at these phenotypes: " + str(phenotype_table))
        # This will hold the csv content for population stats
        treat_pop_stats_csv_content = "treatment,replicate,update,environment,population_size,%s\n" % ",".join(phenotype_table)
        with open(os.path.join(treat_out, "pop_stats.csv"), "w") as fp:
            fp.write(treat_pop_stats_csv_content)
        treat_pop_stats_csv_content = ""
        write_cntr = 0
        # Rummage through the reps!
        for rep in reps:
            print rep
            rep_in = os.path.join(treat_in, rep)
            rep_out = os.path.join(treat_out, rep)
            # Grab all of the population slices
            pops = [pname for pname in os.listdir(rep_in) if os.path.isdir(os.path.join(rep_in, pname))]
            pops.sort()
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
                    env_in = os.path.join(pop_in, env)
                    det_file = "pop_detail.dat"
                    with open(os.path.join(env_in, det_file)) as fp:
                        population_x_env[env] = parse_utils.detail_file_extract(fp)
                # Let's take a look at the information we pulled in
                oids = population_x_env[treat_config["environments"][-1]].keys()
                for oid in oids:
                    oid_x_env = {env:population_x_env[env][oid] for env in population_x_env.keys()}
                    encoding = treat_config["phenotype_encoding"]
                    phenotype = _encode_phenotype(oid_x_env, encoding)
                    num_cpus = int(oid_x_env[treat_config["environments"][-1]]["Number of CPUs"])
                    pop_stats[''.join(map(str, phenotype))] += num_cpus
                    pop_stats["population_size"] += num_cpus
                # Add line to treatment csv for this population slice
                #    "treatment,replicate,update,population_size,[phenotypes]"
                treat_pop_stats_csv_content += "%s,%s,%s,%s,%d,%s\n" % (treatment, rep, update, env_ref[int(update)], pop_stats["population_size"], ",".join([str(pop_stats[ptype]) for ptype in phenotype_table]))
                if write_cntr >= 5:
                    with open(os.path.join(treat_out, "pop_stats.csv"), "a") as fp:
                        fp.write(treat_pop_stats_csv_content)
                    treat_pop_stats_csv_content = ""
                    write_cntr = 0
                write_cntr += 1
        # Make sure treat_out exists. If not, create it.
        mkdir_p(treat_out)
        # Write out our pop stats file
        with open(os.path.join(treat_out, "pop_stats.csv"), "a") as fp:
            fp.write(treat_pop_stats_csv_content)

if __name__ == "__main__":
    main()
