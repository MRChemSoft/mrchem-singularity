"""
HPCCM recipe for MRChem Singularity image (MPI+OpenMP)

Contents:
  Ubuntu 18.04
  GNU compilers (upstream)
  OpenMPI
  OFED/MOFED
  PMI2 (SLURM)
  UCX

Generating recipe (stdout):
  $ hpccm --recipe recipe_mpi.py --format singularity --singularity-version=3.2
"""

os_version='18.04'
mrchem_version='1.0.1'
cmake_version='3.16.3'
openmpi_version='4.0.5'

# CentOS base image
Stage0 += baseimage(image='ubuntu:{}'.format(os_version), _as='build')

# GNU compilers
compiler = gnu()
Stage0 += compiler

# (M)OFED
Stage0 += mlnx_ofed()

# UCX
Stage0 += ucx(cuda=False, ofed=True)

# PMI2
Stage0 += slurm_pmi2()

# OpenMPI (use UCX instead of IB directly)
Stage0 += openmpi(cuda=False,
                  infiniband=False,
                  pmi='/usr/local/slurm-pmi2',
                  ucx='/usr/local/ucx',
                  toolchain=compiler.toolchain,
                  version=openmpi_version)

# CMake
Stage0 += cmake(eula=True, version=cmake_version)

# Python 3
Stage0 += python(python2=False, python3=True)

# MRChem
Stage0 += packages(apt=['patch'])
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D ENABLE_MPI=ON',
                                    '-D ENABLE_OPENMP=ON',
                                    '-D ENABLE_ARCH_FLAGS=OFF',
                                    '-D CXX_COMPILER=mpicxx'],
                        prefix='/usr/local/mrchem',
                        url='http://github.com/MRChemSoft/mrchem/archive/v{}.tar.gz'.format(mrchem_version),
                        directory='mrchem-{}'.format(mrchem_version))

# Runtime distributable stage
Stage1 += baseimage(image='ubuntu:{}'.format(os_version))
Stage1 += Stage0.runtime()
Stage1 += environment(variables={'PATH': '$PATH:/usr/local/mrchem/bin'})
Stage1 += runscript(commands=['mrchem'])

Stage1 += label(metadata={
    'Author': 'Stig Rune Jensen <stig.r.jensen@uit.no>',
    'Version': 'v{}'.format(mrchem_version),
    'Description': 'MRChem program (MPI+OpenMP version)',
    'Dependency': 'OpenMPI v4.0'
})

help_str="""
%help
    Hybrid parallel (MPI + OpenMP) build of MRChem using OpenMPI-{} on a
    Ubuntu-{} base image. Requires compatible OpenMPI version on the host.
    The image includes Mellanox OFED, UCX and PMI2 for compatibility with
    common HPC environments with InfiniBand and SLURM.

    For a pure OpenMP run (n threads on one process) you can run the container
    just as the regular mrchem executable, here with input file molecule.inp:

        $ export OMP_NUM_THREADS=n
        $ ./<image-name>.sif molecule

    In order to run with more that one MPI process you must first manually run
    the input parser to obtain the JSON input file. This is done by dry-running
    (--dryrun) the container on the main input file, here called molecule.inp:

        $ ./<image-name>.sif --dryrun molecule
    
    This will produce a new file molecule.json in the current directory which can
    be passed to the mrchem.x program inside the container using the singularity
    exec command:

        $ singularity exec <image-name>.sif mrchem.x mrchem.json

    To run in hybrid parallel (n threads on N processes) you should launch the
    singularity execution with mpirun/srun:

        $ export OMP_NUM_THREADS=n
        $ mpirun -np N singularity exec <image-name>.sif mrchem.x mrchem.json
""".format(openmpi_version, os_version)
Stage1 += raw(singularity=help_str)
