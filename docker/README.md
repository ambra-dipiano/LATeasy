# build container 

docker build -t fermitool --network=host -f docker/Dockerfile .

# bootstrap the image 

sh bootstrap.sh fermitool [username]

# test the container with slurm 

## update the test_fermi_docker.ll file content
mkdir shared_dir
mkdir test
sbatch test_fermi_docker.ll
