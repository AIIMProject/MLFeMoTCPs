def permutate(structurename,Nelements,NWyckoff):
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



if __name__ == '__main__' : 

    binaryR = permutate('R',2,11)
    print('structures: ',len(binaryR), '     target: ',2**11)
    print(binaryR)

    for R in binaryR: 
        generatePOSCAR(R)

