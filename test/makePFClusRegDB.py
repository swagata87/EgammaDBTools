#!/usr/bin/env python
import os
import time
import subprocess

def to_fileparam(param):
    if param=="mean": return "Correction"
    elif param=="sigma": return "Uncertainty"
    else: return None

def to_fileptbin(ptbin):
    if ptbin.find("Full")!=-1: 
        return ptbin.replace("bin","").lower()
    elif ptbin=="ZS": return "zs1"
    else: return None

if __name__ == "__main__":

    era = "2018"

    regions = ["EB","EE"]
    ptbins = ["Full_ptbin1","Full_ptbin2","Full_ptbin3","ZS"]
    params = ["mean","sigma"]

    if era=="2017":
        print "2017 not implimented"
    elif era=="2018":
        dbtag_version="2018ULV1"
        dblabel_version="2017V2" #hardcoded to this
        out_file ="pfClusReg_2018UL_050819"
        regres_dir = "./"
        regres_data = {"filename" : "Config_2019July26_pfcluster_{region}_{ptbin}_results.root",
             "dbLabel"  : "ecalPFClusterCor{version}_{region}_{ptbin}_{param}_25ns",
             "fileLabel" : "{region}{param}"
                       }
            
    else:
        print "era {} not recognised, should be 2017 or 2018 (as a string)"




    if os.path.isfile(out_file+".db"):
        print "file ",out_file+".db","exists, deleting in 10s"
        time.sleep(10)
        os.remove(out_file+".db")


    toget_str = ""
    labeltag_str = ""

    
    for region in regions:
        for ptbin in ptbins:
            for param in params:
                filename = regres_data["filename"].format(region=region,ptbin=to_fileptbin(ptbin))
                fileLabel = regres_data["fileLabel"].format(region=region,param=to_fileparam(param))
                dbLabel = regres_data["dbLabel"].format(version=dblabel_version,region=region,ptbin=ptbin,param=param)
                dbTag = regres_data["dbLabel"].format(version=dbtag_version,region=region,ptbin=ptbin,param=param)

                cmd = "cmsRun RecoEgamma/EgammaDBTools/test/gbrForestDBWriter.py gbrFilename={filename} fileLabel={fileLabel} dbLabel={dbLabel} dbFilename={dbFilename} dbTag={dbTag}".format(filename=regres_dir+filename,fileLabel=fileLabel,dbLabel=dbLabel,dbTag=dbTag,dbFilename=out_file)
                print cmd
                subprocess.Popen(cmd.split()).communicate()
                toget_str += """cms.PSet(record = cms.string("GBRDWrapperRcd"),
         label = cms.untracked.string("{label}"),
         tag = cms.string("{tag}")),
""".format(label=dbLabel,tag=dbTag)
                labeltag_str+="{} {}\n".format(dbTag,dbLabel)

    print toget_str
    print labeltag_str
