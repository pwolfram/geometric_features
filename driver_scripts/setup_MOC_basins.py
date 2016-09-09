#!/usr/bin/env python
"""
This script creates basins for computing the meridional overturning 
circulation (MOC).  No arguments are required.  The optional --plot
flag can be used to produce plots of each MOC basin.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

defaultFileName = 'features.geojson'


subBasins = {}
subBasins['Atlantic'] = ['Atlantic', 'Mediterranean']
subBasins['IndoPacific'] = ['Pacific', 'Indian']
subBasins['Pacific'] = ['Pacific']
subBasins['Indian'] = ['Indian']

MOCMaskFileNames = {}
MOCMaskFileNames['Atlantic'] = 'ocean/region/MOC_mask_30S/region.geojson'
MOCMaskFileNames['IndoPacific'] = 'ocean/region/MOC_mask_30S/region.geojson'
MOCMaskFileNames['Pacific'] = 'ocean/region/MOC_mask_6S/region.geojson'
MOCMaskFileNames['Indian'] = 'ocean/region/MOC_mask_6S/region.geojson'


for basinName in subBasins:

    if os.path.exists(defaultFileName):
        os.remove(defaultFileName)

    print " * merging features to make %s Basin"%basinName
    MOCName =  '%s_MOC.geojson'%basinName
    imageName =  '%s_MOC.png'%basinName
    basinFileName =  '%s_Basin.geojson'%basinName
    for oceanName in subBasins[basinName]:
        tag = '%s_Basin'%oceanName
    
        args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
        subprocess.check_call(args, env=os.environ.copy())
    
    shutil.move(defaultFileName,basinFileName)
    
    #merge the the features into a single file
    print " * combining features into single feature named %s_MOC"%basinName
    args = ['./combine_features.py', '-f', basinFileName, '-n', '%s_MOC'%basinName]
    #print ' '.join(args)
    subprocess.check_call(args, env=os.environ.copy())
    
    shutil.move(defaultFileName,basinFileName)
    
    print " * masking out features south of MOC region"
    args = ['./difference_features.py', '-f', basinFileName, '-m', MOCMaskFileNames[basinName]]
    subprocess.check_call(args, env=os.environ.copy())
    
    shutil.move(defaultFileName,MOCName)
    
    if options.plot:
        args = ['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl']
        subprocess.check_call(args, env=os.environ.copy())
    
    
if os.path.exists(defaultFileName):
    os.remove(defaultFileName)