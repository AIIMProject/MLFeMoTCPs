from SourceDevelopementVersion import cutoffs_dict, pd
from math import pi


AtomsObjects = pd.read_pickle('CrCoW-sorted-POSCAR-initial-rescaled-AtomsObjects.pkl')

First_Structure = AtomsObjects.iloc[0]['atoms']

some_c14 = AtomsObjects[AtomsObjects.index.str.contains('C14')].sample(n=1)
distances = some_c14['atoms'][0].get_all_distances()
volume = some_c14['atoms'][0].get_volume()
thiscutoff = (cutoffs_dict['volume_factor']*volume)**(1/3)

# cutoffs_dict.index = cutoffs_dict.index.str.split('.').map(lambda l: l[1])

