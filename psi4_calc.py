#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import psi4
from psi4.driver.procrouting.response.scf_response import tdscf_excitations
from psi4.driver import QMMMbohr

def set_output(output_filename="output.dat"):
    psi4.core.set_output_file(output_filename, False)

def load_geometry(xyz_file, append_lines=[]):
    with open(xyz_file, "r") as xyzfile:
        content = "no_com\nno_reorient\n"
        content += "".join(xyzfile.readlines()[1:])
        for line in append_lines:
            content += line + "\n"
        molecule = psi4.geometry(content)
    return molecule

def prepare_charge_field(external_charges):
<<<<<<< HEAD
    if type(external_charges) not in [list, np.ndarray]: #pregunta si external_charges es una lista o np.array. Si no, lo levanta. Si está, lo vuelve array.
=======
    if type(external_charges) not in [list, np.ndarray]:
>>>>>>> b7ff201e6b0ef274e1534ccdfb660afb7a0c7381
        external_charges = np.loadtxt(external_charges)
    else: external_charges = np.array(external_charges)
    x,y,z,q = external_charges.T
    positions_angstrom = np.vstack([x,y,z])
    positions_bohr = positions_angstrom / psi4.constants.bohr2angstroms
<<<<<<< HEAD
    charge_field = np.vstack([q, positions_bohr]).T  #¿ La cargas primero???? q,x,y,z.... en lugar de x,y,z,q??????
=======
    charge_field = np.vstack([q, positions_bohr]).T
>>>>>>> b7ff201e6b0ef274e1534ccdfb660afb7a0c7381
    return charge_field

def read_charge_mult(xyz_path):
    with open(xyz_path, "r") as xyz_file:
        items = xyz_file.readlines()[1].split()
    try: charge = int(items[0])
    except:
        print("WARNING: Valid charge not found! --> Assuming charge neutrality.")
        charge = 0
    try: mult = int(items[1])
    except:
        print("WARNING: Valid multiplicity not found! --> Assuming closed shell (singlet state).")
        mult = 1
    return charge, mult

def add_charge_mult(xyz_path, charge, mult):
    with open(xyz_path, "r") as xyz_file:
        xyz_lines = xyz_file.readlines()
    new_line = f"{charge} {mult}\n"
    with open(xyz_path, "w") as xyz_file:
        for idx,line in enumerate(xyz_lines):
            if idx == 1: line = new_line
            xyz_file.write(line)

def psi4_calc(xyz_path, functional, basis_set, td_n_states=0, max_ram="1 GB", max_thr=1, out_tag=None, out_cubes=None, store_wfn=True, symmetry="C1", optimize=False, external_field=None, external_charges=None, output_folder="."):
    # Setup
    # (tags)
    if not out_tag: out_tag = xyz_path.replace(".xyz","")
    # (system)
    print("\n~~~")
    print(f"Setting all up for {out_tag}...")
    psi4.set_memory(max_ram)
    psi4.core.set_num_threads(max_thr)
<<<<<<< HEAD
    set scf_type direct
=======
    psi4.set_options({"scf_type":"df"})
>>>>>>> b7ff201e6b0ef274e1534ccdfb660afb7a0c7381
    # (lr-td)
    if td_n_states > 0:
        psi4.set_options({"save_jk":True})
        store_wfn = True
    print("~~~")
    # Symmetry
    # ('C1' is default : no symmetry elements except identity)
    if symmetry is None: append_lines = []
    else: append_lines = [f"symmetry {symmetry.lower()}"]
    # Geometry
    molecule = load_geometry(xyz_path, append_lines)
    charge, mult = read_charge_mult(xyz_path)
    # External Field for base calculation
    extra_tag = None
    if external_field is not None:
        psi4.set_options({"perturb_h":True})
        psi4.set_options({"perturb_with":"dipole"})
        psi4.set_options({"perturb_dipole":external_field.tolist()})
    else: psi4.set_options({"perturb_h":False})
    # External (point, MM) Charges for base calculation
    if external_charges is not None: charge_field = prepare_charge_field(external_charges)
    else: charge_field = None
    # Energy
    if not optimize:
        print(f"Computing energy with {functional}/{basis_set}...")
        if external_field is not None: print(f"(External field of [{external_field[0]:.4f}, {external_field[1]:.4f}, {external_field[2]:.4f}].)")
        else: print("(No external field.)")
        set_output(os.path.join(output_folder, f"{out_tag}.out"))
        if charge_field is None:
            print("(No external point-charges.)")
            energy, wavefunction = psi4.energy(f"{functional}/{basis_set}", return_wfn=store_wfn)
        else:
            print(f"(Including field of {len(charge_field)} external point-charges.)")
            energy, wavefunction = psi4.energy(f"{functional}/{basis_set}", return_wfn=store_wfn, external_potentials=charge_field)
        print("~~~")
    # Optimization
    else:
        print(f"Optimizing structure with {functional}/{basis_set}...")
        if external_field is not None: print(f"(External field of [{external_field[0]:.4f}, {external_field[1]:.4f}, {external_field[2]:.4f}].)")
        else: print("(No external field.)")
        set_output(os.path.join(output_folder, f"{out_tag}_opt.out"))
        if charge_field is None:
            print("(No external point-charges.)")
            energy, wavefunction = psi4.optimize(f"{functional}/{basis_set}", molecule=molecule, return_wfn=store_wfn)
        else:
            print(f"(Including field of {len(charge_field)} external point-charges.)")
            energy, wavefunction = psi4.optimize(f"{functional}/{basis_set}", molecule=molecule, return_wfn=store_wfn, external_potentials=charge_field)
        print("~~~")
        new_xyz_path = xyz_path.replace(".xyz", "_opt.xyz")
        print(f"Saving optimized structure as {new_xyz_path}!")
        molecule.save_xyz_file(new_xyz_path, True)
        add_charge_mult(new_xyz_path, charge, mult)
        print("~~~")
    # Wavefunction
    if store_wfn:
        print(f"Storing Wavefunction as {out_tag}_wnf.npy!")
        wfn_file = wavefunction.get_scratch_filename(180)
        wavefunction.to_file(wfn_file)
        wavefunction.to_file(os.path.join(output_folder, f"{out_tag}_wfn"));
        print("~~~")
    # Cubes
    if out_cubes is not None:
        print(f"Storing cube files for molecular orbitals with indices: {' '.join(out_cubes)}!")
        if "frontier" in out_cubes:
            psi4.set_options({"cubeprop_tasks":["frontier_orbitals"]})
        else: psi4.set_options({"cubeprop_tasks":["orbitals"], "cubeprop_orbitals":out_cubes})
        if output_folder != ".":
            psi4.set_options({"cubeprop_filepath":output_folder})
        psi4.cubeprop(wavefunction)
        print("~~~")
    # LR-TD
    if td_n_states > 0:
        print(f"Computing the first {td_n_states} excitation energies with {functional}/{basis_set}...")
        if external_field is not None: print(f"(External field of [{external_field[0]:.4f}, {external_field[1]:.4f}, {external_field[2]:.4f}].)")
        else: print("(No external field.)")
        if charge_field is None: print("(No external point-charges.)")
        else: print(f"(Including field of {len(charge_field)} external point-charges.)")
        # Run LR-TD
        set_output(os.path.join(output_folder, f"{out_tag}_td.out"))
        psi4.set_options({"tdscf_print":2, "tdscf_coeff_cutoff":0.05, "tdscf_tdm_print":["e_tdm_len"]})
        result = tdscf_excitations(wavefunction, states=td_n_states)
    # Return
    print(f"~~~\nAll finished for {out_tag}!\n~~~\n")
    if store_wfn: return wavefunction

##############################
#   Andrés Ignacio Bertoni   #
# (andresibertoni@gmail.com) #
##############################
