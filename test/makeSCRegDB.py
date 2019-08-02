#!/usr/bin/env python
import os
import time
import subprocess

era = "2018"

if era=="2017":
    dbTagSuffix="_2017UL"
    outputFile ="scReg_2017_UL_realIC"

    regres_dir = "/mercury/data1/harper/EgEnergyRegression/EgRegresTrainer/results/"
    regres_data = [
        {"filename" : "scRegUL_1050_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "pfscecal_{region}Correction_offline_v2","fileLabel" : "{region}Correction"},
        {"filename" : "scRegUL_1050_realIC_RealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "pfscecal_{region}Uncertainty_offline_v2","fileLabel" : "{region}Uncertainty"},
        ]
elif era=="2018":
    dbTagSuffix="_2018UL"
    outputFile ="scReg_2018UL"

    regres_dir = "/mercury/data1/harper/EgEnergyRegression/EgRegresTrainer/resultsSCV5/"
    regres_data = [
        {"filename" : "scReg2018UL_IdealIC_IdealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "pfscecal_{region}Correction_offline_v2","fileLabel" : "{region}Correction"},
        {"filename" : "scReg2018UL_RealIC_RealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "pfscecal_{region}Uncertainty_offline_v2","fileLabel" : "{region}Uncertainty"},
        ]
else:
    print "era {} not recognised, should be 2017 or 2018 (as a string)"


if os.path.isfile(outputFile+".db"):
    print "file ",outputFile+".db","exists, deleting in 10s"
    time.sleep(10)
    os.remove(outputFile+".db")


    
toget_str =""
for entry in regres_data:
    for region in ["EB","EE"]:
        filename = entry["filename"].format(region=region)
        dbLabel = entry["dbLabel"].format(region=region)
        fileLabel = entry["fileLabel"].format(region=region)
        cmd = "cmsRun RecoEgamma/EgammaTools/test/gbrForestDBWriter.py gbrFilename={filename} fileLabel={fileLabel} dbLabel={dbLabel} dbFilename={dbFilename} dbTag={dbTag}".format(filename=regres_dir+filename,fileLabel=fileLabel,dbLabel=dbLabel,dbTag=dbLabel+dbTagSuffix,dbFilename=outputFile)
        print cmd
        subprocess.Popen(cmd.split()).communicate()
        toget_str += """cms.PSet(record = cms.string("GBRDWrapperRcd"),
         label = cms.untracked.string("{label}"),
         tag = cms.string("{tag}")),
""".format(label=dbLabel,tag=dbLabel+dbTagSuffix)


print toget_str


