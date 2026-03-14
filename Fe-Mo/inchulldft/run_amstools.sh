export ASE_VASP_COMMAND="mpirun -n 64 /scratch/hpc-prf-mpccip/mpccip01/vasp5_pc2//vasp.5.4.4/vasp.5.4.4/build/std/vasp"
export VASP_PP_PATH=$WORK/vasp5/vasp.5.4.4
export AMS_STRUCTURE_REPOSITORY_PATH=$WORK/Projects/DatasetsML_2.0/Fe-Mo/data/Validation/inchull/
#ams_highthroughput setup.yaml -c vasp_tight.yaml  --verbose -rpfp -rep -q noctua2_64
ams_highthroughput setup.yaml -c vasp_tight.yaml  --verbose -rpfp -rep -q noctua2_64
# 13065963
#-u --rebuild-state-dict 
