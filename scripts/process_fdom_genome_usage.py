#!/usr/bin/python2
import json, os, re
from utilities.utilities import mkdir_p
from utilities.parse_avida_output import genome_from_genfile

"""
This scripts requires that the final_dom_analyze.cfg Avida analyze script has been run on the experiment data.
Loops through and processes final_dom traces + .gen files.
Writes out a .csv file with the following information:
 * treatment, replicate, environment, genome_sites, site_usage, norm_site_usage
"""

def _extract_site_sequence(trace_fp):
    """
    Given a file pointer to an execution trace produced by avida's analyze mode,
     return the site usage (list where index represents the site and the value represents executions at that site)
    """
    # Step 1: chunk the trace
    execution_states = []
    execution_site_sequence = []
    execution_inst_sequence = []
    current_state = -1
    for line in trace_fp:
        if "---------------------------" in line:
            current_state += 1
            execution_states.append("")
        else:
            execution_states[current_state] += line
    # Step 2: extract site execution sequence
    for state in execution_states[:-1]:
        # get instruction head location
        m = re.search(pattern = "IP:(\d+)", string = state)
        instr_head = int(m.group(1))
        # get current instruction
        m = re.search(pattern = "IP:\d+\s\((.*)\)\n", string = state)
        current_instruction = str(m.group(1))
        # store our findings
        execution_site_sequence.append(int(instr_head))
        execution_inst_sequence.append(current_instruction)
    return {"sites": execution_site_sequence, "instructions": execution_inst_sequence}


def main():
    """
    main script functionality
    """
    settings_fn = "param/ss_analysis_settings.json"
    settings = None
    # Load settings from settings file
    with open(settings_fn) as fp:
        settings = json.load(fp)
    # Pull out locations of interest
    experiment_loc = settings["experiment_data"]["base_location"]
    analysis_loc = os.path.join(experiment_loc, settings["experiment_data"]["avida_analysis_dump"])
    dump = os.path.join(experiment_loc, settings["experiment_data"]["script_analysis_dump"])
    mkdir_p(dump)
    # Pull out some other things
    treatments_to_process = settings["processing_config"]["treatments_to_process"]
    # Create csv content
    genome_usage_csv_header = "treatment,replicate,environment,sites,site_usage,norm_site_usage\n"
    genome_usage_csv_path = os.path.join(dump, "final_dominant_genome_usages.csv")
    with open(genome_usage_csv_path, "w") as fp: fp.write(genome_usage_csv_header)
    for treatment in treatments_to_process:
        print "Processing treatment: %s" % treatment
        # First define treatment specs/inherited specs
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
        reps = [r for r in os.listdir(analysis_loc) if treatment in r and "__rep_" in r]
        print "Processing these replicates: " + str(reps)
        for rep in reps:
            rep_id = rep.split("__rep_")[-1]
            rep_loc = os.path.join(analysis_loc, rep, "final_dominant")
            print "Processing replicate: " + str(rep_id)
            # What environments are we looking at?
            envs = [e.split("__")[-1] for e in os.listdir(rep_loc) if "env__" in e]
            dom = {} # dom.sites, dom.usage
            # Grab genome sites from either environment (this will be the same in both environments)
            with open(os.path.join(rep_loc, "env__" + envs[-1], "final_dominant.gen"), "r") as fp:
                dom["sites"] = genome_from_genfile(fp)
            for env in envs:
                tloc = os.path.join(rep_loc, "env__" + env, "trace")
                fname = os.listdir(tloc)[0]
                tloc = os.path.join(tloc, fname)
                trace = None
                with open(tloc, "r") as fp:
                    trace = _extract_site_sequence(fp)
                site_usage = [0 for _ in range(0, len(dom["sites"]))]
                norm_site_usage = [0 for _ in range(0, len(dom["sites"]))]
                # Calculate site usage
                for i in range(0, len(trace["sites"])):
                    site_usage[trace["sites"][i] % len(trace["sites"])] += 1
                    #print trace["sites"][i], trace["instructions"][i], dom["sites"][trace["sites"][i]]
                # Calculate normalized site usage
                for i in range(0, len(site_usage)):
                    norm_site_usage[i] = site_usage[i] / float(sum(site_usage))
                dom[env] = {"env-site-usage": site_usage, "env-norm-site-usage": norm_site_usage}
                # Build csv line
                # "treatment,replicate,environment,sites,site_usage,norm_site_usage\n"
                csv_content = "%s,%s,%s,%s,%s,%s\n" % (treatment, rep, env, "|".join(dom["sites"]), "|".join(map(str, site_usage)), "|".join(map(str, norm_site_usage)))
                with open(genome_usage_csv_path, "a") as fp: fp.write(csv_content)

if __name__ == "__main__":
    main()
