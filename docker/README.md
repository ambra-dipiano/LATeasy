# build container 

docker build -t fermitool --network=host -f docker/Dockerfile .

# bootstrap the image 

sh bootstrap.sh fermitool [username]

# test the container with slurm 

## update the test_fermi_docker.ll file content
mkdir shared_dir
mkdir test
sbatch test_fermi_docker.ll

# start docker container #
docker run -it --user=root --network=host -v /etc/slurm/:/etc/slurm/ -v /etc/munge/:/etc/munge/ fermitool:slurm /bin/bash 

## start munge ##
munged -f 

###Try if you can connect with slurm###
squeue

###Now you can submit jobs.####
