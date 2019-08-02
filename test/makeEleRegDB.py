#!/usr/bin/env python
import os
import time
import subprocess


era = "2018"

if era=="2017":
    dbTagSuffix="_2017ULV2"
    outputFile ="elePhoReg_2017_UL_030619"
    regres_dir = "/mercury/data1/harper/EgEnergyRegression/EgRegresTrainer/resultsEleV5/"
    regres_data = [
        {"filename" : "regEle2017UL_IdealIC_IdealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalOnly_1To300_0p2To2_mean","fileLabel" : "{region}Correction"},
        {"filename" : "regEleEcal2017UL_RealIC_RealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalOnly_1To300_0p0002To0p5_sigma","fileLabel" : "{region}Uncertainty"},
        {"filename" : "regEleEcalTrk2017UL_RealIC_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalTrk_1To300_0p2To2_mean","fileLabel" : "{region}Correction"},
        {"filename" : "regEleEcalTrk2017UL_RealIC_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalTrk_1To300_0p0002To0p5_sigma","fileLabel" : "{region}Uncertainty"}
        ]

elif era=="2018":
    dbTagSuffix="_2018ULV1"
    outputFile ="elePhoReg_2018_UL_120719"
    regres_dir = "/mercury/data1/harper/EgEnergyRegression/EgRegresTrainer/resultsEleV5/"
    regres_data = [
        {"filename" : "regEleEcal2018UL_IdealIC_IdealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalOnly_1To300_0p2To2_mean","fileLabel" : "{region}Correction"},
        {"filename" : "regEleEcal2018UL_RealIC_RealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalOnly_1To300_0p0002To0p5_sigma","fileLabel" : "{region}Uncertainty"},
        {"filename" : "regEleEcalTrk2018UL_RealIC_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalTrk_1To300_0p2To2_mean","fileLabel" : "{region}Correction"},
        {"filename" : "regEleEcalTrk2018UL_RealIC_stdVar_stdCuts_{region}_ntrees1500_results.root", "dbLabel" : "electron_{region_lower}_ecalTrk_1To300_0p0002To0p5_sigma","fileLabel" : "{region}Uncertainty"}
        ]
else:
    print "era {} not recognised, should be 2017 or 2018 (as a string)"




if os.path.isfile(outputFile+".db"):
    print "file ",outputFile+".db","exists, deleting in 10s"
    time.sleep(10)
    os.remove(outputFile+".db")


toget_str = ""
labeltag_str = ""

for entry in regres_data:
    for region in ["EB","EE"]:
        filename = entry["filename"].format(region=region)
        dbLabel = entry["dbLabel"].format(region_lower=region.lower())
        fileLabel = entry["fileLabel"].format(region=region)
        cmd = "cmsRun RecoEgamma/EgammaTools/test/gbrForestDBWriter.py gbrFilename={filename} fileLabel={fileLabel} dbLabel={dbLabel} dbFilename={dbFilename} dbTag={dbTag}".format(filename=regres_dir+filename,fileLabel=fileLabel,dbLabel=dbLabel,dbTag=dbLabel+dbTagSuffix,dbFilename=outputFile)
        print cmd
        subprocess.Popen(cmd.split()).communicate()
        toget_str += """cms.PSet(record = cms.string("GBRDWrapperRcd"),
         label = cms.untracked.string("{label}"),
         tag = cms.string("{tag}")),
""".format(label=dbLabel,tag=dbLabel+dbTagSuffix)
        labeltag_str+="{} {}\n".format(dbLabel+dbTagSuffix,dbLabel)

print toget_str
print labeltag_str
