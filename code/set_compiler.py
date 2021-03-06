import platform
import os.path

def install():
    if platform.system() == 'Darwin':
        # most OSX machines now use clang-based compilers.
        # clang only recently got support for OpenMP.
        # search for a good compiler
        if os.path.exists('/usr/local/bin/clang-omp'):
            os.environ['CC'] = '/usr/local/bin/clang-omp'
            print("Compiling with /usr/local/bin/clang-omp")
        elif os.path.exists('/usr/local/bin/gcc-5'):
            os.environ['CC'] = '/usr/local/bin/gcc-5'
            print("Compiling with /usr/local/bin/gcc")
        else:
            print("No definitely good compiler found, things may not work.")
