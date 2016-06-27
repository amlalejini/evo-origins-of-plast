#!/usr/bin/python2
from utilities.utilities import mkdir_p
from utilities.parse_avida_output import detail_file_extract, extract_lineage_from_detail_file
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

def _encode_phenotype(org_x_env, encoding):
    """
    Given org X environment dictionary and an encoding scheme (specified in settings file),
     return the encoded phenotype.
    """
    abstract_phenotype = []
    full_phenotype = []
    for i in range(0, len(encoding)):
        trait = None
        env = encoding[i]["env"]
        task = encoding[i]["task"]
        abstract_trait = int(int(org_x_env[env][task]) != 0)
        full_trait = int(int(org_x_env[env][task]))
        abstract_phenotype.append(abstract_trait)
        full_phenotype.append(full_trait)
    return {"full": full_phenotype, "coded": abstract_phenotype}

def characterize_org(org_x_env, encoding):
    """
    Given dictionary of organism by environment, return dictionary of characteristics.
     * Characteristics: plastic, optiml
     * NOTE: this function is written specifically for stepping_stones_of_plasticity data (not generalized)
    """
    # Environments: nand+not- nand-not+
    # Tasks: Nand Not
    traits = ["nand", "not"]
    envs = {}
    for env in org_x_env:
        envs[env] = {}
        for trait in traits:
            envs[env][trait] = int(org_x_env[env][trait])
    is_plastic = envs["nand+not-"] != envs["nand-not+"]
    nand_opt = envs["nand+not-"]["nand"] > 0 and envs["nand-not+"]["nand"] == 0
    not_opt = envs["nand+not-"]["not"] == 0 and envs["nand-not+"]["not"] > 0
    optimal = nand_opt and not_opt
    phenotype = _encode_phenotype(org_x_env, encoding)
    return {"plastic": is_plastic, "optimal": optimal, "full_phenotype": phenotype["full"], "coded_phenotype": phenotype["coded"]}

def characterize_lineage_phenotypes(lineage_phenotype_sequence):
    """
    Given a sequence of phenotypes for a lineage, answer the following questions:
        * Unconditional trait expression before conditional trait expression?
        * Suboptimal conditional expression before optimal conditional expression?
    Optimal here means optimal regulation (no regard for counts, just for express/not express)
    Warning: This function is writen specifically for NAND+NOT-/NAND-NOT+ experiment data.
    Warning pt2: This is a pretty hacked together function. Could easily be made more efficient/general.
    """
    suboptimal_before_optimal = None
    unconNAND_before_conNAND = None
    unconNOT_before_conNOT = None
    #lineage_phenotype_sequence = ["0:0:0:0", "0:10:0:10","10:0:10:0", "10:0:8:0", "10:0:0:1"]
    # Suboptimal before optimal?
    subopt_flag = False
    for p in lineage_phenotype_sequence:
        p = map(int, p.split(":"))
        env_nand = p[0:2]
        env_not = p[2:len(p)]
        plast = (env_nand != env_not)
        opt = (env_nand[0] > 0 and env_nand[1] == 0) and (env_not[1] > 0 and env_not[0] == 0)
        subopt = (env_nand != env_not) and (not opt)
        if subopt:
            subopt_flag = True
        elif opt:
            if subopt_flag:
                suboptimal_before_optimal = True
            else:
                suboptimal_before_optimal = False
            break
    # Unconditional NAND before conditional NAND
    unconNAND_flag = False
    for p in lineage_phenotype_sequence:
        p = map(int, p.split(":"))
        env_nand = p[0:2]
        env_not = p[2:len(p)]
        nothing = (env_nand[0] == 0) and (env_not[0] == 0)
        unconNAND = (env_nand[0] == env_not[0]) and (env_nand[0] > 0 and env_not[0] > 0)
        if unconNAND:
            unconNAND_flag = True
        elif not nothing:
            if unconNAND_flag:
                unconNAND_before_conNAND = True
            else:
                unconNAND_before_conNAND = False
            break
    # Unconditional NOT before conditional NOT
    unconNOT_flag = False
    for p in lineage_phenotype_sequence:
        p = map(int, p.split(":"))
        env_nand = p[0:2]
        env_not = p[2:len(p)]
        nothing = (env_nand[1] == 0) and (env_not[1] == 0)
        unconNOT = (env_nand[1] == env_not[1]) and (env_nand[1] > 0 and env_not[1] > 0)
        if unconNOT:
            unconNOT_flag = True
        elif not nothing:
            if unconNOT_flag:
                unconNOT_before_conNOT = True
            else:
                unconNOT_before_conNOT = False
            break
    print {"suboptimal_before_optimal": suboptimal_before_optimal,
            "unconditionalNAND_before_conditionalNAND": unconNAND_before_conNAND,
            "unconditionalNOT_before_conditionalNOT": unconNOT_before_conNOT
            }
    return {"suboptimal_before_optimal": suboptimal_before_optimal,
            "unconditionalNAND_before_conditionalNAND": unconNAND_before_conNAND,
            "unconditionalNOT_before_conditionalNOT": unconNOT_before_conNOT
            }

def main():
    """
    main script functionality
    """
    settings_fn = "param/ss200_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    analysis_loc = os.path.join(experiment_loc, settings["experiment_data"]["avida_analysis_dump"])
    dump = os.path.join(experiment_loc, settings["experiment_data"]["script_analysis_dump"])
    mkdir_p(dump)
    # Pull out some other neato things
    treats_to_process = settings["processing_config"]["treatments_to_test"]
    # Create csv content
    # phenotype sequence format: C0000-C1111-...-C0101; full phenotype sequence format: 10:0:0:10-10:10:10:10-...-0:0:0:0
    # We're going to write out the detailed file line by line
    detailed_csv_header = "treatment,replicate,plastic,optimal,coded_phenotype,full_phenotype,fitness,lineage_coded_phenotype_sequence,lineage_coded_start_updates,lineage_coded_duration_updates,lineage_full_phenotype_sequence,lineage_full_start_updates,lineage_full_duration_updates\n"
    detailed_csv_path = os.path.join(dump, "final_dominant_detailed.csv")
    with open(detailed_csv_path, "w") as fp: fp.write(detailed_csv_header)
    # We'll just write the overview file out all at once
    overview_csv_content = "treatment,total_plastic,proportion_plastic,total_optimal,proportion_optimal,total_subopt_before_optimal_in_lineages,total_optimal_in_lineages,proportion_subopt_before_optimal_in_lineages,total_unconNAND_before_conNAND_in_lineages,total_conNAND_in_lineages,proportion_unconNAND_before_conNAND_in_lineages,total_unconNOT_before_conNOT_in_lineages,total_conNOT_in_lineages,proportion_unconNOT_before_conNOT_in_lineages,total\n"
    for treatment in treats_to_process:
        print "Processing %s" % treatment
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
        # Here's where we'll dump everything for this treatment
        treatment_dump = os.path.join(dump, treatment)
        mkdir_p(treatment_dump)
        # Get all reps of this treatment
        reps = [r for r in os.listdir(analysis_loc) if treatment in r]
        # Initialize some stats we'll be keeping track of
        total_optimal = 0
        total_plastic = 0
        total = 0
        # Sequence stats
        total_subopt_before_opt = 0
        total_unconNAND_before_conNAND = 0
        total_unconNOT_before_conNOT = 0
        total_achieve_conNOT = 0
        total_achieve_conNAND = 0
        total_achieve_opt = 0
        for rep in reps:
            rep_id = rep.split("__rep_")[-1]
            print " - rep: " + str(rep_id)
            rep_loc = os.path.join(analysis_loc, rep, "final_dominant")
            # What environments are we looking at?
            envs = [e.split("__")[-1] for e in os.listdir(rep_loc) if "env__" in e]
            dom_by_env = {}
            lineage_by_env = {}
            lineage_characterizations = []
            for env in envs:
                # Extract details
                fd_loc = os.path.join(rep_loc, "env__" + env, "final_dominant.dat")
                with open(fd_loc, "r") as fp: dom_by_env[env] = detail_file_extract(fp)[0]
                # Extract lineages
                lineage_loc = os.path.join(rep_loc, "env__" + env, "lineage_tasks.dat")
                with open(lineage_loc, "r") as fp: lineage_by_env[env] = extract_lineage_from_detail_file(fp)
            # Characterize the dominant organism
            env_order = _get_treatment_param("environments")
            phenotype_encoding = _get_treatment_param("phenotype_encoding")
            characterization = characterize_org(dom_by_env, phenotype_encoding)
            plastic = characterization["plastic"]
            optimal = characterization["optimal"]
            coded_phenotype = "".join(map(str, characterization["coded_phenotype"]))
            full_phenotype = ":".join(map(str, characterization["full_phenotype"]))
            fitness = ":".join([dom_by_env[e]["fitness"] for e in env_order])
            # Characterize the lineage
            # build lineage sequences
            full_phenotype_seq = []
            coded_phenotype_seq = []
            start_updates = []
            duration_updates = []
            num_ancestors = len(lineage_by_env[env_order[0]])
            for i in range(0, num_ancestors):
                # for each ancestor
                ancestor_by_env = {env:lineage_by_env[env][i] for env in env_order}
                # characterize ancestor
                ancestor_char = characterize_org(ancestor_by_env, phenotype_encoding)
                full_phenotype_seq.append(ancestor_char["full_phenotype"])
                coded_phenotype_seq.append(ancestor_char["coded_phenotype"])
                # start update = update born
                this_start_update = int(ancestor_by_env[env_order[0]]["update born"])
                try:
                    next_start_update = int(lineage_by_env[env_order[0]][i + 1]["update born"])
                except:
                    next_start_update = _get_treatment_param("total_updates")
                duration = next_start_update - this_start_update
                start_updates.append(this_start_update)
                duration_updates.append(duration)
            ###########################################
            # Collapse coded sequences
            collapsed_coded_phenotypes = []
            collapsed_coded_start_updates = []
            collapsed_coded_duration_updates = []
            cur_phen = None
            cur_start = 0
            cur_duration = 0
            for i in range(0, len(coded_phenotype_seq)):
                if cur_phen == None:
                    # First phenotype
                    cur_phen = coded_phenotype_seq[i]
                    cur_start = start_updates[i] + 1            # The +1 accounts for the fact that the ancestor starts at update '-1'; we'll just zero that out.
                    cur_duration = duration_updates[i] - 1      # -1 is here for same reason as above.
                elif coded_phenotype_seq[i] == cur_phen:
                    # Phenotypes match, collapse
                    cur_duration += duration_updates[i]
                else:
                    # Phenotypes do not match, clip
                    collapsed_coded_phenotypes.append("".join(map(str, cur_phen)))
                    collapsed_coded_start_updates.append(cur_start)
                    collapsed_coded_duration_updates.append(cur_duration)
                    cur_phen = coded_phenotype_seq[i]
                    cur_start = start_updates[i]
                    cur_duration = duration_updates[i]
                # Now, we need to check to see if we're at the last state
                #  if so, we'll want to unconditionally clip
                if i == len(coded_phenotype_seq) - 1:
                    collapsed_coded_phenotypes.append("".join(map(str, cur_phen)))
                    collapsed_coded_start_updates.append(cur_start)
                    collapsed_coded_duration_updates.append(cur_duration)
            ###########################################
            # Collapse full sequences
            collapsed_full_phenotypes = []
            collapsed_full_start_updates = []
            collapsed_full_duration_updates = []
            cur_phen = None
            cur_start = 0
            cur_duration = 0
            for i in range(0, len(full_phenotype_seq)):
                if cur_phen == None:
                    # First phenotype
                    cur_phen = full_phenotype_seq[i]
                    cur_start = start_updates[i] + 1            # The +1 accounts for the fact that the ancestor starts at update '-1'; we'll just zero that out.
                    cur_duration = duration_updates[i] - 1      # -1 is here for same reason as above.
                elif full_phenotype_seq[i] == cur_phen:
                    # Phenotypes match, collapse
                    cur_duration += duration_updates[i]
                else:
                    # Phenotypes do not match, clip
                    collapsed_full_phenotypes.append(":".join(map(str, cur_phen)))
                    collapsed_full_start_updates.append(cur_start)
                    collapsed_full_duration_updates.append(cur_duration)
                    cur_phen = full_phenotype_seq[i]
                    cur_start = start_updates[i]
                    cur_duration = duration_updates[i]
                # Now, we need to check to see if we're at the last state
                #  if so, we'll want to unconditionally clip
                if i == len(full_phenotype_seq) - 1:
                    collapsed_full_phenotypes.append(":".join(map(str, cur_phen)))
                    collapsed_full_start_updates.append(cur_start)
                    collapsed_full_duration_updates.append(cur_duration)
            # Characterize the lineage full phenotype sequence
            lineage_characterization = characterize_lineage_phenotypes(collapsed_full_phenotypes)
            ##################################
            # Update overview stats
            if plastic: total_plastic += 1
            if optimal: total_optimal += 1
            total += 1

            if lineage_characterization["suboptimal_before_optimal"]: total_subopt_before_opt += 1
            if lineage_characterization["suboptimal_before_optimal"] != None: total_achieve_opt += 1
            if lineage_characterization["unconditionalNOT_before_conditionalNOT"]: total_unconNOT_before_conNOT += 1
            if lineage_characterization["unconditionalNOT_before_conditionalNOT"] != None: total_achieve_conNOT += 1
            if lineage_characterization["unconditionalNAND_before_conditionalNAND"]: total_unconNAND_before_conNAND += 1
            if lineage_characterization["unconditionalNAND_before_conditionalNAND"] != None: total_achieve_conNAND += 1

            #################################
            # Build detailed csv content line
            # format: "treatment,replicate,plastic,optimal,coded_phenotype,full_phenotype,fitness,lineage_coded_phenotype_sequence,lineage_coded_start_updates,lineage_coded_duration_updates,lineage_full_phenotype_sequence,lineage_full_start_updates,lineage_full_duration_updates\n"
            detailed_csv_line = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %\
                                (
                                treatment, "rep_" + rep_id, plastic, optimal, coded_phenotype, full_phenotype, fitness,
                                "-".join(collapsed_coded_phenotypes),
                                "-".join(map(str, collapsed_coded_start_updates)),
                                "-".join(map(str, collapsed_coded_duration_updates)),
                                "-".join(collapsed_full_phenotypes),
                                "-".join(map(str, collapsed_full_start_updates)),
                                "-".join(map(str, collapsed_full_duration_updates))
                                )

            with open(detailed_csv_path, "a") as fp: fp.write(detailed_csv_line)
        #################
        # Build treatment overview line
        #formatpt2: treatment,total_plastic,proportion_plastic,total_optimal,proportion_optimal,
        #           total_subopt_before_optimal_in_lineages,total_optimal_in_lineages,proportion_subopt_before_optimal_in_lineages,
        #           total_unconNAND_before_conNAND_in_lineages,total_conNAND_in_lineages,proportion_unconNAND_before_conNAND_in_lineages,
        #           total_unconNOT_before_conNOT_in_lineages,total_conNOT_in_lineages,proportion_unconNOT_before_conNOT_in_lineages,
        #           total
        # format: "treatment,total_plastic,total_optimal,total\n"
        prop_plastic = total_plastic / float(total)
        prop_optimal = total_optimal / float(total)
        # Proportion subopt before opt?
        prop_subopt_before_opt = 0
        if total_achieve_opt != 0: prop_subopt_before_opt = total_subopt_before_opt / float(total_achieve_opt)
        # Proportion uncon nand before con nand?
        prop_unconNAND_before_conNAND = 0
        if total_achieve_conNAND != 0: prop_unconNAND_before_conNAND = total_unconNAND_before_conNAND / float(total_achieve_conNAND)
        # proportion uncon not before con not?
        prop_unconNOT_before_conNOT = 0
        if total_achieve_conNOT != 0: prop_unconNOT_before_conNOT = total_unconNOT_before_conNOT / float(total_achieve_conNOT)
        # make content line

        overview_csv_content += "%s,%d,%f,%d,%f,%d,%d,%f,%d,%d,%f,%d,%d,%f,%d\n" % (treatment, total_plastic, prop_plastic, total_optimal, prop_optimal,
                                                                                    total_subopt_before_opt, total_achieve_opt, prop_subopt_before_opt,
                                                                                    total_unconNAND_before_conNAND, total_achieve_conNAND, prop_unconNAND_before_conNAND,
                                                                                    total_unconNOT_before_conNOT, total_achieve_conNOT, prop_unconNOT_before_conNOT,
                                                                                    total)
    # Write out overview csv content
    with open(os.path.join(dump, "final_dominant_overview.csv"), "w") as fp: fp.write(overview_csv_content)
    print ("DONE")

if __name__ == "__main__":
    main()
