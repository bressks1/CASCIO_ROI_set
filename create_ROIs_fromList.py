### This script creates a series of spherical ROIs
### and adds them together by region category
## Inputs: list of MNI coordinate for ROI, corresponding region label
### Alisa Zoltowski
### Created 01-14-22

# import what is needed for the operating system
import os
# import csv to read in ROI file
import csv
# import glob to grab files
import glob

# set up base directory and base subject directory
baseDir = "/Volumes/PSR/Cascio_Lab/Zoltowski/MRI_Analyses/AutismRestingState/WinderRRBs"
roiDir = baseDir + "/IndividualBodyParts"

## SETTINGS-edit if desired; kernel size, template file name
kernel_size = '4'
template_file = baseDir + '/rspm_template_gray_xnat.nii'

# read in region of interest coordinate list
roi_file_location = baseDir + "/somatomotor_ROIs.csv"
ROI_CoordList = {}  # create dictionary of region with coordinates
ROI_Categories = [] # create list of region categories, for aggregate ROI
with open(roi_file_location, 'rU') as subject_run_file:
    roi_data = csv.reader(subject_run_file, delimiter=',')
    next(roi_data, None)  # Skip header
    for row in roi_data:
        label = row[0] + '_' + row[1]
        ROI_Categories.append(row[0])
        ROI_CoordList[label] = {}
        ROI_CoordList[label]['X'] = row[2]
        ROI_CoordList[label]['Y'] = row[3]
        ROI_CoordList[label]['Z'] = row[4]

## get distinct categories
ROI_UniqueCategories = list(set(ROI_Categories))

## loop through regions, creating spherical mask at each coordinate
regionList = list(ROI_CoordList)
for region in regionList:
    # run fsl maths functions, define terms to use
    create_ROI = template_file + " -mul 0 -add 1 -roi "
    ROI_coordinates = ROI_CoordList[region]['X'] + " 1 " + ROI_CoordList[region]['Y'] + " 1 " + ROI_CoordList[region]['Z'] + " 1 0 1"
    ROI_sphere = roiDir + "/" + region + "_sphere.nii.gz"

    # first command- point ROI
    os.system("fslmaths " + create_ROI + ROI_coordinates + " tmp")
    # second command- sphere ROI
    os.system("fslmaths tmp -kernel sphere " + kernel_size + " -fmean " + ROI_sphere + " -odt float")
    print("Completed ROI for region: " + region)

## then- loop through region categories and add together
for category in ROI_UniqueCategories:
    # grab relevant files
    relevant_rois = glob.glob(roiDir + "/" + category + "*")

    # start with first roi to add, define what output file will be called
    add_roi_command = relevant_rois[0]
    output_combined = baseDir + "/" + category + "_ALL.nii.gz"

    # then- loop through to add each one
    for roiFile in relevant_rois[1:]:
        add_roi_command = add_roi_command + " -add " + roiFile

    # finally- run output
    os.system("fslmaths " + add_roi_command + " " + output_combined)
    print("Completed addition for area: " + category)
