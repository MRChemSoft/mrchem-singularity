"""
HPCCM recipe for MRChem Singularity image (OpenMP)

Contents:
  Ubuntu 20.04
  GNU compilers (upstream)

Generating recipe (stdout):
  $ hpccm --recipe recipe_omp.py --format singularity --singularity-version=3.2
"""

os_version="20.04"
mrchem_version="@_VERSION_@"
cmake_version="3.20.6"

# CentOS base image
Stage0 += baseimage(image=f"ubuntu:{os_version}", _as="build")

# GNU compilers
compiler = gnu()
Stage0 += compiler

# CMake
Stage0 += cmake(eula=True, version=cmake_version)

# Python 3
Stage0 += python(python2=False, python3=True)

# MRChem
Stage0 += packages(apt=["patch"])
Stage0 += generic_cmake(
    cmake_opts=["-D CMAKE_BUILD_TYPE=Release",
                "-D ENABLE_MPI=OFF",
                "-D ENABLE_OPENMP=ON",
                "-D ENABLE_ARCH_FLAGS=OFF",
    ],
    prefix="/usr/local/mrchem",
    url=f"http://github.com/MRChemSoft/mrchem/archive/v{mrchem_version}.tar.gz",
    directory=f"mrchem-{mrchem_version}",
)

# Runtime distributable stage
Stage1 += baseimage(image=f"ubuntu:{os_version}")
Stage1 += Stage0.runtime(_from="build")
Stage1 += environment(variables={"PATH": "$PATH:/usr/local/mrchem/bin"})
Stage1 += runscript(commands=["mrchem"])

Stage1 += label(metadata={
    "Author": "Stig Rune Jensen <stig.r.jensen@uit.no>",
    "Version": f'"v{mrchem_version}"',
    "Description": "MRChem program (OpenMP version)"
})

help_str="""
%help
    Shared memory parallel (OpenMP) build of MRChem on a Ubuntu-{os_version} base image.

    For a pure OpenMP run (n threads on one process) you can run the container
    just as the regular mrchem executable, here with input file molecule.inp:

        $ export OMP_NUM_THREADS=n
        $ ./<image-name>.sif molecule
"""
Stage1 += raw(singularity=help_str)
