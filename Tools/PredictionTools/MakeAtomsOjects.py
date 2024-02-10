import string
from ase.io.vasp import read_vasp
from itertools import product

def permutate(structurename: str, Nelements: int, NWyckoff: int):
    # names of elements
    element_names = list(string.ascii_uppercase)[:Nelements]
    configs = []
    for placement_tags in product(element_names, repeat=NWyckoff):
        configs.append(structurename+'-'+''.join(placement_tags) )
    return configs

def old_permutate(structurename,Nelements,NWyckoff):
    # names of elements
    n=['A','B','C','D','E','F','G','H','I','J']
    # list container for all strings
    permutations=[]
    # loop elements on Wyckoff sites
    for e1 in range(Nelements):
        for e2 in range(Nelements):
            if NWyckoff==2:
                config = n[e1]+n[e2]
                permutations.append(config)
            else:
                for e3 in range(Nelements):
                    if NWyckoff==3:      
                        config = n[e1]+n[e2]+n[e3]
                        permutations.append(config)
                    else:    
                        for e4 in range(Nelements):
                            if NWyckoff==4:                              
                                config = n[e1]+n[e2]+n[e3]+n[e4]
                                permutations.append(config)
                            else:
                                for e5 in range(Nelements):
                                    if NWyckoff==5:                              
                                        config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]
                                        permutations.append(config)
                                    else:
                                        for e6 in range(Nelements):
                                            if NWyckoff==6:                              
                                                config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]
                                                permutations.append(config)
                                            else:
                                                for e7 in range(Nelements):
                                                    if NWyckoff==7:                              
                                                        config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]+n[e7]
                                                        permutations.append(config)
                                                    else:
                                                        for e8 in range(Nelements):
                                                            if NWyckoff==8:                              
                                                                config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]+n[e7]+n[e8]
                                                                permutations.append(config)
                                                            else:
                                                                for e9 in range(Nelements):
                                                                    if NWyckoff==9:                              
                                                                        config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]+n[e7]+n[e8]+n[e9]
                                                                        permutations.append(config)
                                                                    else:
                                                                        for e10 in range(Nelements):
                                                                            if NWyckoff==10:                              
                                                                                config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]+n[e7]+n[e8]+n[e9]+n[e10]
                                                                                permutations.append(config)
                                                                            else:
                                                                                for e11 in range(Nelements):
                                                                                    config = n[e1]+n[e2]+n[e3]+n[e4]+n[e5]+n[e6]+n[e7]+n[e8]+n[e9]+n[e10]+n[e11]
                                                                                    permutations.append(config)
    for i in range(len(permutations)):
        permutations[i] = structurename+'-'+permutations[i]
    return permutations


# In[2]:



def readPOSCAR(filename):
    poscarfile = open(filename,'r')
    poscar = poscarfile.readlines()
    poscarfile.close()
    return poscar

def splitPOSCAR(poscar):
    header   = poscar[0:5]
    allatoms = poscar[7:]
    return header,allatoms


def writePOSCAR(filename,poscar):
    f=open(filename,'w')
    for line in poscar: f.write(line)
    f.close()
    return

def compilePOSCAR(header,comp,atoms):
    poscar = header
    compstr = ''
    for compi in comp: compstr += str(compi)+' '
    poscar.append(compstr+'\n')
    poscar.append('direct\n')
    for atom in atoms: poscar.append(atom)
    return poscar

def getSublattices(allatoms):
    sublabel = []
    for atom in allatoms:
        label = atom.split()[3]
        if len(sublabel) == 0:
            sublabel.append(label)
        else:
            newlabel = True
            for oldlabel in sublabel:
                if oldlabel==label: 
                    newlabel = False
            if newlabel: 
                sublabel.append(label)
    return sublabel

def splitAtoms(allatoms,sublattices):
    atomblocks = []
    for i in sublattices: atomblocks.append([])
    for atom in allatoms:
        subatom = atom.split()[3]
        for i in range(len(sublattices)):
            if subatom == sublattices[i]:
                temp = atomblocks[i][:]
                temp.append(atom)
                atomblocks[i][:] = temp
    return atomblocks

def setOccupation(atomblocks,occupation):
    atoms = []
    species = list(set(occupation))
    species.sort()
    nspecies = len(species)
    comp = []
    for speci in species:
        compi = 0
        for i in range(len(occupation)):
            if occupation[i] == speci:
                blocki=atomblocks[i]
                for atom in blocki: atoms.append(atom)
                compi += len(blocki)
        comp.append(compi)
    return atoms, comp



def generatePOSCAR(filename):
    strucname = filename.split('-')[0]
    occstring = filename.split('-')[1]
    # read POSCAR and prepare data
    structure = readPOSCAR('POSCAR.'+strucname)
    header, atomsOriginal = splitPOSCAR(structure)
    sublattices = getSublattices(atomsOriginal)
    #print('detected ',len(sublattices),' sublattices: ',sublattices)
    atomblocks = splitAtoms(atomsOriginal,sublattices)
    natoms = [] 
    for blocki in atomblocks: natoms.append(len(blocki))
    #print('atoms in sublattices: ',natoms)
    # order atomblocks according to occupation string
    occupation = [occi for occi in occstring]
    atoms, comp = setOccupation(atomblocks,occupation)
    poscar = compilePOSCAR(header,comp,atoms)
    writePOSCAR('POSCAR.'+filename,poscar)
    return

import re
import  mendeleev
import numpy as np
from ase.atoms import Atoms

def get_scaled_atomic_volume(new_atoms: Atoms):
    symbol_counts = pd.Series(new_atoms.get_chemical_symbols()).value_counts()
    unique_symbols = symbol_counts.index.tolist()
    # re.findall('[A-Za-z]{1,2}', new_atoms.get_chemical_formula())
    unique_nspecs = symbol_counts.values
     # [int(n) for n in re.findall('[0-9]+', new_atoms.get_chemical_formula())]
    atom_num : dict = { symb: num for symb, num in zip(unique_symbols, unique_nspecs)}
    vols_dict = {} 
    for s in unique_symbols:
        try:
            vols_dict[s] = (4/3)*np.pi*(mendeleev.element(s).atomic_radius/100)**3  
        except Exception as E:
            pdb.set_trace()
            pass
    try:
        total_atom_vol = np.sum([ vols_dict[s] * atom_num[s] for s in unique_symbols] )
    except Exception as E:
        pdb.set_trace()
        pass
    
    return total_atom_vol

import pdb

def decoratePOSCAR(taggedstrucname, species_dict : dict[str, str], return_replacings = False):
    strucname, occstring = taggedstrucname.split('-')
    replacings = {i+1: species_dict[tag] for i, tag in enumerate(occstring)}
    proto = read_vasp(f'PrototypeStructures/POSCAR_{strucname}_proto.vasp')
    new_symbols = [replacings[i] for i in proto.numbers]
    new_atoms = proto.copy()
    new_atoms.set_chemical_symbols(new_symbols)
    scaled_atomic_volume = get_scaled_atomic_volume(new_atoms)
    new_cell = new_atoms.cell * ( (scaled_atomic_volume / new_atoms.get_volume())**(1./3.) )
    new_atoms.set_cell(new_cell, scale_atoms = True)
    return_values = new_atoms
    if return_replacings :
        return_values = new_atoms, replacings
    return return_values

import pandas as pd 
from tqdm.auto import tqdm

def make_all_atoms_objects(list_of_binary_tags, species_dict={'A': 'Fe', 'B': 'Mo'}):
    binary_atoms = {}
    for tag in tqdm(list_of_binary_tags):
        this_atoms = decoratePOSCAR(tag, species_dict)
        formula = this_atoms.get_chemical_formula()
        formula = formula.replace('Fe','Fe_pv').replace('Mo','Mo_sv')
        index = formula+'.'+tag
        binary_atoms[index] = this_atoms
    return pd.Series(binary_atoms)
    

if __name__ == '__main__' : 
    binaryr = permutate('R', 2, 11)
    atoms_objects = make_all_atoms_objects(binaryr)
    atoms_objects.to_pickle('Fe-Mo/Atomsobjects/R_structures.pkl')




