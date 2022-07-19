#!/bin/bash



# [split the data into its respective volumes]
echo 'Splitting Volumes...'
fslsplit dti.nii dti_split -t
# [merge the rev pol data with slice 0]
echo 'merging volumes...'
fslmerge -t FM_vols.nii fm_rev_pol.nii dti_split0000.nii
# [clean up directory]
rm dti_split*
# [extract one slice]
echo 'extracting slice...'
fslroi FM_vols.nii FM_oneslice.nii 0 -1 0 -1 0 1 0 -1 
# [merge it to the data]
echo 'merging into padded data...'
fslmerge -z FM_padded FM_oneslice FM_vols.nii
# [run topup on FM_padded]
echo 'running topup...'
topup --imain=FM_padded.nii --datain=datain.txt --config=b02b0.cnf --out=my_topup_results --iout=fieldmap_b0 --fout=calculated_fm
# [get rid of last volume in fieldmap]
echo 'removing last volume'
fslsplit fieldmap_b0.nii final_fieldmap -t
mv final_fieldmap0000.nii.gz final_fieldmap.nii.gz 
rm final_fieldmap0001.nii.gz 


# [clean up]
#rm dti_split0000.nii.gz
## [unzip .gz file]
#gunzip FM_vols.nii.gz
## [clean up directory]
#rm *.gz