#!/usr/bin/env bash -l

./clean.sh

export PYTHON_VERSION=`python3 -c 'import sys; version=sys.version_info[:3]; print("{0}.{1}.{2}".format(*version))'`

export whichConda=`which conda`

##install anaconda platform incase it is not installed already
if [ ${#whichConda} < 0 ]
then
    wget https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh
    bash Anaconda3-2023.03-Linux-x86_64.sh
    rm Anaconda3-2023.03-Linux-x86_64.sh
fi
    conda info

eval "$(conda shell.bash hook)"

conda create -n DynamicOptimizer python=$PYTHON_VERSION

conda install -c conda-forge ta-lib

pip install -r requirements.txt

echo "============================="\n
echo "DynamicOptimizer is ready for action"\n
echo "============================="\n