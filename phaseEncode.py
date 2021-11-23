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

def getPhaseEncodeDirections(dicomPath, subDir):
#	for sub in getSubList(subDir):
#		fullPath = subDir + sub + dicomPath
#		os.chdir(fullPath)
#		if checkForDicoms(sub):
#			os.chdir(subDir)
#			continue
#		print("Unzipping dicoms for subject: " + sub)
#		untar("dicom.tgz")
#		os.chdir(subDir)
	dcm2Nii(subDir, dicomPath)


def untar(tarball):
	try:
		untar = subprocess.run(['tar', '-xzf', tarball], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		untar.check_returncode()
	except subprocess.CalledProcessError:
		print("Looks like your tarball didn't untar!\nMake sure you're in the correct directory.")
		print("This is the current working directory:" + os.getcwd())
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



def dcm2Nii(subDir, dicomPath):
	niftiDir = "niftis"
	run = "run-01"
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath
		os.chdir(fullPath)
		rawDicoms = fullPath + "/dicom"
		if not os.path.isdir("niftis"):
			os.makedirs("niftis")
		if os.path.getsize("niftis") == 0:
			print("Running dcm2niix on subject: " + sub)
			try:
				dcm = subprocess.run(['dcm2niix_dev', '-o', niftiDir, rawDicoms], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				dcm.check_returncode()
			except subprocess.CalledProcessError:
				print("Dcm2niix failed to run.\nDouble check that you're in the correct directory.")
				print("This is the current working directory:" + os.getcwd())
				print("Killing script...")
				time.sleep(1)
				sys.exit()
			os.chdir(niftiDir)
			for file in os.listdir():
				fileName, fileExt = os.path.splitext(file)
				fileName = run
				newName = f'{fileName}{fileExt}'
				os.rename(file, newName)
		else:
			print("It looks like dcm2niix has already been run for " + sub + "\nMoving to next subject.")




getPhaseEncodeDirections(dicomPath, subDir)




#subprocess.run(['dcm2niix_dev', '-o', niftiDir, rawDicoms], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# ^ this seems to work