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



RUN 

RUN echo deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial xenial >> /etc/apt/sources.list && wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && apt-get update && apt-get upgrade -y && \
    apt-get install -y clang-12 clang-tools-12 libc++1-12 libc++-12-dev \
                       libc++abi1-12 libc++abi-12-dev libclang1-12 libclang-12-dev \
                       libclang-common-12-dev libclang-cpp12 libclang-cpp12-dev liblld-12 \
                       liblld-12-dev liblldb-12 liblldb-12-dev libllvm12 libomp-12-dev \
                       libomp5-12 lld-12 lldb-12 llvm-12 llvm-12-dev llvm-12-runtime llvm-12-tools 



# Why do some build images have ninja, other not? Weird.
RUN cd / && wget https://github.com/ninja-build/ninja/releases/download/v1.10.1/ninja-linux.zip && \
    unzip ninja-linux.zip && chmod 755 ninja && mv ninja /usr/local/bin

RUN pip3 install --upgrade pip && pip3 install sysv_ipc 

# Download afl++
RUN git clone https://github.com/sjmluo/RLFuzzing.git /afl
    
# Build afl++ without Python support as we don't need it.
# Set AFL_NO_X86 to skip flaky tests.
RUN cd /afl && \
    LLVM_CONFIG=llvm-config-12 make && make distrib && make install

