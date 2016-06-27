#!/usr/bin/python2
"""
"""
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    """
    Main script functionality
    """
    fdom_overview_frame = pd.read_csv("data/ss200_final_dominant_overview.csv")


    ###################################
    # Unrestricted rates
    ###################################
    ## Rates of plasticity ##
    evo_plast_frame = fdom_overview_frame[fdom_overview_frame["treatment"].apply(lambda e: "unrestricted" in e)]
    # Cycle length
    cl_plast_frame = evo_plast_frame[fdom_overview_frame["treatment"].apply(lambda e: ("cycle" in e) or ("baseline" in e) or ("control" in e))]
    # Mutation rate
    mut_plast_frame = evo_plast_frame[fdom_overview_frame["treatment"].apply(lambda e: ("mut" in e) or ("baseline" in e) or ("control" in e))]

    sns.set_style("dark")
    sns.set(font_scale = 1.2)
    ###################
    # Plot things
    ###################
    # plt.subplot(121)
    # clorder = ["cycle-50-unrestricted", "baseline-unrestricted", "cycle-200-unrestricted", "control-unrestricted"]
    # cl_plot = sns.barplot(x = "treatment", y = "total_plastic", data = cl_plast_frame, order = clorder, n_boot = 1000)
    # cl_plot.set_ylim([0, 200])
    # # add value at top of chart
    # for p in cl_plot.patches:
    #     height = p.get_height()
    #     cl_plot.text(p.get_x() + (p.get_width() / 2.0) * 0.9, height + 2, str(int(height)))
    #
    # plt.subplot(122)
    # mutorder = ["low-mut-unrestricted", "baseline-unrestricted", "high-mut-unrestricted", "control-unrestricted"]
    # mut_plot = sns.barplot(x = "treatment", y = "total_plastic", data = mut_plast_frame, order = mutorder, n_boot = 1000)
    # mut_plot.set_ylim([0, 200])
    # # add value at top of chart
    # for p in mut_plot.patches:
    #     height = p.get_height()
    #     mut_plot.text(p.get_x() + (p.get_width() / 2.0) * 0.9, height + 2, str(int(height)))
    # plt.show()

    ####################################
    # Restricted Rates
    ####################################
    fdom_grouped_df = pd.read_csv("data/ss200_final_dominant_overview2.csv")
    fdom_grouped_df = fdom_grouped_df[fdom_grouped_df["treatment"] != "control"]
    # Plot baseline
    bss_plot = sns.factorplot(x = "treatment", y = "total_plastic", data = fdom_grouped_df, hue = "condition", hue_order = ["unrestricted", "uncon-restricted", "subopt-restricted", "full-restricted"], kind = "bar", order = ["baseline", "low-mut", "high-mut", "cycle-50", "cycle-200"])
    bss_plot.set(ylim = [0, 200])
    plt.show()

if __name__ == "__main__":
    main()
