#!/usr/bin/env bash

# Based on gist.github.com/gboudreau/install-ffmpeg-amazon-linux.sh
# and https://trac.ffmpeg.org/wiki/CompilationGuide/Centos
if [ "`/usr/bin/whoami`" != "root" ]; then
    echo "You need to execute this script as root."
    exit 1
fi

yum -y update
yum -y install autoconf automake bzip2 cmake freetype-devel gcc gcc-c++ git
yum -y install libtool make mercurial nasm pkgconfig zlib-devel openssl libssl-dev openssl-devel

cd /opt
wget http://www.nasm.us/pub/nasm/releasebuilds/2.13.01/nasm-2.13.01.tar.xz
tar -xf nasm-2.13.01.tar.xz
cd nasm-2.13.01
./configure --prefix=/usr && make && make install

cd /opt
git clone --depth 1 http://git.videolan.org/git/x264
cd x264
PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static
make
make install
echo

cd /opt
hg clone https://bitbucket.org/multicoreware/x265
cd x265/build/linux
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED:bool=off ../../source
make
make install
echo

cd /opt
curl -O http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg


export CFLAGS="-I/usr/local/ssl/include -L/usr/local/ssl/lib -Wl,-rpath=/usr/local/ssl/lib"
CFLAGS="$CFLAGS" CXXFLAGS="$CFLAGS"
PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib -ldl" \
  --bindir="$HOME/bin" --pkg-config-flags="--static" \
  --enable-gpl \
  --enable-libx264 \
  --enable-libx265 \
  --disable-ffplay \
  --enable-openssl \
  --enable-nonfree
make
make install
hash -r


# Test the resulting ffmpeg binary
# cp $HOME/bin/ffmpeg /usr/bin/
# cp $HOME/bin/ffprobe /usr/bin/
# cp $HOME/bin/ffserver /usr/bin/
# cp $HOME/bin/vsyasm /usr/bin/
# cp $HOME/bin/x264 /usr/bin/
# cp $HOME/bin/yasm /usr/bin/
# cp $HOME/bin/ytasm /usr/bin/


# ffmpeg -version