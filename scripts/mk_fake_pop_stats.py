#!/usr/bin/python2
"""
This script makes fake population statistics csv files. Strictly used for testing visualization tools.
"""
import random, math

def main():
    """
    Main script functionality.
    """
    print("Generating fake population stats.")
    treatments = ["io-sense-only"]
    replicates = ["single_runs_1"]
    phenotypes = ["0000","0001","0010","0011","0100","0101","0110","0111","1000","1001","1010","1011","1100","1101","1110","1111"]
    num_pops = 10
    step_size = 100
    fake_csv = "treatment,replicate,update,population_size,%s\n" % ",".join(phenotypes)
    for treatment in treatments:
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
                fake_csv += "%s,%s,%s,%s,%s\n" % (treatment, replicate, str(cur_update), str(pop_size), ",".join(map(str, normpvals)))
                cur_update += step_size

    with open("fake_pop_stats.csv", "w") as fp:
        fp.write(fake_csv)


if __name__ == "__main__":
    main()
