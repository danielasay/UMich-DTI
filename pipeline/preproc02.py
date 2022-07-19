# ********* This script is to be run AFTER running dwifslpreproc on Armis
# ********* It will perform Constrained Spherical Deconvolution on the available DTI data.

#### This script has functions that will:
## 1) Run dwibiascorrect on the data to remove inhomogeneities in the data for better mask estimation
## 2) Create a brain mask
## 3) create a basis function using dwi2response
## 4) calculate fiber orientation densitites for each subject with dwi2fod
## 5) normalize data for later group level analyses with mtnormalise

import os
import subprocess
import sys


procDir = "/scratch/seharte_root/seharte99/shared_data/expl/dtiProc"


def checkIfCompleted(procDir):
	os.chdir(procDir)
	noRunSubList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("wmfod_norm.mif"):
			print("all steps have already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			noRunSubList.append(sub)
		os.chdir(procDir)
	return noRunSubList


def verifyModules():
	print("Modules loaded:")
	os.system("module list")
	while True:
			loaded = input("\nFor this script, you need the mrtrix and ANTs modules loaded.\nAre they listed above? If so, type yes and hit enter. \nIf not, please type no and hit enter.\n")
			if loaded == "yes" or loaded == "y" or loaded == "Yes" or loaded == "YES":
				print("great! running script...")
				break
			elif loaded == "no" or loaded == "n" or loaded == "No" or loaded == "NO":
				print("\nplease load mrtrix and ANTs using the following command:\n")
				print("module load mrtrix ANTs\n")
				print("after loading the modules, relaunch the script")
				sys.exit()


def dwibiascorrect(procDir, noRunList):
	for sub in getSubListBiasCorrect(procDir, noRunList):
		os.chdir(sub)
		print("running dwibiascorrect on subject " + sub + "...")
		dwibiascorrect = "dwibiascorrect ants run-01_den_preproc.mif run-01_den_preproc_unbiased.mif -bias bias.mif"
		proc1 = subprocess.Popen(dwibiascorrect, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("run-01_den_preproc_unbiased.mif"):
			print("dwibiascorrect ran successfully for subject " + sub)
		else:
			print("dwibiascorrect did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)



def getSubListBiasCorrect(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("run-01_den_preproc_unbiased.mif"):
			print("dwibiascorrect has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList


def dwi2mask(procDir, noRunList):
	for sub in getSubListDwiMask(procDir, noRunList):
		os.chdir(sub)
		print("running dwi2mask on subject " + sub + "...")
		dwi2mask = "dwi2mask run-01_den_preproc_unbiased.mif mask.mif"
		proc1 = subprocess.Popen(dwi2mask, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("mask.mif"):
			print("dwi2mask ran successfully for subject " + sub)
		else:
			print("dwi2mask did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)


def getSubListDwiMask(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("mask.mif"):
			print("dwi2mask has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def dwi2Response(procDir, noRunList):
	for sub in getSubListDwiResponse(procDir, noRunList):
		os.chdir(sub)
		print("running dwi2response on subject " + sub + "...")
		dwi2response = "dwi2response dhollander run-01_den_preproc_unbiased.mif wm.txt gm.txt csf.txt -voxels voxels.mif"
		proc1 = subprocess.Popen(dwi2response, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("wm.txt"):
			print("dwi2response ran successfully for subject " + sub)
		else:
			print("dwi2response did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListDwiResponse(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("wm.txt"):
			print("dwi2response has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def dwi2Fod(procDir, noRunList):
	for sub in getSubListDwiFod(procDir, noRunList):
		os.chdir(sub)
		print("running dwi2fod on subject " + sub + "...")
		dwi2Fod = "dwi2fod msmt_csd run-01_den_preproc_unbiased.mif -mask mask.mif wm.txt wmfod.mif gm.txt gmfod.mif csf.txt csffod.mif"
		proc1 = subprocess.Popen(dwi2Fod, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("wmfod.mif"):
			print("dwi2Fod ran successfully for subject " + sub)
		else:
			print("dwi2Fod did NOT run successfully for subject " + sub + ". please check")
		print("combining fod data...")
		combineFod = "mrconvert -coord 3 0 wmfod.mif - | mrcat csffod.mif gmfod.mif - vf.mif"
		proc2 = subprocess.Popen(combineFod, shell=True, stdout=subprocess.PIPE)
		proc2.wait()
		if os.path.isfile("vf.mif"):
			print("sucessfully combined data.")
		else:
			print("data did not successfully combine for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListDwiFod(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		os.chdir(sub)
		if os.path.isfile("vf.mif"):
			print("dwi2Fod has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList

def normalizeData(procDir, noRunList):
	for sub in getSubListNormalize(procDir, noRunList):
		os.chdir(sub)
		print("running normalization on subject " + sub + "...")
		normalize = "mtnormalise wmfod.mif wmfod_norm.mif gmfod.mif gmfod_norm.mif csffod.mif csffod_norm.mif -mask mask.mif"
		proc1 = subprocess.Popen(normalize, shell=True, stdout=subprocess.PIPE)
		proc1.wait()
		if os.path.isfile("wmfod_norm.mif"):
			print("normalization ran successfully for subject " + sub)
		else:
			print("normalization did NOT run successfully for subject " + sub + ". please check")
		os.chdir(procDir)

def getSubListNormalize(procDir, noRunList):
	os.chdir(procDir)
	subList = []
	for sub in os.listdir(os.getcwd()):
		if sub in noRunList:
			continue
		os.chdir(sub)
		if os.path.isfile("wmfod_norm.mif"):
			print("normalization has already been run on subject " + sub + ". Moving to next subject...")
			os.chdir(procDir)
			continue
		else:
			subList.append(sub)
		os.chdir(procDir)
	return subList


noRunList = checkIfCompleted(procDir)
verifyModules()
dwibiascorrect(procDir, noRunList)
dwi2mask(procDir, noRunList)
dwi2Response(procDir, noRunList)
dwi2Fod(procDir, noRunList)
normalizeData(procDir, noRunList)