##### This script has functions that will:
# 1) generate a list of all the subjects that have been processed on new scanner software
# 2) copy over abcd bvec and bval files 
# 3) create fieldmaps using external fsl script
# 4) verify that the fieldmaps have been successfully created

import sys
import os
import shutil
import time


dtiProc = "/PROJECTS/REHARRIS/explosives/dtiProc"
subDir = "/PROJECTS/REHARRIS/explosives/raw/"
dicomPath = "/DTI"


# get a list of all the subjects that have been processed with the new software

def getSubList(subDir):
	os.chdir(subDir)
	subList = []
	for sub in os.listdir():
		os.chdir(sub)
		if os.path.isdir("DTI"):
			os.chdir("DTI")
			if os.path.isfile("dti.nii"):
				subList.append(sub)
		os.chdir(subDir)
	return subList


## copies the abcd bvec and bval files

def changeBVFiles(subDir, subList):
	os.chdir(subDir)
	for sub in subList:
		os.chdir(sub + "/DTI")
		if os.path.isfile("abcd_edit.bval") and os.path.isfile("abcd_edit.bvec"):
			print("abcd bval and bvec files have already been copied over for subject " + sub)
			time.sleep(.1)
			os.chdir(subDir)
			continue
		else:
			print("copying abcd bval and bvec files for subject " + sub)
			shutil.copy("/home/dasay/diffusion/abcd_edit.bval", os.getcwd())
			shutil.copy("/home/dasay/diffusion/abcd_edit.bvec", os.getcwd())
		os.chdir(subDir)

# creates fieldmaps for each subject


def createFieldmaps(subDir, subList):
	os.chdir(subDir)
	for sub in subList:
		os.chdir(sub + "/DTI")
		if os.path.isfile("final_fieldmap.nii.gz"):
			print("fieldmap already exists for subject " + sub + "\nmoving to next subject...")
			time.sleep(.1)
			os.chdir(subDir)
		else:
			print("creating fieldmap for subject " + sub + " ...")
			shutil.copy("/PROJECTS/REHARRIS/explosives/dtiProc/scripts/fslFMAP.sh", os.getcwd())
			os.system("bash fslFMAP.sh")
			os.chdir(subDir)



def checkOutput(subDir, subList):
	os.chdir(subDir)
	badSubs = []
	for sub in subList:
		os.chdir(sub + "/DTI")
		if os.path.isfile("final_fieldmap.nii.gz"):
			print("Fieldmap successfully created for subject " + sub)
			time.sleep(.1)
			os.chdir(subDir)
		else:
			badSubs.append(sub)
			os.chdir(subDir)
	print("No fieldmaps were created for the following subjects:\n" + str(badSubs) + "\nIf there are no subjects listed, then you're good!")


subjects = getSubList(subDir)

changeBVFiles(subDir, subjects)

createFieldmaps(subDir, subjects)

checkOutput(subDir, subjects)
