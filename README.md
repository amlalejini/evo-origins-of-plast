# evo-origins-of-plast
Repository for Evolutionary Origins of Phenotypic Plasticity Project (as of 05/03/2016)

## Scripts
 * mk_runlist.py -- Uses experiment specifications defined in param/ss_exp_specs.json to generate a run_list file to run the experiment. (Entire experiment ran from one run_list file)
 * run_avida_analyses.py -- Uses ss_analysis_settings for input parameters. Given details about file locations, etc, this script will run avida in analyze mode using all specified analysis scripts on all specified treatments. Original submission arguments for each treatment are used when running avida in analyze mode for that treatment.  
  * process_final_dominants.py -- This script processes analysis data generated from the 'final_dom_analyze.cfg' avida analyze script.
    * Expected output:
      * final_dominant_details.csv:
        * For each final dominant genotype: is_plastic, is_optimal, trait values, abstracted phenotype code, lineage code sequence, lineage full phenotype sequence
      * final_dominant_overview.csv:
        * treatment, # reps plastic, # reps optimal
