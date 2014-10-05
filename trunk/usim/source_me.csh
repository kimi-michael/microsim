
#source this file before running usim --mkimyaga

if ( ! ($?USIM_ROOT) ) then
    echo "Error \$USIM_ROOT env variable must be defined"\
	 " it should point to usim root dir"
    exit 1
endif

modpath -v PYTHONPATH -n 1 `realpath $USIM_ROOT`
modpath -v PYTHONPATH -n 1 `realpath tests`
modpath -v PYTHONPATH -n 1 `realpath pydot-1.0.28`
