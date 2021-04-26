[![https://singularityhub.github.io/singularityhub-docs/assets/img/hosted-singularity--hub-%23e32929.svg](https://singularityhub.github.io/singularityhub-docs/assets/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/4912) 

### Generate new recipes using HPC Container Maker (HPCCM)

    $ hpccm --recipe <recipe_name>.py --format singularity --singularity-version=3.2 > recipes/Singularity.<version-tag>

### Build Singularity image locally

    $ sudo singularity build <image-name>.sif recipes/Singularity.<version-tag>

### Build Singularity image remotely on Singularity Hub

    $ git add recipes/Singularity.<version-tag>
    $ git commit -m "Add recipe for <version-tag>"
    $ git push

### Pull Singularity image from Singularity Hub

    $ singularity pull --name <image-name>.sif shub://MRChemSoft/mrchem-singularity:<version-tag>

### Run Singularity container (non MPI)

    $ singularity exec <image-name>.sif mrchem molecule

### Run Singularity container (MPI)

    $ singularity exec <image-name>.sif mrchem -D molecule
    $ mpirun singularity exec <image-name>.sif mrchem.x molecule.json
