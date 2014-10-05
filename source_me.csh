
modpath -n 1 -v USIM_ROOT `realpath ./usim`
modpath -n 1 -v DUT_ROOT  `realpath ./uarc_dev`

modpath -n 1 -v PATH $USIM_ROOT
modpath -n 1 -v PATH $DUT_ROOT

cd $USIM_ROOT
source source_me.csh

cd $DUT_ROOT
source ./source_me.csh
cd ../
