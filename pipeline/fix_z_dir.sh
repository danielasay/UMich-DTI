#!/bin/bash

module load mrtrix

cd /scratch/seharte_root/seharte99/shared_data/expl/explBIDS

for sub in reh*; do
	cd $sub/combined
	echo "running mrgrid on subject" $sub 
	mrgrid run-01_den.mif pad -axis 2 0,1 out.mif
	rm run-01_den.mif
	mrconvert out.mif run-01_den.mif
	rm out.mif
	cd ../..
done
