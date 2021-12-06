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
dicomPath = "/DTI/dti/dti_102multihb/run_01/niftis/"
fieldmapPath = "/DTI/fieldmap/niftis/"

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

def getSubList(rawSubDir):
	os.chdir(rawSubDir)
	subList = []
	for dir in os.listdir():
		if dir.startswith("reh21exp1"):
			subList.append(dir)
	return subList

def copyData(subDir, rawSubDir, dicomPath, fieldmapPath):
	print("Copying raw over raw data...")
	for sub in getSubList(rawSubDir):
		dtiPath = rawSubDir + sub + dicomPath
		newDtiPath = subDir + sub + "/dti"
		dataCopied = checkIfDataCopied(newDtiPath, sub, False)
		if dataCopied is False:
			for file in os.listdir(dtiPath):
				source = dtiPath + file
				destination = newDtiPath
				print("Copying " + file + " for subject " + sub)
				shutil.copy(source, destination)
		fieldmaps = rawSubDir + sub + fieldmapPath
		newFieldmapPath = subDir + sub + "/fieldmaps"
		dataCopied = checkIfDataCopied(newFieldmapPath, sub, True)
		if dataCopied is False:
			for file in os.listdir(fieldmaps):
				source = fieldmaps+ file
				destination = newFieldmapPath
				print("Copying " + file + " for subject " + sub)
				shutil.copy(source, destination)

def checkIfDataCopied(dataPath, sub, fieldmap):
	os.chdir(dataPath)
	dirContents = os.listdir()
	if dirContents:
		print("Dti data already copied for subject: " + sub) if fieldmap is False else print("Fieldmap data already copied for subject: " + sub)
		return True
	else:
		return False


def convert(fieldmap, sub):
	if fieldmap is False:
		if os.path.isfile("already_converted.txt"):
			print("Dti files have already been combined and converted to .mif format.")
			return
		print("Converting files for subject: " + sub)
		convertToMif = f"""
			mrconvert \
			run-01.nii \
			run-01_dwi.mif \
			-fslgrad run-01.bvec run-01.bval
		"""
		proc1 = subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		subprocess.run(['touch', 'already_converted.txt'])

	else:
		if os.path.isfile("already_converted.txt"):
			print("Fmap files have already been combined and converted to .mif format.")
			return
		print("Converting files for subject: " + sub)
		convertToMif = f"""
			mrconvert \
			fieldmap.nii \
			fieldmap.mif \
			-fslgrad fieldmap.bvec fieldmap.bval
		"""
		proc2 = subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		subprocess.run(['touch', 'already_converted.txt'])

def renameAndConvert(subDir):
	print("Converting files from nii to mif format...")
	for sub in getSubList(subDir):
		# Go into dti directory for the sub and convert data to .mif
		os.chdir(subDir)
		dtiData = sub + "/dti"
		os.chdir(dtiData)
		convert(False, sub) # False indicates not fieldmap data
		os.chdir(subDir)
		fmapData = sub + "/fieldmaps"
		os.chdir(fmapData)
		convert(True, sub) # True indicates fieldmap data


def checkIfEqual(array):
	array = iter(array)
	try:
		first = next(array)
	except StopIteration:
		return True
	return all(first == x for x in array)

def compareVolumes(subDir):
	print("Checking that volume numbers are consistent across nii, bvec and bval files...")
	for sub in getSubList(subDir):
		dtiVolumes = []
		dtiSubjectDir = subDir + sub + "/dti"
		os.chdir(dtiSubjectDir)
		#	print("Comparing dti file values for subject: " + sub + "...")
		dim4 = nib.load("run-01.nii")
		dtiVolumes.append(dim4.shape[3])
		bvecCmd = "cat run-01.bvec > bvec.txt"
		proc1 = subprocess.Popen(bvecCmd, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		dtiVolumes.append(np.loadtxt('bvec.txt', dtype='str').shape[1])
		bvalCmd = "cat run-01.bval > bval.txt"
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


def checkNoiseFile(sub):
	if os.path.isfile("noise.mif"):
		print("dwi_denoise has already been run on subject: " + sub)
		return True
	else:
		return False


def dwiDenoise(subDir):
	print("Running dwi_denoise on subjects...")
	for sub in getSubList(subDir):
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
	if os.path.isfile("residual.mif"):
		print("mrcalc has already been run on subject: " + sub)
		return True
	else:
		return False

def visualInspection(subDir):
	print("Calculating residuals on subjects...")
	for sub in getSubList(subDir):
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


def combinePhaseEncoding():
	pass


#copyData(subDir, rawSubDir, dicomPath, fieldmapPath)

#renameAndConvert(subDir)

#compareVolumes(subDir)

#dwiDenoise(subDir)

#visualInspection(subDir)




