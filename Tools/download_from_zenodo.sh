#!/bin/bash
#===============================================================================
#
#          FILE:  download_from_zenodo.sh
# 
#         USAGE:  ./download_from_zenodo.sh 
# 
#   DESCRIPTION: Download the data from zenodo
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Mariano Forti (MF), mariano.forti@ruhr-uni-bochum.de
#       COMPANY:  ICAMS
#       VERSION:  1.0
#       CREATED:  15.04.2026 11:03:43 CEST
#      REVISION:  ---
#===============================================================================

RECORD='https://zenodo.org/records/19427673/'
FILES=$RECORD/'files/'
ZIP=$FILES'FeMo_TCP_dataset.zip'
DESCRIPTION=$RECORD'ZENODO_DESCRIPTION.md'

if [ ! -f FeMo_TCP_dataset.zip ]; then
  if [ -f /home/mariano/CuadernoTrabajo/DatasetsML_2.0/zenodo_upload/FeMo_TCP_dataset.zip ]; then
    cp /home/mariano/CuadernoTrabajo/DatasetsML_2.0/zenodo_upload/FeMo_TCP_dataset.zip .
  else
    wget -O FeMo_TCP_dataset.zip $ZIP
  fi
fi
unzip FeMo_TCP_dataset

#echo "Dlownloading DESCRIPTION"
#if [ ! -f ZENODO_DESCRIPTION.md ]; then
#  wget  $DESCRIPTION
#fi


