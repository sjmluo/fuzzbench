ARG parent_image
FROM $parent_image

RUN apt-get update && \
    apt-get install -y ninja-build texinfo libstdc++6 flex bison cmake gcc g++ python3-setuptools zlib1g build-essential

RUN git clone https://github.com/Dongdongshe/K-Scheduler.git /afl && \
    cd /afl

RUN cd /afl/libfuzzer_integration/llvm_11.0.1 && \
    mkdir build && cd build && \
    export CXXFLAGS="-pthread" && \
    cmake -G Ninja -DLLVM_ENABLE_PROJECTS="clang;compiler-rt" -DCMAKE_BUILD_TYPE=release -DLLVM_TARGETS_TO_BUILD=host ../llvm  && \
    ninja && cd ../../..

RUN export LLVM_COMPILER_PATH=/afl/libfuzzer_integration/llvm_11.0.1/build/bin && pip3 install --upgrade pip && pip3 install wllvm networkit ipdb

RUN cd /afl/afl_integration/build_example && \
    export PATH=/afl/libfuzzer_integration/llvm_11.0.1/build/bin:$PATH && \
    export LLVM_COMPILER=clang && \
    $CC -O2 -c -w -fPIC /afl/afl_integration/afl-2.52b_kscheduler/llvm_mode/afl-llvm-rt.o.c -o afl-llvm-rt.o && \
    cd /afl/qsym_integration/build_example/ && cp -r binutils_src build_afl && \
    cd build_afl && \
    CC=wllvm CXX=wllvm++ CFLAGS="-fsanitize-coverage=trace-pc-guard,no-prune -O2 -fsanitize=address" CXXFLAGS="-fsanitize-coverage=trace-pc-guard,no-prune -O2 -fsanitize=address" LDFLAGS=/afl/afl_integration/build_example/afl-llvm-rt.o ./configure && make -j


RUN cd /afl/afl_integration/build_example/ && \
    export PATH=/afl/libfuzzer_integration/llvm_11.0.1/build/bin:$PATH && \
    export LLVM_COMPILER=clang && export CC=wllvm && export CXX=wllvm++ && \
    export CFLAGS="-stdlib=libstdc++ -fsanitize-coverage=trace-pc-guard,no-prune -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope" && \
    export CXXFLAGS="-stdlib=libstdc++ -fsanitize-coverage=trace-pc-guard,no-prune -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope" && \
    $CC -O2 -c -w /afl/afl_integration/afl-2.52b_kscheduler/llvm_mode/afl-llvm-rt.o.c -o afl-llvm-rt.o && \
    $CXX -std=c++11 -O2 -c /afl/libfuzzer_integration/llvm_11.0.1/compiler-rt/lib/fuzzer/afl/afl_driver.cpp && \
    ar r afl_llvm_rt_driver.a afl_driver.o afl-llvm-rt.o && \
    export LDFLAGS=/afl/afl_integration/build_example/afl-llvm-rt.o


