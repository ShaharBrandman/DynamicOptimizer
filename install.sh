#!/usr/bin/sh
##
## This script requires anaconda installed and added to enviroments varibale
##
##  Anaconda3 2023.03 Linux Install repo:
##  https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh
## Simply wget it :)

./clean.sh

git clone https://www.github.com/ShaharBrandman/bybitHTTPX.git

export PYTHON_VERSION=`python3 -c 'import sys; version=sys.version_info[:3]; print("{0}.{1}.{2}".format(*version))'`

echo "PYTHON_VERSION: ${PYTHON_VERSION}"

export ANACONDA_PATH=which conda

if [ ${#ANACONDA_PATH} > 0 ]
then
    ##eval "$(conda shell.bash hook)"
    echo "Creating env..."
    conda create -n DynamicOptimizer python=$PYTHON_VERSION

    conda install -c conda-forge ta-lib
    echo "Installing TA-lib with conda"
    pip install -r requirements.txt
    echo "Installing dependencies from requirements.txt with pip"
    conda info

    echo "Type conda activate DynamicOptimizer to start the enviroment"
else
    echo "Anaconda is not installed or seem to not be found, try exporting the path correctly or reinstalling the entire platform"
fi