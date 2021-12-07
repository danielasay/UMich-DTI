#!/bin/bash

###SBATCH --job-name=$subject
#SBATCH --mail-user=dasay@med.umich.edu
#SBATCH --mail-type=END,FAIL

#SBATCH --account=kboehnke99
#SBATCH --partition=standard

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

#### If you change cpus-per-task or mem, change them in the fmriprep command
#SBATCH --cpus-per-task=3
#SBATCH --mem=32gb

#SBATCH --time=6:00:00
#SBATCH --export=ALL

#### End SBATCH preamble

source /home/${USER}/.bash_profile
module load fsl/5.0.11


my_job_header

# Set participant name
participant=$subject

# Create a local directory in which to work
TMPDIR=$(mktemp -d /tmp/dasay-dtiMrtrix3.XXXXXXXXX)
cd $TMPDIR
mkdir BIDS processed work

# Set the names of the fmriprep diretories.  NOTE, processed and work
# cannot be in the BIDS directory
SOURCE_DIR=/scratch/seharte_root/seharte99/shared_data/expl
BIDS_DIR=$PWD/BIDS
OUTPUT_DIR=$PWD/processed
WORK_DIR=$PWD/work

# Get the needed BIDS data; print only the summary statistics from the copy
rsync -a --info=STATS /scratch/seharte_root/seharte99/shared_data/expl/explBIDS/$participant/combined/ ./BIDS

# Print some information about the run that might be useful
echo "#---------------------------------------------------------------------#"
echo "Running on           :  $(hostname -s)"
echo "Processor type       :  $(lscpu | grep 'Model name' | sed 's/[ \t][ ]*/ /g')"
echo "Assigned processors  :  $(cat /sys/fs/cgroup/cpuset/slurm/uid_${EUID}/job_${SLURM_JOBID}/cpuset.cpus)"
echo "Assigned memory nodes:  $(cat /sys/fs/cgroup/cpuset/slurm/uid_${EUID}/job_${SLURM_JOBID}/cpuset.mems)"
echo "======================================================================="
echo "/tmp space"
df -h /tmp
echo "======================================================================="
echo "Memory usage"
free
echo "#---------------------------------------------------------------------#"
echo

# Get the start time
start_time=$(date +%s)


# Run it
source /etc/profile.d/http_proxy.sh

cd BIDS

#### dwipreproc command

dwifslpreproc run-01_den.mif run-01_den_preproc.mif \
	 -nocleanup \
	 -pe_dir PA \
	 -rpe_pair -se_epi b0_pair.mif \
	 -eddy_options " --slm=linear --data_is_shelled"

finish_time=$(date +%s)

# Calculate run time and print in hh:mm format
printf "Run time:  %02d:%02d\n" $(echo "$run_time / 60" | bc) $(echo "$run_time % 60" | bc)

# Copy the results out for posterity
echo "Copying $OUTPUT_DIR/$participant to ${SOURCE_DIR}/processed"
mkdir -p ${SOURCE_DIR}/processed/
rsync -a --info=STATS $OUTPUT_DIR/* ${SOURCE_DIR}/processed/

# Change out of the $TMPDIR and remove it
cd
rm -rf $TMPDIR





