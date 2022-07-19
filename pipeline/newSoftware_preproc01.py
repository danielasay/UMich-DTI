### This scripts has functions that will: 
# 1) copy nifti data from raw dir to dtiProc, both fieldmaps and dti
# 2) label dti and fieldmap data as PA and AP, respectively
# 3) convert the data from nii to mif format and combine with its bvec and bval files
# 4) compare the number of volumes in mif file and bvec/bval files, all 3 should be equal
# 5) run dwi_denoise and calculate residual
# 6) optionally run a visual inspection on residuals
# 7) extract and combine reverse and primary phase encoding directions - primary == PA, reverse == AP

# It is recommended to run this script on a linux screen as to avoid crashes and incomplete processing steps
# See https://linuxize.com/post/how-to-use-linux-screen/ for details


import shutil
import os
import subprocess
import pandas as pd
import nibabel as nib
import numpy as np
import time

rawSubDir = "/PROJECTS/REHARRIS/explosives/raw/"
subDir = "/PROJECTS/REHARRIS/explosives/dtiProc/subs/"
rawPath = "/DTI"


# this function will check if the mrtrix module has been loaded. If it hasn't, the user will be prompted to the program will qui

def checkMrtrix():
	print("please make sure you've run `module load mrtrix` in the terminal before running this script!\nComment out this function on line 324 once you've loaded it.")
	exit()


# this function will create a subject directory and dti and fieldmap sub-directories in the dtiProc/subs dir

def makeSubDirs(subDir, rawSubDir):
	for sub in getSubList(rawSubDir):
		os.chdir(subDir)
		if os.path.isdir(sub):
			continue
		else:
			os.makedirs(sub)
			os.chdir(sub)
			os.makedirs("dti")
			os.makedirs("fieldmaps")

# this function will create a list of subjects to process if their data was collected using the new scanner software AND createFieldMap.py has successfully run

def getSubList(rawSubDir):
	os.chdir(rawSubDir)
	subList = []
	for sub in os.listdir():
		os.chdir(sub)
		if os.path.isdir("DTI"):
			os.chdir("DTI")
			if os.path.isfile("dti.nii") and os.path.isfile("final_fieldmap.nii.gz"):
				subList.append(sub)
		os.chdir(rawSubDir)
	return subList

# if subject data has not already been copied, this function will copy it over from raw to dtiProc

def copyData(subDir, rawSubDir, rawPath):
	print("Copying over raw data...")
	for sub in getSubList(rawSubDir):
		dataPath = rawSubDir + sub + rawPath
		newDtiPath = subDir + sub + "/dti"
		dataCopied = checkIfDataCopied(newDtiPath, sub, False)
		if dataCopied is False:
			dtiCopyList = ["/abcd_edit.bval", "/abcd_edit.bvec", "/dti.nii"]
			for file in dtiCopyList:
				source = dataPath + file
				destination = newDtiPath
				print("Copying " + file + " for subject " + sub)
				shutil.copy(source, destination)
		fieldmaps = rawSubDir + sub + rawPath
		newFieldmapPath = subDir + sub + "/fieldmaps"
		dataCopied = checkIfDataCopied(newFieldmapPath, sub, True)
		if dataCopied is False:
			fmapCopyList = ["/final_fieldmap.nii.gz"]
			for file in fmapCopyList:
				source = fieldmaps + file
				destination = newFieldmapPath
				print("Copying " + file + " for subject " + sub)
				shutil.copy(source, destination)

# This function will ensure that the dti and fieldmap data are the same dimensions

def resample(rawSubDir, subDir):
	for sub in getSubList(rawSubDir):
		print("Resampling the data for subject " + sub)
		dtiNiiPath = subDir + sub + "/dti/dti.nii"
		fieldmapPath = subDir + sub + "/fieldmaps"
		os.chdir(fieldmapPath)
		shutil.copy(dtiNiiPath, os.getcwd())
		resampleCommand = "3dresample -master dti.nii -prefix new_fieldmap.nii -input final_fieldmap.nii.gz"
		proc = subprocess.Popen(resampleCommand, shell=True, stdout=subprocess.PIPE)
		proc.wait()
		os.remove("dti.nii")
		time.sleep(.1)



# this function will check if the raw data for a given subject has already been copied from raw to dtiProc

def checkIfDataCopied(dataPath, sub, fieldmap):
	os.chdir(dataPath)
	dirContents = os.listdir()
	if dirContents:
		print("Dti data already copied for subject: " + sub) if fieldmap is False else print("Fieldmap data already copied for subject: " + sub)
		return True
	else:
		return False


# function will convert dti and fieldmap data from .nii to .mif format.

def convert(fieldmap, sub):
	if fieldmap is False:
		if os.path.isfile("already_converted.txt"):
			print("Dti files have already been combined and converted to .mif format for subject " + sub)
			return
		print("Converting dti files for subject: " + sub)
		convertToMif = f"""
			mrconvert \
			dti.nii \
			run-01_dwi.mif \
			-fslgrad abcd_edit.bvec abcd_edit.bval
		"""
		proc1 = subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		subprocess.run(['touch', 'already_converted.txt'])
	else:
		if os.path.isfile("already_converted.txt"):
			print("Fmap files have already been combined and converted to .mif format for subject " + sub)
			return
		print("Converting fmap files for subject: " + sub)
		convertToMif = f"""
			mrconvert \
			new_fieldmap.nii \
			fieldmap.mif 
		"""
		proc2 = subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		subprocess.run(['touch', 'already_converted.txt'])


# go into each subject directory and call convert() function

def renameAndConvert(subDir):
	print("Converting files from nii to mif format...")
	for sub in getSubList(rawSubDir):
		# Go into dti directory for the sub and convert data to .mif
		os.chdir(subDir)
		dtiData = sub + "/dti"
		os.chdir(dtiData)
		convert(False, sub) # False indicates not fieldmap data
		os.chdir(subDir)
		fmapData = sub + "/fieldmaps"
		os.chdir(fmapData)
		convert(True, sub) # True indicates fieldmap data


# helper function to the compareVolumes function. Not necessary.

def checkIfEqual(array):
	array = iter(array)
	try:
		first = next(array)
	except StopIteration:
		return True
	return all(first == x for x in array)


# optional function to verify that volumes are consistent across files. This function may not have as much use with new software.

def compareVolumes(subDir):
	print("Checking that volume numbers are consistent across nii, bvec and bval files...")
	for sub in getSubList(rawSubDir):
		dtiVolumes = []
		dtiSubjectDir = subDir + sub + "/dti"
		os.chdir(dtiSubjectDir)
		#	print("Comparing dti file values for subject: " + sub + "...")
		dim4 = nib.load("run-01.nii")
		dtiVolumes.append(dim4.shape[3])
		bvecCmd = "cat abcd_edit.bvec > bvec.txt"
		proc1 = subprocess.Popen(bvecCmd, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		dtiVolumes.append(np.loadtxt('bvec.txt', dtype='str').shape[1])
		bvalCmd = "cat abcd_edit.bval > bval.txt"
		proc2 = subprocess.Popen(bvalCmd, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		dtiVolumes.append(np.loadtxt('bval.txt', dtype='str').shape[0])
		if not checkIfEqual(dtiVolumes):
			print("Dti volume numbers not equal for subject: " + sub + "\nThis is the current working directory:")
			os.getcwd()
			print("Killing script...")
			sys.exit()
		# Run check for fmap data
		fmapVolumes = []
		fmapSubjectDir = subDir + sub + "/fieldmaps"
		os.chdir(fmapSubjectDir)
		#print("Comparing fieldmap file values for subject: " + sub + "...")
		dim4 = nib.load("fieldmap.nii")
		fmapVolumes.append(dim4.shape[3])
		bvecCmd = "cat fieldmap.bvec > bvec.txt"
		proc3 = subprocess.Popen(bvecCmd, shell=True, stdout=subprocess.PIPE)
		proc3.wait()
		dtiVolumes.append(np.loadtxt('bvec.txt', dtype='str').shape[1])
		bvalCmd = "cat fieldmap.bval > bval.txt"
		proc4 = subprocess.Popen(bvalCmd, shell=True, stdout=subprocess.PIPE)
		proc4.wait()
		dtiVolumes.append(np.loadtxt('bval.txt', dtype='str').shape[0])
		if not checkIfEqual(fmapVolumes):
			print("Fmap volume Numbers not equal for subject: " + sub + "\nThis is the current working directory:")
			os.getcwd()
			print("Killing script...")
			sys.exit()
	print("Volume numbers are consistent for all subs!")


# verify that dwi_denoise has not already been run on the subject

def checkNoiseFile(sub):
	if os.path.isfile("run-01_den.mif"):
		print("dwi_denoise has already been run on subject: " + sub)
		return True
	else:
		return False


# run mrtrix function dwidenoise

def dwiDenoise(subDir):
	print("Running dwi_denoise on subjects...")
	for sub in getSubList(rawSubDir):
		dtiSubjectDir = subDir + sub + "/dti"
		os.chdir(dtiSubjectDir)
		if not checkNoiseFile(sub):
			print("Running on " + sub)
			denoise = "dwidenoise run-01_dwi.mif run-01_den.mif -noise noise.mif"
			proc = subprocess.Popen(denoise, shell=True, stdout=subprocess.PIPE)
			proc.wait()
		else:
			continue


def checkResidFile(sub):
	return False
#	if os.path.isfile("residual.mif"):
#		print("Residuals have already been calculated for subject: " + sub)
#		return True
#	else:
#		return False

# entirely optional function to do a visual inspection. Does not consistenly work across different machines.

def visualInspection(subDir):
	print("Calculating residuals on subjects...")
	for sub in getSubList(rawSubDir):
		dtiSubjectDir = subDir + sub + "/dti"
		os.chdir(dtiSubjectDir)
		if not checkResidFile(sub):
			print("Running on " + sub)
			residuals = "mrcalc run-01_dwi.mif run-01_den.mif -subtract residual.mif"
			proc1 = subprocess.Popen(residuals, shell=True, stdout=subprocess.PIPE)
			proc1.wait()
		else:
			continue
		visual = input("Would you like to do a visual inspection of subject: " + sub + "'s data?\nEnter 'yes' or 'no': ")
		if visual == "yes":
			view = "mrview residual.mif"
			proc2 = subprocess.Popen(view, shell=True, stdout=subprocess.PIPE)
			proc2.wait()
		else:
			continue


# this function will create a B0 image that combines the dti and fieldmap data 

def createB0(subDir):
	#Get b0 image
	for sub in getSubList(rawSubDir):
		currentSub = subDir + sub
		os.chdir(currentSub)
		if not os.path.isdir("combined"):
			os.makedirs("combined")
			combinedDir = os.getcwd() + "/combined"
			os.chdir("fieldmaps")
			shutil.copy("fieldmap.mif", combinedDir)
		print("Creating B0 image for subject: " + sub)
		# get mean for fmaps
		#1os.chdir("fieldmaps")
		#1fmapB0 = "mrconvert fieldmap.mif - | mrmath - mean meanReversed.mif -axis 3"
		#1proc1 = subprocess.Popen(fmapB0, shell=True, stdout=subprocess.PIPE)
		#1proc1.wait()
		#1shutil.copy("meanReversed.mif", combinedDir)
		os.chdir(currentSub)
		# get mean for dti
		os.chdir("dti")
		dtiB0 = "dwiextract run-01_den.mif - -bzero | mrmath - mean meanPrimary.mif -axis 3"
		proc2 = subprocess.Popen(dtiB0, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		shutil.copy("meanPrimary.mif", combinedDir)
		shutil.copy("run-01_den.mif", combinedDir)
		# combine means into b0 image
		os.chdir(combinedDir)
		meanB0 = "mrcat fieldmap.mif meanPrimary.mif -axis 3 b0_pair.mif"
		proc3 = subprocess.Popen(meanB0, shell=True, stdout=subprocess.PIPE)
		proc3.wait()

def fixDataStrides(subDir):
	"""
	This is to be run when the data strides read as anything else besides [-1 2 3 4]
	Use mrinfo to view data strides. This is a fix after dwifslpreproc would not run.
	"""
	for sub in getSubList(rawSubDir):
		currentSub = subDir + sub + "/combined"
		os.chdir(currentSub)
		shutil.copy("/home/dasay/diffusion/abcd_edit.bval", os.getcwd())
		shutil.copy("/home/dasay/diffusion/abcd_edit.bvec", os.getcwd())
		mifToNii = "mrconvert run-01_den.mif tmp.nii"
		proc1 = subprocess.Popen(mifToNii, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		os.remove("run-01_den.mif")
		niiToMif = "mrconvert tmp.nii run-01_den.mif -fslgrad abcd_edit.bvec abcd_edit.bval"
		proc2 = subprocess.Popen(niiToMif, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		os.remove("tmp.nii")




# run all the functions that you'd like to

def runAll(subDir, rawSubDir, rawPath):
	checkMrtrix()
	makeSubDirs(subDir, rawSubDir)
	copyData(subDir, rawSubDir, rawPath)
	resample(rawSubDir, subDir)
	renameAndConvert(subDir)
	#compareVolumes(subDir)
	dwiDenoise(subDir)
	#visualInspection(subDir)
	createB0(subDir)
	fixDataStrides(subDir)


runAll(subDir, rawSubDir, rawPath)