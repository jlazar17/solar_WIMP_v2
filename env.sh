eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`

############################# DIRECTORIES TO MODIFY ############################
export BASE_DIR=/data/ana/BSM/IC86_all_energy_solar_WIMP/
export CONDOR_LOGS_DIR=/home/jlazar/condor_logs/
################################################################################

export PLOT_DIR=$BASE_DIR/plots/
export DATA_DIR=$BASE_DIR/data/

export LD_LIBRARY_PATH=$SROOT/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$SROOT/lib64:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$SROOT/include:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$SROOT/include:$CPLUS_INCLUDE_PATH

export CXX=g++
export CC=gcc
export SWSPACE=/data/user/jlazar/software/solar/
export SWBUILDPATH=$SWSPACE/local
export SWSOURCEPATH=$SWSPACE/sources
export PREFIX=$SWBUILDPATH
export PATH=$SWBUILDPATH/bin:$PATH
export LD_LIBRARY_PATH=$SWBUILDPATH/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$SWBUILDPATH/lib64/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/cvmfs/icecube.opensciencegrid.org/py2-v3/Ubuntu_14.04_x86_64/lib/:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=$SWBUILDPATH/include/:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=$SWBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export CXX_INCLUDE_PATH=$SWBUILDPATH/include/:$CPLUS_INCLUDE_PATH
export PKG_CONFIG_PATH=$SWBUILDPATH/lib/pkgconfig:$SWBUILDPATH/lib64/pkgconfig:$PKG_CONFIG_PATH


export PKG_CONFIG_PATH=$SROOT/lib/pkgconfig:$SROOT/include:$PKG_CONFIG_PATH
export PYTHONPATH=$SWBUILDPATH/lib/python3.7/site-packages:$PYTHONPATH
export PYTHONPATH=$SWBUILDPATH/lib/:$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$BASE_DIR
export BOOST_ROOT=$SROOT
export HDF5_DISABLE_VERSION_CHECK=1
export HDF5_USE_FILE_LOCKING='FALSE'
/data/user/jlazar/combo37/build/env-shell.sh
