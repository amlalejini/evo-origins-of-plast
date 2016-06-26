var zoom_rate = 0.05;
var default_treatment = "c100";
var lineage_vis_data_fpath = "data/ss_final_dominant_detailed.csv";
var lineage_vis_settings =
{
  "control-unrestricted": {
    "hr_name": "Control: Unrestricted",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100000,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotp"],
    "update_label_interval": 500,
  },
  "control-uncon-restricted": {
    "hr_name": "Control: Unconditional Expression Restricted",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100000,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotp"],
    "update_label_interval": 500,
  },
  "control-subopt-restricted": {
    "hr_name": "Control: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100000,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotp"],
    "update_label_interval": 500,
  },
  "control-full-restricted": {
    "hr_name": "Control: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100000,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotp"],
    "update_label_interval": 500,
  },

  "baseline-unrestricted": {
    "hr_name": "baseline: UR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "baseline-uncon-restricted": {
    "hr_name": "baseline: UCONR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "baseline-subopt-restricted": {
    "hr_name": "baseline: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "baseline-full-restricted": {
    "hr_name": "baseline: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },

  "high-mut-unrestricted": {
    "hr_name": "HM: UR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "high-mut-uncon-restricted": {
    "hr_name": "HM: UCONR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "high-mut-subopt-restricted": {
    "hr_name": "HM: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "high-mut-full-restricted": {
    "hr_name": "HM: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },

  "low-mut-unrestricted": {
    "hr_name": "low-mut: UR",
    "sliced_ranges": [[5500, 7000], [25000, 27000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "low-mut-uncon-restricted": {
    "hr_name": "low-mut: UCONR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "low-mut-subopt-restricted": {
    "hr_name": "low-mut: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "low-mut-full-restricted": {
    "hr_name": "low-mut: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },

  "cycle-50-unrestricted": {
    "hr_name": "cycle-50: UR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 50,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-50-uncon-restricted": {
    "hr_name": "cycle-50: UCONR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 50,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-50-subopt-restricted": {
    "hr_name": "cycle-50: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 50,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-50-full-restricted": {
    "hr_name": "cycle-50: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 50,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },

  "cycle-200-unrestricted": {
    "hr_name": "cycle-200: UR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 200,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-200-uncon-restricted": {
    "hr_name": "cycle-200: UCONR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 200,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-200-subopt-restricted": {
    "hr_name": "cycle-200: SR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 200,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "cycle-200-full-restricted": {
    "hr_name": "cycle-200: FR",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 200,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },

  "c50": {
    "hr_name": "c50",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 50,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "c100": {
    "hr_name": "c100",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 100,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  },
  "c400": {
    "hr_name": "c400",
    "sliced_ranges": [[0, 1000], [47500, 52500], [95000, 100000]],
    "full_ranges": [[0, 100000]],
    "environment_cycle_length": 400,
    "maximum_update": 100000,
    "environment_codes": ["nandpnotm", "nandmnotp"],
    "update_label_interval": 500,
  }

};


lookup_table = {
  "nandpnotp": "CONTROL-ENV",
  "nandpnotm": "ENV-NAND",
  "nandmnotp": "ENV-NOT",
  "tasks_performed": {
    "0000": {"ENV-NAND": "NONE", "ENV-NOT": "NONE"},
    "0001": {"ENV-NAND": "NONE", "ENV-NOT": "NOT"},
    "0010": {"ENV-NAND": "NONE", "ENV-NOT": "NAND"},
    "0011": {"ENV-NAND": "NONE", "ENV-NOT": "BOTH"},
    "0100": {"ENV-NAND": "NOT", "ENV-NOT": "NONE"},
    "0101": {"ENV-NAND": "NOT", "ENV-NOT": "NOT"},
    "0110": {"ENV-NAND": "NOT", "ENV-NOT": "NAND"},
    "0111": {"ENV-NAND": "NOT", "ENV-NOT": "BOTH"},
    "1000": {"ENV-NAND": "NAND", "ENV-NOT": "NONE"},
    "1001": {"ENV-NAND": "NAND", "ENV-NOT": "NOT"},
    "1010": {"ENV-NAND": "NAND", "ENV-NOT": "NAND"},
    "1011": {"ENV-NAND": "NAND", "ENV-NOT": "BOTH"},
    "1100": {"ENV-NAND": "BOTH", "ENV-NOT": "NONE"},
    "1101": {"ENV-NAND": "BOTH", "ENV-NOT": "NOT"},
    "1110": {"ENV-NAND": "BOTH", "ENV-NOT": "NAND"},
    "1111": {"ENV-NAND": "BOTH", "ENV-NOT": "BOTH"}
  }
};
