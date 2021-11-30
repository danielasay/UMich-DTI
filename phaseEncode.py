##### This script has functions that will:
# 1) untar the dicom.tgz file
# 2) run dcm2niix_dev on the dicom files
# 3) extract the phase encode direction
# 4) compare the phase encode direction from the field map and dti data for each subject
# 5) return True/False depending on if they're correctly matched, spit out csv/txt file
import sys
import pandas as pd
import numpy as np
import csv
import os
import subprocess
import json
import time

#fieldmap = True #Boolean that must be changed depending on if you are running this on fieldmap data
dtiProc = "/PROJECTS/REHARRIS/explosives/dtiProc"
subDir = "/PROJECTS/REHARRIS/explosives/raw/"
dicomPath = "/DTI/dti/dti_102multihb/run_01"
fieldmapPath = "/DTI/fieldmap"


def unpackData(dicomPath, subDir, fieldmapPath, fieldmap):
	untar(subDir, dicomPath, fieldmap, fieldmapPath, "dicom.tgz")
	dcm2Nii(subDir, dicomPath, fieldmapPath, fieldmap)

def getPhaseEncodeDirections(dicomPath, subDir, fieldmapPath, dtiProc):
	extractDirections(subDir, dicomPath, fieldmapPath, dtiProc)


def untar(subDir, dicomPath, fieldmap, fieldmapPath, tarball):
	for sub in getSubList(subDir):
		fullPath = subDir + sub + dicomPath if fieldmap is False else subDir + sub + fieldmapPath
		os.chdir(fullPath)
		if checkForDicoms(sub, fieldmap):
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

def checkForDicoms(sub, fieldmap, dicom="dicom"):
	if os.path.isdir(dicom):
		print("Unzipped dti dicoms already exist for subject: " + sub + "\nMoving to next subject.") if fieldmap is False else print("Unzipped fieldmap dicoms already exist for subject: " + sub + "\nMoving to next subject.")
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
			print("It looks like dcm2niix has already been run on dti data for subject: " + sub + "\nMoving to next subject.") if fieldmap is False else print("It looks like dcm2niix has already been run on fieldmap data for subject: " + sub + "\nMoving to next subject.")
			time.sleep(1)

def createPhaseEncodeCSV(dtiProc, subDir):
	os.chdir(dtiProc)
	if os.path.isfile("phaseEncodeDirections.csv"):
		print("Output CSV file already exists!")
		return
	else:
		print("Creating csv output file...")
		time.sleep(1)
		subprocess.run(['touch', 'phaseEncodeDirections.csv'])
		with open('phaseEncodeDirections.csv', mode='w') as csv_file:
			fieldnames = ['subject', 'dtiDirection', 'fieldmapDirection']
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
			writer.writeheader()


def addRow(dtiProc, sub, dtiEncodeDirection, fmapEncodeDirection):
	os.chdir(dtiProc)
	print("Adding subject " + sub + " to the csv file.")
	time.sleep(1)
	with open('phaseEncodeDirections.csv', mode='a+', newline = '') as csv_file:
		writer = csv.writer(csv_file)
		elements = [sub, dtiEncodeDirection, fmapEncodeDirection]
		writer.writerow(elements)

def extractDirections(subDir, dicomPath, fieldmapPath, dtiProc):
	createPhaseEncodeCSV(dtiProc, subDir)
	niftiDir = "/niftis"
	dtiJsonFile = "run-01.json"
	fmapJsonFile = "fieldmap.json"
	for sub in getSubList(subDir):
		dtiFullPath = subDir + sub + dicomPath + niftiDir
		os.chdir(dtiFullPath)
		with open(dtiJsonFile) as dtiFile:
			dtiInfo = json.load(dtiFile)
		dtiEncodeDir = dtiInfo['PhaseEncodingDirection']
		# do the same for fmap
		fmapFullPath = subDir + sub + fieldmapPath + niftiDir
		os.chdir(fmapFullPath)
		with open(fmapJsonFile) as fmapFile:
			fmapInfo = json.load(fmapFile)
		fmapEncodeDir = fmapInfo['PhaseEncodingDirection']
		addRow(dtiProc, sub, dtiEncodeDir, fmapEncodeDir)
	checkOutput(dtiProc)

def checkOutput(dtiProc):
	os.chdir(dtiProc)
	incorrectDirectionSubs = []
	df = pd.read_csv("phaseEncodeDirections.csv")
	incorrectDirectionSubs.append(np.where((df['dtiDirection'] != df['fieldmapDirection']), "All Good", df['subject']))
	usableList = incorrectDirectionSubs[0]
	badSubs = []
	for i in usableList:
		if i != "All Good":
			badSubs.append(i)
	print("These subjects did not have correct phase encoding directions: " + str(badSubs))
	print("If the list is empty, then you're good!")




# run on Dti data
unpackData(dicomPath, subDir, fieldmapPath, False)

# Run on fieldmaps
unpackData(fieldmapPath, subDir, fieldmapPath, True)

# Create csv file with phase encode output. Must run this after the unpack functions for both dti and fieldmaps!!
getPhaseEncodeDirections(dicomPath, subDir, fieldmapPath, dtiProc)




