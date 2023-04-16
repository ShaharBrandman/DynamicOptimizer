wget https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh

chmod +x Anaconda3-2023.03-Linux-x86_64.sh

sudo bash Anaconda3-2023.03-Linux-x86_64.sh

conda env create -f enviroment.yaml

conda activate DynamicOptimizer

wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz

tar -xzf ta-lib-0.4.0-src.tar.gz

cd ta-lib

./configure --prefix=/usr

make

make install

mv ta-lib talib