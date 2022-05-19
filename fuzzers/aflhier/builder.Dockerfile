ARG parent_image
FROM $parent_image

RUN apt-get update && \
    apt-get install -y wget libstdc++-5-dev libtool-bin automake flex bison \
                       libglib2.0-dev libpixman-1-dev python3-setuptools unzip \
                       build-essential python3-dev clang llvm

RUN cd / && git clone https://github.com/bitsecurerlab/aflplusplus-hier.git /aflhier && \
    cd /aflhier

RUN cd /aflhier && \
    unset CFLAGS && unset CXXFLAGS && \
    AFL_NO_X86=1 CC=clang PYTHON_INCLUDE=/ make && \
    cd qemu_mode && ./build_qemu_support.sh && cd ..

