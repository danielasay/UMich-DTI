# ********* This script is to be run AFTER running the preproc02.py script **************
# ********* It will create tissue boundaries on the available DTI and anatomical data. **************

#### This script has functions that will:
## 1) Segment the anatomical image into 5 tissue types
## 2) extract b0 image averages
## 3) run fsl flirt
## 4) create wm-gm boundaries

import os
import subprocess
import sys


procDir = "/scratch/seharte_root/seharte99/shared_data/expl/dtiProc"


def verifyModules():
	print("Modules loaded:")
	os.system("module list")
	while True:
			loaded = input("\nFor this script, you need the mrtrix module loaded.\nIs it listed above? If so, type yes and hit enter. \nIf not, please type no and hit enter.\n")
			if loaded == "yes" or loaded == "y" or loaded == "Yes" or loaded == "YES":
				print("great! running script...")
				break
			elif loaded == "no" or loaded == "n" or loaded == "No" or loaded == "NO":
				print("\nplease load mrtrix using the following command:\n")
				print("module load mrtrix\n")
				print("after loading the module, relaunch the script")
				sys.exit()


def checkIfCompleted(procDir):
	os.chdir(procDir)
	noRunSubList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("gmwmSeed_coreg.mif"):
			print("all steps have already been run on subject " + sub)
			noRunSubList.append(sub)
			os.chdir(procDir)
		os.chdir(procDir)
	return noRunSubList


def segmentAnat(prodDir, noRunList):
	for sub in getSubListSegmentAnat(procDir, noRunList):
		os.chdir(sub)
		print("running mrconvert on subject " + sub + "...")
		mrconvert = "mrconvert t1spgr_208sl.nii T1.mif"
		proc1 = subprocess.Popen(mrconvert, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("T1.mif"):
			print("mrconvert ran successfully for subject " + sub)
		else:
			print("mrconvert did NOT run successfully for subject " + sub + ". please check")
		print("running 5ttgen on subject " + sub + "...")
		segment = "5ttgen fsl T1.mif 5tt_nocoreg.mif"
		proc2 = subprocess.Popen(segment, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		if os.path.isfile("5tt_nocoreg.mif"):
			print("5ttgen ran successfully for subject " + sub)
		else:
			print("5ttgen did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListSegmentAnat(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile("5tt_nocoreg.mif"):
			print("tissue segmentation has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def dwiExtract(procDir, noRunList):
	for sub in getSubListDwiExtract(procDir, noRunList):
		os.chdir(sub)
		print("running dwiextract on subject " + sub + "...")
		dwiextract = "dwiextract run-01_den_preproc_unbiased.mif - -bzero | mrmath - mean mean_b0.mif -axis 3"
		proc1 = subprocess.Popen(dwiextract, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("mean_b0.mif"):
			print("dwiextract ran successfully for subject " + sub)
		else:
			print("dwiextract did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListDwiExtract(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile("mean_b0.mif"):
			print("dwiextract has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def fslFlirt(procDir, noRunList):
	for sub in getSubListFslFlirt(procDir, noRunList):
		os.chdir(sub)

		# run 2 mrconvert commands for work in fsl
		print("running mrconvert steps on subject " + sub + "...")
		convertB0ToNii = "mrconvert mean_b0.mif mean_b0.nii.gz"
		proc1 = subprocess.Popen(convertB0ToNii, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		convertNocoregToNii = "mrconvert 5tt_nocoreg.mif 5tt_nocoreg.nii.gz"
		proc2 = subprocess.Popen(convertNocoregToNii, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		if os.path.isfile("mean_b0.nii.gz") and os.path.isfile("5tt_nocoreg.nii.gz"):
			print("mrconvert ran successfully for subject " + sub)
		else:
			print("mrconvert did NOT run successfully for subject " + sub + ". please check")

		# run fslroi to make a 3D rather than 4D dataset
		print("running fslroi on subject " + sub + "...")
		fslroi = "fslroi 5tt_nocoreg.nii.gz 5tt_vol0.nii.gz 0 1"
		proc3 = subprocess.Popen(fslroi, shell=True, stdout=subprocess.PIPE)
		proc3.wait()
		if os.path.isfile("5tt_vol0.nii.gz"):
			print("fslroi ran successfully for subject " + sub)
		else:
			print("fslroi did NOT run successfully for subject " + sub + ". please check")

		# run flirt on subject
		print("running fsl flirt on subject " + sub + "...")
		flirt = "flirt -in mean_b0.nii.gz -ref 5tt_vol0.nii.gz -interp nearestneighbour -dof 6 -omat diff2struct_fsl.mat"
		proc4 = subprocess.Popen(fslroi, shell=True, stdout=subprocess.PIPE)
		proc4.wait()
		if os.path.isfile("diff2struct_fsl.mat"):
			print("flirt ran successfully for subject " + sub)
		else:
			print("flirt did NOT run successfully for subject " + sub + ". please check")

		# run 2 transformation commands
		print("running transformation commands on subject " + sub + "...")
		transformconvert = "transformconvert diff2struct_fsl.mat mean_b0.nii.gz 5tt_nocoreg.nii.gz flirt_import diff2struct_mrtrix.txt"
		proc5 = subprocess.Popen(transformconvert, shell=True, stdout=subprocess.PIPE)
		proc5.wait()
		mrtransform = "mrtransform 5tt_nocoreg.mif -linear diff2struct_mrtrix.txt -inverse 5tt_nocoreg.mif"
		proc6 = subprocess.Popen(mrtransform, shell=True, stdout=subprocess.PIPE)
		proc6.wait()
		if os.path.isfile("5tt_coreg.mif"):
			print("transformations ran successfully for subject " + sub)
		else:
			print("transformations did NOT run successfully for subject " + sub + ". please check")

		os.chdir(procDir)

def gtSubListFslFlirt(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile("5tt_coreg.mif"):
			print("dwiextract has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def createBoundary(procDir, noRunList):
	for sub in getSubListCreateBoundary(procDir, noRunList):
		os.chdir(sub)
		print("running 5tt2gmwmi on subject " + sub + "...")
		boundary = "5tt2gmwmi 5tt_coreg.mif gmwmSeed_coreg.mif"
		proc1 = subprocess.Popen(boundary, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("gmwmSeed_coreg.mif"):
			print("dwiextract ran successfully for subject " + sub)
		else:
			print("dwiextract did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListCreateBoundary(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile("gmwmSeed_coreg.mif"):
			print("5tt2gmwmi has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList



checkIfCompleted(procDir)
verifyModules()
noRunList = checkIfCompleted(procDir)
convertAnat(procDir, noRunList)
dwiExtract(procDir, noRunList)
fslFlirt(procDir, noRunList)
createBoundary(procDir, noRunList)

