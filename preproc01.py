### This scripts has functions that will: 
# 1) copy nifti data from raw dir to dtiProc, both fieldmaps and dti
# 2) label dti and fieldmap data as PA and AP, respectively
# 3) convert the data from nii to mif format and combine with its bvec and bval files
# 4) compare the number of volumes in mif file and bvec/bval files, all 3 should be equal
# 5) run dwi_denoise and calculate residual
# 6) optionally run a visual inspection on residuals
# 7) extract and combine reverse and primary phase encoding directions - primary == PA, reverse == AP


def copyData():
	pass


def renameAndConvert():
	pass


def compareVolumes():
	pass


def dwiDenoise():
	pass


def visualInspection():
	pass


def combinePhaseEncoding():
	pass
