##### This script has functions that will:
# 1) untar the dicom.tgz file
# 2) run dcm2niix_dev on the dicom files
# 3) extract the phase encode direction
# 4) compare the phase encode direction from the field map and dti data for each subject
# 5) return True/False depending on if they're correctly matched, spit out csv/txt file
import sys
import os
import subprocess
import time

subDir = "/PROJECTS/REHARRIS/explosives/raw/"
dicomPath = "/DTI/dti/dti_102multihb/run_01"

def getPhaseEncodeDirections(dicomPath, subDir, niftiDir=None):
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath
		os.chdir(fullPath)
		if checkForDicoms(sub):
			os.chdir(subDir)
			continue
		print("Unzipping dicoms for subject: " + sub)
		untar("dicom.tgz")
		os.chdir(subDir)


def untar(tarball):
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath
		os.chdir(fullPath)
		try:
			untar = subprocess.run(['tar', '-xzf', tarball], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			untar.check_returncode()
		except subprocess.CalledProcessError:
			print("Looks like your tarball didn't untar!\nMake sure you're in the correct directory.")
			print("This is the current working directory: " + os.getcwd())
			print("Killing script...")
			time.sleep(1)
			sys.exit()


def getSubList(subDir):
	os.chdir(subDir)
	subList = []
	for dir in os.listdir():
		if dir.startswith("reh21exp1"):
			subList.append(dir)
	return subList

def checkForDicoms(sub, dicom="dicom"):
	if os.path.isdir(dicom):
		print("Unzipped dicoms already exist for subject: " + sub + "\nMoving to next subject.")
		time.sleep(3)
		return True
	else:
		return False



def dcm2Nii(subDir):
	os.chdir()

getPhaseEncodeDirections(dicomPath, subDir)

