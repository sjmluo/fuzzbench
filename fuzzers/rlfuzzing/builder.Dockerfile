# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG parent_image
FROM $parent_image

# Install the necessary packages.
RUN apt-get update && \
    apt-get install -y wget libstdc++-5-dev libtool-bin automake flex bison \
                       libglib2.0-dev libpixman-1-dev python3-setuptools unzip \
                       gcc-5-plugin-dev build-essential python3-dev cmake ninja-build python-sysv-ipc apt-transport-https 


RUN echo deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial xenial >> /etc/apt/sources.list && wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && apt-get update && apt-get upgrade -y && \
    apt-get install -y clang-11 clang-tools-11 libc++1-11 libc++-11-dev \
                       libc++abi1-11 libc++abi-11-dev libclang1-11 libclang-11-dev \
                       libclang-common-11-dev libclang-cpp11 libclang-cpp11-dev liblld-11 \
                       liblld-11-dev liblldb-11 liblldb-11-dev libllvm11 libomp-11-dev \
                       libomp5-11 lld-11 lldb-11 llvm-11 llvm-11-dev llvm-11-runtime llvm-11-tools



# Why do some build images have ninja, other not? Weird.
RUN cd / && wget https://github.com/ninja-build/ninja/releases/download/v1.10.1/ninja-linux.zip && \
    unzip ninja-linux.zip && chmod 755 ninja && mv ninja /usr/local/bin

RUN pip3 install --upgrade pip && pip3 install sysv_ipc 

# Download afl++
RUN git clone https://github.com/sjmluo/RLFuzzing.git /afl
    
# Build afl++ without Python support as we don't need it.
# Set AFL_NO_X86 to skip flaky tests.
RUN cd /afl && \
    LLVM_CONFIG=llvm-config-11 make && make distrib && make install

