import os
import shutil
import subprocess
import yaml

from fuzzers import utils
from fuzzers.afl import fuzzer as afl_fuzzer


def build():

    cflags = [
        '-lstdc++ -stdlib=libstdc++ -fsanitize-coverage=trace-pc-guard,no-prune -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope'
    ]
    utils.append_flags('CFLAGS', cflags)
    utils.append_flags('CXXFLAGS', cflags)

    os.environ['CC'] = 'wllvm'
    os.environ['CXX'] = 'wllvm++'
    os.environ['LLVM_COMPILER'] = 'clang'
    os.environ['FUZZER_LIB'] = '/afl/afl_integration/build_example/afl_llvm_rt_driver.a'

    with open('/src/benchmark.yaml') as f:
        benmark_data = yaml.load(f, Loader=yaml.FullLoader)

    fuzz_target = os.getenv('FUZZ_TARGET')
    prject_name = benmark_data['project']

    # build_dir = '/afl/afl_integration/build_example/out'
    build_dir = f'/src/{prject_name}/'
    os.makedirs(build_dir, exist_ok=True)
    # new_env = os.environ.copy()
    # print(os.environ['OUT'] )
    # raise
    utils.build_benchmark()


    # if fuzz_target:
    #   new_env['FUZZ_TARGET'] = os.path.join(build_dir, os.path.basename(fuzz_target))

    output_stream = subprocess.DEVNULL

    ft = os.path.join(build_dir, fuzz_target)
    subprocess.check_call(f"extract-bc {fuzz_target}".split(),
                          stdout=output_stream,
                          stderr=output_stream,
                          env=os.environ.copy(), cwd=build_dir)

    subprocess.check_call(f"/afl/libfuzzer_integration/llvm_11.0.1/build/bin/llvm-dis ./.{fuzz_target}.o.bc".split(),
        stdout=output_stream,
        stderr=output_stream,
        env=os.environ.copy(), cwd=build_dir)

    subprocess.check_call(f"python3 /afl/afl_integration/build_example/fix_long_fun_name.py ./.{fuzz_target}.o.ll".split(),
        stdout=output_stream,
        stderr=output_stream,
        env=os.environ.copy(), cwd=build_dir)


    os.makedirs(build_dir + f'cfg_out_{fuzz_target}', exist_ok=True)

    subprocess.check_call(f"opt -dot-cfg ../.{fuzz_target}.o_fix.ll".split(),
        stdout=output_stream,
        stderr=output_stream,
        env=os.environ.copy(), cwd=build_dir + f'cfg_out_{fuzz_target}')

    for  filename in os.listdir(build_dir + f'cfg_out_{fuzz_target}/'):
        if filename.endswith('.dot'):
            dst =filename[1:]
            src = build_dir + f'cfg_out_{fuzz_target}/' + filename 
            dst = build_dir + f'cfg_out_{fuzz_target}/' + dst

            os.rename(src, dst) 

    # subprocess.check_call(f"cp -a /afl/afl_integration/build_example/. .".split(),
    #     stdout=output_stream,
    #     stderr=output_stream,
    #     env=os.environ.copy(), cwd=build_dir)


    subprocess.check_call(f"python3 /afl/afl_integration/build_example/gen_graph.py ./.{fuzz_target}.o_fix.ll cfg_out_{fuzz_target}".split(),
        stdout=output_stream,
        stderr=output_stream,
        env=os.environ.copy(), cwd=build_dir, shell=True)

    shutil.copy('/afl/afl_integration/build_example/afl-fuzz_kscheduler',
                os.environ['OUT'])
    shutil.copy('/afl/afl_integration/build_example/gen_dyn_weight.py',
                os.environ['OUT'])
    os.environ['OUT'] += os.pathsep + os.pathsep.join(build_dir)



def fuzz(input_corpus, output_corpus, target_binary):
    afl_fuzzer.prepare_fuzz_environment(input_corpus)
    run_afl_fuzz(input_corpus, output_corpus, target_binary)


def run_afl_fuzz(input_corpus,
                 output_corpus,
                 target_binary,
                 additional_flags=None,
                 hide_output=False):
    """Run afl-fuzz."""
    # Spawn the afl fuzzing process.
    print('[run_afl_fuzz] Running target with afl-fuzz')
    subprocess.Popen('python3 ./gen_dyn_weight.py'.split(), shell=True)
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
    output_stream = subprocess.DEVNULL
    subprocess.check_call('echo 0 > signal'.split(), stdout=output_stream, stderr=output_stream)
    subprocess.check_call(command, stdout=output_stream, stderr=output_stream)

