#!/bin/bash

cd {{workdir}}
version=1.050
url=https://fastjet.hepforge.org/contrib/downloads/fjcontrib-{{version}}.tar.gz
local_file={{workdir}}/fjcontrib-{{version}}.tar.gz
{{softbuild}} --download {{url}} --output {{local_file}}
tar zxvf {{local_file}}
srcdir={{workdir}}/fjcontrib-{{version}}
cd {{srcdir}}
# this produces only static libs
./configure --fastjet-config={{prefix}}/bin/fastjet-config --prefix={{prefix}} && make -j all && make check && make install
# add a cmake for dynamic libs!
exit $?
