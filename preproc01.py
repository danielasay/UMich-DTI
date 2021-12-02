### This scripts has functions that will: 
# 1) copy nifti data from raw dir to dtiProc, both fieldmaps and dti
# 2) label dti and fieldmap data as PA and AP, respectively
# 3) convert the data from nii to mif format and combine with its bvec and bval files
# 4) compare the number of volumes in mif file and bvec/bval files, all 3 should be equal
# 5) run dwi_denoise and calculate residual
# 6) optionally run a visual inspection on residuals
# 7) extract and combine reverse and primary phase encoding directions - primary == PA, reverse == AP
import shutil
import os
import subprocess

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
		subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
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
		subprocess.Popen(convertToMif, shell=True, stdout=subprocess.PIPE)
		subprocess.run(['touch', 'already_converted.txt'])

def renameAndConvert(subDir):
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

def compareVolumes():
	


def dwiDenoise():
	pass


def visualInspection():
	pass


def combinePhaseEncoding():
	pass


#copyData(subDir, rawSubDir, dicomPath, fieldmapPath)

#renameAndConvert(subDir)




