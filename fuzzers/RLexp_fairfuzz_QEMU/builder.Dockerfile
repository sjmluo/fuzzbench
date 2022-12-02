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

RUN apt-get update && \
    apt-get install wget libstdc++-5-dev libtool-bin automake -y && \
    apt-get install flex bison libglib2.0-dev libpixman-1-dev -y

# Set AFL_NO_X86 to skip flaky tests.
RUN git clone https://github.com/carolemieux/afl-rb.git /afl && \
    cd /afl && \
    AFL_NO_X86=1 make && \
    unset CFLAGS && unset CXXFLAGS && \
    cd qemu_mode && ./build_qemu_support.sh

RUN cd / && git clone https://github.com/vanhauser-thc/qemu_driver && \
    cd /qemu_driver && \
    git checkout 8ad9ad589b4881552fa7ef8b7d29cd9aeb5071bd && \
    make && \
    cp -fv libQEMU.a /libAFLDriver.a