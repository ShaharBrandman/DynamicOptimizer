pip install -r requirements

wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz

tar -xzf ta-lib-0.4.0-src.tar.gz

cd ta-lib

./configure --prefix=/usr

make

make install

mv ta-lib talib