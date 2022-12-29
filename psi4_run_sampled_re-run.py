#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from psi4_calc import psi4_calc
from electric_field_tools import load_positions_xyz, load_charges_dat,\
        get_equivalent_mean_electric_field

# (user defined: paths)
out_tag = "icg_lc"
samples_folder = "random_sampling"
out_folder_path = "results"
selected_indices_path = os.path.join(samples_folder, "random_indices.txt")
explicit_positions_filename = "explicit_atoms_$index$.xyz"
implicit_charges_filename = "implicit_charges_$index$.dat"

# (user defined: electronic)
max_ram = "60GB"
max_thr = 16
functional = "LRC-WPBE"
basis_set = "def2-SVPD"
nstates = 6

# (creates output containing folder)
if not os.path.exists(out_folder_path): os.mkdir(out_folder_path)

selected_indices = np.loadtxt(selected_indices_path, dtype=int)
for index in selected_indices[2:3]:
    # (prepares paths)
    xyz_path = os.path.join(samples_folder, explicit_positions_filename.replace("$index$", str(index)))
    imp_dat_path = os.path.join(samples_folder, implicit_charges_filename.replace("$index$", str(index)))
    # (creates out folder)
    out_path = os.path.join(out_folder_path, f"{out_tag}_{index}")
    if not os.path.exists(out_path): os.mkdir(out_path)
    
    f = False

    # (in vacuum)
    this_tag = "vac_" + out_tag
    try: 
        f = open(f"{this_tag}_td.out","r")
    except FileNotFoundError:
        print(f"No está corrido {this_tag}_td.out\n")
        psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, output_folder=out_path)
    if f:
        for i,line in enumerate(f):
            if "Excited State    8" in line:
                break 
            elif i==(len(lines)-1):
                psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, output_folder=out_path)
    f = False

    # (with implicit charges)
    this_tag = "imp_" + out_tag
    try: 
        f = open(f"{this_tag}_td.out","r")
        lines = f.readlines()
    except FileNotFoundError:
        print(f"No está corrido {this_tag}_td.out\n")
        psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, external_charges=imp_dat_path, output_folder=out_path)
    if f:
        for i,line in enumerate(f):
            if "Excited State    8" in line:
                break
            elif i==(len(lines)-1):
                psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, external_charges=imp_dat_path, output_folder=out_path)

    f = False

    # (with equivalent field)
    this_tag = "eqf_" + out_tag
    try: 
        f = open(f"{this_tag}_td.out","r")
    except FileNotFoundError:
        print(f"No está corrido {this_tag}_td.out\n")
        imp_positions, imp_charges = load_charges_dat(imp_dat_path)
        exp_positions = load_positions_xyz(xyz_path)
        eq_field_vec = get_equivalent_mean_electric_field(imp_positions, imp_charges, exp_positions)
        psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, external_field=eq_field_vec, output_folder=out_path)
    if f:
        for i,line in enumerate(f):
            if "Excited State    8" in line:
                break 
            elif i==(len(lines)-1):
                    imp_positions, imp_charges = load_charges_dat(imp_dat_path)
                    exp_positions = load_positions_xyz(xyz_path)
                    eq_field_vec = get_equivalent_mean_electric_field(imp_positions, imp_charges, exp_positions)
                    psi4_calc(xyz_path, functional, basis_set, nstates, max_ram, max_thr, optimize=False, out_tag=this_tag, external_field=eq_field_vec, output_folder=out_path)

##############################
#   Andrés Ignacio Bertoni   #
# (andresibertoni@gmail.com) #
##############################
