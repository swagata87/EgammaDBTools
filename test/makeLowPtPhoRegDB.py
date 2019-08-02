#!/usr/bin/env python
import os
import time
import subprocess





dbTagSuffix="_LbyL2018"
outputFile ="lbyL_2018_UL_250719"
regres_dir = "./"
regres_data = [
    {"filename" : "lowPtPho/moustache_sc/scRegUL_1050_invTar_stdVar_stdCuts_{region}_ntrees1500_results.root",  "dbLabel" : "pfscecal_{region_lower}Correction_offline_v2","fileLabel" : "{region}Correction"},
    {"filename" : "lowPtPho/moustache_sc/scRegUL_1050_invTar_stdVar_stdCuts_{region}_ntrees1500_results.root",  "dbLabel" : "pfscecal_{region_lower}Uncertainty_offline_v2","fileLabel" : "{region}Uncertainty"},
    {"filename" : "lowPtPho/refined_sc/regPhoEcal2017UL_IdealIC_IdealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root",  "dbLabel" : "photon_{region_lower}_ecalOnly_1To20_0p2To2_mean","fileLabel" : "{region}Correction"},
    {"filename" : "lowPtPho/refined_sc/regPhoEcal2017UL_IdealIC_IdealTraining_stdVar_stdCuts_{region}_ntrees1500_results.root",  "dbLabel" : "photon_{region_lower}_ecalOnly_1To20_0p0002To0p5_sigma","fileLabel" : "{region}Uncertainty"}
]
    
    
    
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
