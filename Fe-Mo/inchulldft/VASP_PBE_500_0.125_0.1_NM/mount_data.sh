for dir in Fe Mo FeMo; do
  if [ ! -d "$dir" ]; then
    mkdir "$dir"
  fi
  if mountpoint -q $dir; then
    echo "$dir is already mounted."
  else
    echo "Mounting $dir..."
    case $HOSTNAME in
    "mlaptop")
      echo "using bindfs to mount local directory"
      bindfs /WorkData/VASP5_PBE_500_0.125_0.1_NM/"$dir"_inchulldft $dir
      ;;
    "aberdeen"|"marauder")
      echo "using sshfs to mount marauder directory"
      sshfs marauder:/archive/mariano/VASP5_PBE_500_0.125_0.1_NM/"$dir"_inchulldft $dir
      ;;
    esac
  fi
done
#sshfs marauder:/archive/mariano/VASP5_PBE_500_0.125_0.1_NM/Fe_inchulldft Fe
#sshfs marauder:/archive/mariano/VASP5_PBE_500_0.125_0.1_NM/Mo_inchulldft Mo
#sshfs marauder:/archive/mariano/VASP5_PBE_500_0.125_0.1_NM/FeMo_inchulldft FeMo
