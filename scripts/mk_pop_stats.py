#!/usr/bin/python2
"""
OVERVIEW:
This script makes population statistics csv files from Avida analysis data.
OUTPUT:
 -- pop stats csv that details various statistics about each population it analyzes
   * treatment, replicate, update, environment
   * population_size
   * genotype diversity (shannon diversity index for genotypes)
   * phenotype counts for each possible phenotype encoding
"""
import json, os
import utilities.parse_avida_output as parse_utils
from utilities.utilities import mkdir_p, binary, shannon_diversity

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
    settings_fn = "param/ss_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    dump_loc = os.path.join(experiment_loc, settings["experiment_data"]["script_analysis_dump"])
    pull_loc = os.path.join(experiment_loc, settings["experiment_data"]["avida_analysis_dump"])
    # Pull out some other relevant settings
    treatments_to_process = settings["processing_config"]["treatments_to_process"]
    treatment_configs = settings["treatment_configs"]
    # This will contain compiled pop stats, which will only look good if all treatments have the same possible list of phenotypes
    # Build list of all possible phenotypes for this treatment
    phenotype_table = [binary(i, 4).split("b")[-1] for i in range(0, len(settings["treatment_configs"]["shared_config"]["phenotype_encoding"])**2)]
    compiled_pop_stats_csv_content = "treatment,replicate,update,environment,population_size,genotype_diversity,%s\n" % ",".join(phenotype_table)
    with open(os.path.join(dump_loc, "compiled_pop_stats.csv"), "w") as fp:
        fp.write(compiled_pop_stats_csv_content)
    compiled_pop_stats_csv_content = ""
    # Rummage through the data!
    for treatment in treatments_to_process:
        print "Processing: " + treatment
        # We want to push data from the dump_loc
        treatment_dump = os.path.join(dump_loc, treatment)
        mkdir_p(treatment_dump)
        # Get all of the reps for this treatment.
        reps = [r for r in os.listdir(pull_loc) if (treatment in r) and ("__rep_" in r)]
        # Define treatment specs and inherited specs, we'll use a helper function to access them.
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
        #################
        # Here's where we start to do some processing
        ########
        # Build the environment reference for this treatment
        env_ref = _generate_environment_reference(_get_treatment_param("environments"),
                                                  _get_treatment_param("cycle_length"),
                                                  _get_treatment_param("total_updates"))
        # Build list of all possible phenotypes for this treatment
        phenotype_table = [binary(i, 4).split("b")[-1] for i in range(0, len(_get_treatment_param("phenotype_encoding"))**2)]
        print ("I'll be looking at these phenotypes for this treatment: " + str(phenotype_table))
        # This will hold the csv content for population stats
        treat_pop_stats_csv_content = "treatment,replicate,update,environment,population_size,genotype_diversity,%s\n" % ",".join(phenotype_table)
        with open(os.path.join(treatment_dump, "pop_stats.csv"), "w") as fp:
            fp.write(treat_pop_stats_csv_content)
        treat_pop_stats_csv_content = ""
        write_cntr = 0
        # Rummage through the reps!
        for rep in reps:
            print "Processing rep: " + str(rep)
            rep_id = rep.split("__rep_")[-1]
            rep_loc = os.path.join(pull_loc, rep)
            # Grab all of the population slices
            pops = [pname for pname in os.listdir(rep_loc) if os.path.isdir(os.path.join(rep_loc, pname)) and "pop_" in pname]
            print "Here are all of the pops: " + str(pops)
            pops.sort()
            updates = []
            # Do some work on each population
            for pop in pops:
                print "Processing pop: " + str(pop)
                pop_in = os.path.join(rep_loc, pop)
                # Grab this population's update
                update = pop.split("_")[-1]
                updates.append(update)
                # Initialize population stats
                pop_stats = {phenotype_table[i]:0 for i in range(0, len(phenotype_table))}
                pop_stats["population_size"] = 0
                pop_stats["genotype_shannon_diversity"] = 0
                # Pull in population data by environment
                population_x_env = {}
                for env in _get_treatment_param("environments"):
                    env_in = os.path.join(pop_in, "env__" + env)
                    det_file = "pop_detail.dat"
                    with open(os.path.join(env_in, det_file)) as fp:
                        population_x_env[env] = parse_utils.detail_file_extract(fp)
                # Let's take a look at the information we pulled in
                oids = population_x_env[_get_treatment_param("environments")[-1]].keys()
                genotype_cnts = {}  # We'll use this to calculate shannon diversity index for genotypes
                # For each organism in the population
                for oid in oids:
                    oid_x_env = {env:population_x_env[env][oid] for env in population_x_env.keys()}
                    encoding = _get_treatment_param("phenotype_encoding")
                    phenotype = _encode_phenotype(oid_x_env, encoding)
                    num_cpus = int(oid_x_env[_get_treatment_param("environments")[-1]]["number of cpus"])
                    pop_stats[''.join(map(str, phenotype))] += num_cpus
                    pop_stats["population_size"] += num_cpus
                    genotype_cnts[oid] = num_cpus
                # Calculate shannon diversity index
                pop_stats["genotype_shannon_diversity"] = shannon_diversity(genotype_cnts.values())
                # Add line to treatment csv for this population slice
                #    "treatment,replicate,update,population_size,diversity,[phenotypes]"
                treat_pop_stats_csv_content += "%s,%s,%s,%s,%d,%f,%s\n" % (treatment, rep_id, update, env_ref[int(update)], pop_stats["population_size"], pop_stats["genotype_shannon_diversity"], ",".join([str(pop_stats[ptype]) for ptype in phenotype_table]))
                compiled_pop_stats_csv_content += "%s,%s,%s,%s,%d,%f,%s\n" % (treatment, rep_id, update, env_ref[int(update)], pop_stats["population_size"], pop_stats["genotype_shannon_diversity"], ",".join([str(pop_stats[ptype]) for ptype in phenotype_table]))
                if write_cntr >= 5:
                    with open(os.path.join(treatment_dump, "pop_stats.csv"), "a") as fp:
                        fp.write(treat_pop_stats_csv_content)
                    with open(os.path.join(dump_loc, "compiled_pop_stats.csv"), "a") as fp:
                        fp.write(compiled_pop_stats_csv_content)
                    treat_pop_stats_csv_content = ""
                    compiled_pop_stats_csv_content = ""
                    write_cntr = 0
                write_cntr += 1
        # Write out our pop stats file
        with open(os.path.join(treatment_dump, "pop_stats.csv"), "a") as fp:
            fp.write(treat_pop_stats_csv_content)
        with open(os.path.join(dump_loc, "compiled_pop_stats.csv"), "a") as fp:
            fp.write(compiled_pop_stats_csv_content)
        compiled_pop_stats_csv_content = ""
    with open(os.path.join(dump_loc, "compiled_pop_stats.csv"), "a") as fp:
        fp.write(compiled_pop_stats_csv_content)


if __name__ == "__main__":
    main()
