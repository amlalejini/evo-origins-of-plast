#!/usr/bin/python2
from utilities.utilities import mkdir_p

import json, sys, os, shutil

'''
This module reads from main and composes run list files for an experiment.
'''

if __name__ == "__main__":
    # Grab run list specification
    with open("param/stepping_stones_run_list_spec.json") as fp:
        specs = json.load(fp)
    # Go ahead and extract experiment name and list of treatment specifications
    experiment = specs["experiment"]
    treatments = specs["treatments"]
    dist_analyses = specs["distribute_analyses"]
    print treatments.keys()
    # Build run_list file for each treatment
    for treatment in treatments:
        ###################
        # Build the run list file
        ###################
        # First, define treatment specs and inherited specs (shared)
        TSPEC = specs["treatments"][treatment]
        ISPEC = specs[specs["treatments"][treatment]["inherit_from"]]
        def _get_spec(spec = None):
            '''
            useful helper function for getting the correct parameter value
            @amlalejini: there are various things I could do to make this nicer.
            '''
            if spec in TSPEC.keys():
                return TSPEC[spec]
            elif spec in TSPEC["-set"].keys():
                return TSPEC["-set"][spec]
            elif spec in ISPEC.keys():
                return ISPEC[spec]
            elif spec in ISPEC["-set"].keys():
                return ISPEC["-set"][spec]
            else:
                return None

        description = "EXP: %s; TREATMENT: %s"  % (experiment, treatment)
        class_pref = _get_spec("class_pref")
        mem_request = _get_spec("mem_request")
        email_when = _get_spec("email_when")
        email = _get_spec("email")
        walltime = _get_spec("walltime")
        config_dir = os.path.join(_get_spec("config_dir_base"), treatment, "configs")
        dest_dir = os.path.join(_get_spec("dest_dir_base"), treatment, "data")
        # Combine everything that belongs in the run list header
        run_list_header ='''set description %s
set class_pref %s
set mem_request %s
set email_when %s
set email %s
set walltime %s
set config_dir %s
set dest_dir %s

''' % (description, class_pref, mem_request, email_when, email, walltime, config_dir, dest_dir)
        # Grab the start/end seeds
        start_seed = _get_spec("replicates_begin-end")[0]
        end_seed = _get_spec("replicates_begin-end")[1]
        avida_config = _get_spec("avida_config")
        # Initialize args with common args
        args = {key:ISPEC["-set"][key] for key in ISPEC["-set"]}
        # Then, overwrite/add where necessary with treatment-specific args
        for arg in TSPEC["-set"]: args[arg] = TSPEC["-set"][arg]
        arg_str = ""
        for arg in args:
            arg_str += "-set %s %s " % (arg, args[arg])
        # Finally, put together the avida run cmd
        avida_cmd = "%d..%d single_runs ./avida -c %s -s $seed %s \n" % (start_seed, end_seed, avida_config, arg_str)
        # Combine the header and the avida cmd for the full run list file content
        run_list = run_list_header + avida_cmd

        ###################
        # Pull in necessary files form 'config_source_dir' and build treatment directories
        ###################
        config_dest = os.path.join("./", experiment, treatment, "configs")
        mkdir_p(config_dest)
        # copy over 1) avida config, 2) ancestor org, 3) instruction set, 4) environment, 5) events
        config_src_dir = _get_spec("config_source_dir")
        avida_config = os.path.join(config_src_dir, _get_spec("avida_config"))
        ancestor_config = os.path.join(config_src_dir, _get_spec("ancestor_org"))
        instr_set_config = os.path.join(config_src_dir, _get_spec("instruction_set"))
        env_config = os.path.join(config_src_dir, _get_spec("ENVIRONMENT_FILE"))
        event_config = os.path.join(config_src_dir, _get_spec("EVENT_FILE"))
        executable = os.path.join(config_src_dir, _get_spec("executable"))
        cfgs = [avida_config, ancestor_config, instr_set_config, env_config, event_config, executable]
        for cfg in cfgs: shutil.copyfile(cfg, os.path.join(config_dest, cfg.split("/")[-1]))
        # should we copy over analyses?
        if dist_analyses:
            # save out avida cmd args necessary to rerun with same settings
            with open(os.path.join(config_dest, "avida_args.info"), "w") as fp:
                fp.write("-c %s %s" % (_get_spec("avida_config"), arg_str))
            # for each specified analysis file
            for afile in _get_spec("analysis_files"):
                # set the 'experiment'/treatment name
                fcontent = ""
                with open(os.path.join(config_src_dir, afile)) as fp:
                    for line in fp:
                        if "SET e" in line:
                            fcontent += "SET e %s\n" % treatment
                        else:
                            fcontent += line
                with open(os.path.join(config_dest, afile), "w") as fp:
                    fp.write(fcontent)
        # Write out the run list file
        with open(os.path.join(config_dest, "run_list-%s" % treatment), "w") as fp:
            fp.write(run_list)

    print("Done")
