

def write_run_params(ambig_tbl = None,
                     haddock_dir = "/root/haddock/haddock2.4-2021-01/",
                     n_comp = 2,
                     pdb_file_1 = "",
                     pdb_file_2 = "",
                     project_dir = "./",
                     prot_segid_1 = "A",
                     prot_segid_2 = "B",
                     run_number = 1,
                     output_file = "run.param"):
    param_lines  = [
        f"HADDOCK_DIR={haddock_dir}",
        f"N_COMP={n_comp}",
        f"PDB_FILE1={pdb_file_1}",
        f"PDB_FILE2={pdb_file_2}",
        f"PROJECT_DIR={project_dir}",
        f"PROT_SEGID_1={prot_segid_1}",
        f"PROT_SEGID_2={prot_segid_2}",
        f"RUN_NUMBER={run_number}",
    ]
    if ambig_tbl:
        param_lines = [f"AMBIG_TBL={ambig_tbl}", *param_lines]
    # print(param_lines)
    # return(param_lines)
    f = open(output_file, "w")
    f.writelines("\n".join(param_lines))
    f.close()