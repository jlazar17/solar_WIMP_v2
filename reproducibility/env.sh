eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

############################# DIRECTORIES TO MODIFY ############################
export CHANNEL=5
export MASS=500
export DATADIR=$PWD/data/
export SCRIPTSDIR=$PWD/../scripts/
export SUBMITDIR=$PWD/../submit/
################################################################################

export LD_LIBRARY_PATH=$SROOT/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$SROOT/lib64:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$SROOT/include:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$SROOT/include:$CPLUS_INCLUDE_PATH

export CXX=g++
export CC=gcc
export SWSPACE=/data/ana/BSM/IC86_all_energy_solar_WIMP/
export SWBUILDPATH=$SWSPACE/software/local
export SWSOURCEPATH=$SWSPACE/software/src
export PREFIX=$SWBUILDPATH
export PATH=$SWBUILDPATH/bin:$PATH
export LD_LIBRARY_PATH=$SWBUILDPATH/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$SWBUILDPATH/lib64/:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$SWBUILDPATH/include/:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$SWBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export CXX_INCLUDE_PATH=$SWBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export PKG_CONFIG_PATH=$SWBUILDPATH/lib/pkgconfig:$SWBUILDPATH/lib64/pkgconfig:$PKG_CONFIG_PATH


export PKG_CONFIG_PATH=$SROOT/lib/pkgconfig:$SROOT/include:$PKG_CONFIG_PATH
export PYTHONPATH=$SWSPACE:$PYTHONPATH
export PYTHONPATH=$SWBUILDPATH/lib/python3.7/site-packages:$PYTHONPATH
export PYTHONPATH=$SWBUILDPATH/lib/:$PYTHONPATH
export PYTHONPATH=$SWSOURCEPATH/charon/:$PYTHONPATH
/data/user/jlazar/combo37/build/env-shell.sh
