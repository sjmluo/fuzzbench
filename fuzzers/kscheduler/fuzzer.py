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
    os.environ['OUT'] = build_dir
    utils.build_benchmark()


    # if fuzz_target:
    #   new_env['FUZZ_TARGET'] = os.path.join(build_dir, os.path.basename(fuzz_target))

    output_stream = subprocess.DEVNULL
    print('==========HERE=============')

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

    # print("for f in $(ls -a |grep '^\\.*'|grep dot);do mv $f ${f:1};done")

    # subprocess.check_call("for f in $(ls -a |grep '^\\.*'|grep dot);do mv $f ${f:1};done",
    #     stdout=output_stream,
    #     stderr=output_stream,
    #     env=os.environ.copy(), cwd=build_dir + f'cfg_out_{fuzz_target}')


    for  filename in os.listdir(build_dir + f'cfg_out_{fuzz_target}'):
        print(filename)
        if filename.endswith('.dot'):
            dst =filename[1:]
            src = build_dir + f'cfg_out_{fuzz_target}' + filename 
            dst = build_dir + f'cfg_out_{fuzz_target}' + dst

            os.rename(src, dst) 

    print('==========HERE=============')



    print('==========HERE=============')
    print(os.system(f'ls -apl {build_dir}'))
    print(os.system('which python3'))

    # print('ft:', ft)
    # print(os.system('find / -type f -name "*.bc"'))
    # print(os.system('ls -pl /src/freetype2/'))
    # print(os.system(new_env['FUZZ_TARGET']))
    # print('==============')
    # print(os.system('ls -pl /afl/afl_integration/build_example/'))
    # print(os.system('ls -pl /afl/afl_integration/build_example/out'))
    # print(os.system('ls -pl $OUT'))
    # print(os.system('echo $OUT'))
    # print(os.system('ls -pl $OUT'))
    # print(os.system('ls -pl /afl/libfuzzer_integration/llvm_11.0.1/build/bin/'))
    # print('{0}'.format(new_env['FUZZ_TARGET']))
    # os.system("chmod 777 $OUT")
    # print(os.system('ls -pl /src/freetype2/'))
    # print(os.system('pwd'))

    print('==========HERE=============')

    # subprocess.check_call(f"/afl/libfuzzer_integration/llvm_11.0.1/build/bin/llvm-dis /src/freetype2/.ftfuzzer.o.bc".split(),
    #     stdout=output_stream,
    #     stderr=output_stream,
    #     env=os.environ.copy())




    # &&   && {build_dir}/../python3 fix_long_fun_name.py {ft}.ll  && mkdir cfg_out_{0} && cd cfg_out_{0} && opt -dot-cfg ../{0}_fix.ll && for f in $(ls -a |grep '^\.*'|grep dot);do mv $f ${{f:1}};done && cd .. && python3 ./gen_graph.py {0}_fix.ll cfg_out_{0}

    # gen_dyn_weight(new_env['FUZZ_TARGET'])

    shutil.copy('/afl/afl_integration/build_example/afl-fuzz_kscheduler',
                os.environ['OUT'])
    shutil.copy('/afl/afl_integration/build_example/gen_dyn_weight.py',
                os.environ['OUT'])


def fuzz(input_corpus, output_corpus, target_binary):
    afl_fuzzer.prepare_fuzz_environment(input_corpus)
    run_afl_fuzz(input_corpus, output_corpus, target_binary)


def gen_dyn_weight(target_binary):
    output_stream = subprocess.DEVNULL

    # subprocess.check_call("cd /afl/afl_integration/build_example/", stdout=output_stream, stderr=output_stream)

    subprocess.check_call("extract-bc {0}".format(target_binary),
                          stdout=output_stream,
                          stderr=output_stream)
    subprocess.check_call(
        "llvm-dis {0}.bc && ./python3 fix_long_fun_name.py {0}.ll && mkdir cfg_out_{0} && cd cfg_out_{0} && opt -dot-cfg ../{0}_fix.ll && for f in $(ls -a |grep '^\.*'|grep dot);do mv $f ${{f:1}};done && cd .. && python3 ./gen_graph.py {0}_fix.ll cfg_out_{0}"
        .format(target_binary),
        stdout=output_stream,
        stderr=output_stream)


def run_afl_fuzz(input_corpus,
                 output_corpus,
                 target_binary,
                 additional_flags=None,
                 hide_output=False):
    """Run afl-fuzz."""
    # Spawn the afl fuzzing process.
    print('[run_afl_fuzz] Running target with afl-fuzz')
    subprocess.check_call('python3 ./gen_dyn_weight.py &',
                          stdout=output_stream,
                          stderr=output_stream)
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
