#!/usr/bin/python2
import re

def detail_file_extract(detail_fp):
    """
    Given file pointer to detail file, extract information into form below:
    return [{"detail":value, "detail":value, ...}, ...]
    """
    ######################
    # Step 1) Build Legend
    ###
    # Travel to the legend.
    for line in detail_fp:
        if line == "# Legend:\n": break
    # Consume the legend.
    details = []
    for line in detail_fp:
        if line == "\n": break
        details.append(line.split(":")[-1].strip())
    ######################
    # Step 2) Consume Organisms
    ###
    orgs = {}
    org_cnt = 0
    for line in detail_fp:
        org_dets = line.strip().split(" ")
        org = {details[i].lower():org_dets[i] for i in range(0, len(org_dets))}
        org_id = -1
        if "genotype id" in org:
            org_id = org["genotype id"]
        else:
            org_id = org_cnt
        orgs[org_id] = org
        org_cnt += 1
    return orgs

def extract_lineage_from_detail_file(detail_fp):
    """
    Given detail file pointer of a lineage, parse. Return as dictionary.
    """
    # Find column labels
    col_labels = []
    lineage_details = []
    for line in detail_fp:
        if line.strip() == "# Legend:": break
    # Collect column labels
    for line in detail_fp:
        if line.strip() == "": break
        m = re.search(pattern = "#\s[0-9]+:\s([\w\s]+)", string = line)
        col_labels.append(m.group(1).strip().lower())
    # Collect ancestor details
    for line in detail_fp:
        ancestor_details = line.strip().split(" ")
        lineage_details.append({col_labels[i]: ancestor_details[i] for i in range(0, len(ancestor_details))})
    return lineage_details

def genome_from_genfile(gen_fp):
    """
    Given a file pointer to a .gen (from avida analyze mode), return the genome as a list of instructions.
    """
    return [line.strip() for line in gen_fp if (line.strip() != "") and (not "#" in line)]
