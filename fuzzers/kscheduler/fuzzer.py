import os
import shutil
import subprocess

from fuzzers import utils
from fuzzers.afl import fuzzer as afl_fuzzer

def build():


    cflags = ['-lstdc++ -stdlib=libstdc++ -fsanitize-coverage=trace-pc-guard,no-prune -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope']
    utils.append_flags('CFLAGS', cflags)
    utils.append_flags('CXXFLAGS', cflags)


    os.environ['CC'] = 'wllvm'
    os.environ['CXX'] = 'wllvm++'
    os.environ['LLVM_COMPILER'] = 'clang'
    os.environ['FUZZER_LIB'] = '/afl/afl_integration/build_example/afl_llvm_rt_driver.a'
    utils.build_benchmark()


    shutil.copy('/afl/afl_integration/build_example/afl-fuzz_kscheduler', os.environ['OUT'])
    shutil.copy('/afl/afl_integration/build_example/gen_dyn_weight.py', os.environ['OUT'])



def fuzz(input_corpus, output_corpus, target_binary):
    afl_fuzzer.prepare_fuzz_environment(input_corpus)
    gen_dyn_weight(target_binary)
    run_afl_fuzz(input_corpus, output_corpus, target_binary)


def gen_dyn_weight(target_binary):
    output_stream = subprocess.DEVNULL

    # subprocess.check_call("extract-bc {0} && llvm-dis {0}.bc && python /afl/afl_integration/build_example/fix_long_fun_name.py /afl/afl_integration/build_example/{0}.ll && mkdir /afl/afl_integration/build_example/cfg_out_{0} && cd cfg_out_{0} && opt -dot-cfg /afl/afl_integration/build_example/{0}_afl_asan_fix.ll && for f in $(ls -a |grep '^\.*'|grep dot);do mv $f ${{f:1}};done && cd .. && python /afl/afl_integration/build_example/gen_graph.py /afl/afl_integration/build_example/{0}_afl_asan_fix.ll cfg_out_{0}".format(target_binary), stdout=output_stream, stderr=output_stream)

    subprocess.check_call('python3 ./gen_dyn_weight.py &', stdout=output_stream, stderr=output_stream)

def run_afl_fuzz(input_corpus,
                 output_corpus,
                 target_binary,
                 additional_flags=None,
                 hide_output=False):
    """Run afl-fuzz."""
    # Spawn the afl fuzzing process.
    print('[run_afl_fuzz] Running target with afl-fuzz')
    command = [
        './afl-fuzz_kscheduler',
        '-i',
        input_corpus,
        '-o',
        output_corpus,
        # Use no memory limit as ASAN doesn't play nicely with one.
        '-m',
        'none',
        '-t',
        '1000+',  # Use same default 1 sec timeout, but add '+' to skip hangs.
    ]
    # Use '-d' to skip deterministic mode, as long as it it compatible with
    # additional flags.
    if not additional_flags:
        command.append('-d')
    if additional_flags:
        command.extend(additional_flags)
    dictionary_path = utils.get_dictionary_path(target_binary)
    if dictionary_path:
        command.extend(['-x', dictionary_path])
    command += [
        '--',
        target_binary,
        # Pass INT_MAX to afl the maximize the number of persistent loops it
        # performs.
        '2147483647'
    ]
    print('[run_afl_fuzz] Running command: ' + ' '.join(command))
    output_stream = subprocess.DEVNULL if hide_output else None
    subprocess.check_call(command, stdout=output_stream, stderr=output_stream)

