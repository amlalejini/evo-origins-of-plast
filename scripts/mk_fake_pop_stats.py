#!/usr/bin/python2
"""
This script makes fake population statistics csv files. Strictly used for testing visualization tools.
"""
import random, math, json

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
    Main script functionality.
    """
    settings_fn = "param/settings.json"
    settings = None
    with open(settings_fn) as fp:
        settings = json.load(fp)

    print("Generating fake population stats.")
    treatments = ["io-sense-only"]
    replicates = ["single_runs_1"]
    phenotypes = ["0000","0001","0010","0011","0100","0101","0110","0111","1000","1001","1010","1011","1100","1101","1110","1111"]
    num_pops = 10
    step_size = 100
    fake_csv = "treatment,replicate,update,environment,population_size,%s\n" % ",".join(phenotypes)
    for treatment in treatments:
        treat_config = settings["treatment_configs"][treatment]
        env_ref = _generate_environment_reference(treat_config["environments"], treat_config["cycle_length"], treat_config["total_updates"])
        for replicate in replicates:
            cur_update = 0
            for n in range(0, num_pops):
                pop_size = 3600
                pvals = []
                for phenotype in phenotypes:
                    pvals.append(abs(math.sin(random.uniform(-1, 1))))
                # normalize everything to sum up to 3600
                tot = sum(pvals)
                normpvals = [int((val / float(tot)) * pop_size) for val in pvals]
                pop_size = sum(normpvals)
                # treatment, rep, update, popsize, phenotypes
                fake_csv += "%s,%s,%s,%s,%s,%s\n" % (treatment, replicate, str(cur_update), env_ref[cur_update], str(pop_size), ",".join(map(str, normpvals)))
                cur_update += step_size

    with open("fake_pop_stats.csv", "w") as fp:
        fp.write(fake_csv)


if __name__ == "__main__":
    main()
