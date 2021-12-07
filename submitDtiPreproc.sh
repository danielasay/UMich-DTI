#!/bin/bash

for subject in $(cat dti_preproc_run1.txt); do

        export subject
        echo "Submitting $subject"
        sbatch --job-name=$subject --output=/scratch/seharte_root/seharte99/shared_data/expl/job_output/$subject-%j.log dtiPreprocSbatch.sh

done