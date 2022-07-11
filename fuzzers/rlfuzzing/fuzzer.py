import os
import shutil
import subprocess

from fuzzers.aflplusplus import fuzzer as aflplusplus_fuzzer


def build():
    """Build benchmark."""
    aflplusplus_fuzzer.build('qemu')

    shutil.copy('/afl/afl-fuzz', os.environ['OUT'])
    shutil.copy('/afl/src/RLFuzzing.py', os.environ['OUT'])

def fuzz(input_corpus, output_corpus, target_binary):
    """Run fuzzer."""
    # Get LLVMFuzzerTestOneInput address.
    subprocess.Popen('python3 ./RLFuzzing.py &', shell=True)
    nm_proc = subprocess.run([
        'sh', '-c',
        'nm \'' + target_binary + '\' | grep -i \'T afl_qemu_driver_stdin\''
    ],
                             stdout=subprocess.PIPE,
                             check=True)
    target_func = "0x" + nm_proc.stdout.split()[0].decode("utf-8")
    print('[fuzz] afl_qemu_driver_stdin_input() address =', target_func)

    # Fuzzer options for qemu_mode.
    flags = ['-Q', '-c0']
#     flags = ['-Q', '-c0', '-p', 'explore']

    
    os.environ['AFL_QEMU_PERSISTENT_ADDR'] = target_func
    os.environ['AFL_ENTRYPOINT'] = target_func
    os.environ['AFL_QEMU_PERSISTENT_CNT'] = "1000000"
    os.environ['AFL_QEMU_DRIVER_NO_HOOK'] = "1"
    aflplusplus_fuzzer.fuzz(input_corpus,
                            output_corpus,
                            target_binary,
                            flags=flags)


