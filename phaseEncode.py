##### This script has functions that will:
# 1) untar the dicom.tgz file
# 2) run dcm2niix_dev on the dicom files
# 3) extract the phase encode direction
# 4) compare the phase encode direction from the field map and dti data for each subject
# 5) return True/False depending on if they're correctly matched, spit out csv/txt file
import sys
import csv
import os
import subprocess
import json
import time

fieldmap = True #Boolean that must be changed depending on if you are running this on fieldmap data
dtiProc = "/PROJECTS/REHARRIS/explosives/dtiProc"
subDir = "/PROJECTS/REHARRIS/explosives/raw/"
dicomPath = "/DTI/dti/dti_102multihb/run_01"
fieldmapPath = "/DTI/fieldmap"

def getPhaseEncodeDirections(dicomPath, subDir, fieldmapPath, fieldmap):
	untar(subDir, dicomPath, fieldmapPath, "dicom.tgz")
	dcm2Nii(subDir, dicomPath, fieldmapPath, fieldmap)


def untar(subDir, dicomPath, fieldmapPath, tarball):
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath if fieldmap is False else subDir + sub + fieldmapPath
		os.chdir(fullPath)
		if checkForDicoms(sub):
			os.chdir(subDir)
			continue
		print("Unzipping dicoms for subject: " + sub)
		try:
			untar = subprocess.run(['tar', '-xzf', tarball], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			untar.check_returncode()
		except subprocess.CalledProcessError:
			print("Looks like your tarball didn't untar!\nMake sure you're in the correct directory.")
			print("This is the current working directory:" + os.getcwd())
			print("Killing script...")
			time.sleep(1)
			sys.exit()
		os.chdir(subDir)


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
		time.sleep(1)
		return True
	else:
		return False


def dcm2Nii(subDir, dicomPath, fieldmapPath, fieldmap):
	niftiDir = "niftis"
	run = "run-01" if fieldmap is False else "fieldmap"
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath if fieldmap is False else subDir + sub + fieldmapPath
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
			print("Done! Moving to next subject...")

			
		else:
			print("It looks like dcm2niix has already been run for subject: " + sub + "\nMoving to next subject.")
			time.sleep(1)

def createPhaseEncodeCSV(dtiProc):
	os.chdir(dtiProc)
	subprocess.run(['touch', 'phaseEncodeDirections.csv'])
	with open('phaseEncodeDirections.csv', mode='w') as csv_file:
		fieldnames = ['subject', 'dtiDirection', 'fieldmapDirection']
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()


def addRow(dtiProc, sub, dtiEncodeDir, fieldmapEncodeDir):
	os.chdir(dtiProc)
	with open('phaseEncodeDirections.csv', mode='w') as csv_file:
		fieldnames = ['subject', 'dtiDirection', 'fieldmapDirection']
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writerow({'subject': sub, 'dtiDirection': dtiEncodeDir, 'fieldmapDirection' : fieldmapEncodeDir})


def extractDirection(subDir, dicomPath):
	niftiDir = "niftis"
	jsonFile = "run-01.json"
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath + niftiDir
		os.chdir(fullPath)
		with open(jsonFile) as file:
			info = json.load(file)
		dtiEncodeDir = info['PhaseEncodingDirection']
		


#	writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
#    writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})


# run on Dti data
#getPhaseEncodeDirections(dicomPath, subDir, fieldmapPath, fieldmap)

# Run on fieldmaps
getPhaseEncodeDirections(fieldmapPath, subDir, fieldmapPath, fieldmap)


















