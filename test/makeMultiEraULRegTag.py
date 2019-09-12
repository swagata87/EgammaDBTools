#!/usr/bin/env python
import os
import time
import subprocess
import sys
import json
import argparse
import shutil
import glob
"""
Combines tags in the database into a single tag with multiple IOVs for data
"""

def get_sc_tagnames():
    return ["pfscecal_EBCorrection_offline_v2{}",
            "pfscecal_EBUncertainty_offline_v2{}",
            "pfscecal_EECorrection_offline_v2{}",
            "pfscecal_EEUncertainty_offline_v2{}"]

def get_elepho_tagnames():
    return ["electron_eb_ecalOnly_1To300_0p2To2_mean{}",
            "electron_ee_ecalOnly_1To300_0p2To2_mean{}",
            "electron_eb_ecalOnly_1To300_0p0002To0p5_sigma{}",
            "electron_ee_ecalOnly_1To300_0p0002To0p5_sigma{}",
            "electron_eb_ecalTrk_1To300_0p2To2_mean{}",
            "electron_ee_ecalTrk_1To300_0p2To2_mean{}",
            "electron_eb_ecalTrk_1To300_0p0002To0p5_sigma{}",
            "electron_ee_ecalTrk_1To300_0p0002To0p5_sigma{}",
            "photon_eb_ecalOnly_5To300_0p2To2_mean{}",
            "photon_ee_ecalOnly_5To300_0p2To2_mean{}",
            "photon_eb_ecalOnly_5To300_0p0002To0p5_sigma{}",
            "photon_ee_ecalOnly_5To300_0p0002To0p5_sigma{}"
            ]

def get_pfcluseb_tagnames():
    return ["ecalPFClusterCor{}_EB_Full_ptbin1_mean_25ns",
            "ecalPFClusterCor{}_EB_Full_ptbin1_sigma_25ns",
            "ecalPFClusterCor{}_EB_Full_ptbin2_mean_25ns",
            "ecalPFClusterCor{}_EB_Full_ptbin2_sigma_25ns",
            "ecalPFClusterCor{}_EB_Full_ptbin3_mean_25ns",
            "ecalPFClusterCor{}_EB_Full_ptbin3_sigma_25ns",
            "ecalPFClusterCor{}_EB_ZS_mean_25ns",
            "ecalPFClusterCor{}_EB_ZS_sigma_25ns",
            ]

def get_pfclusee_tagnames():
    return ["ecalPFClusterCor{}_EE_Full_ptbin1_mean_25ns",
            "ecalPFClusterCor{}_EE_Full_ptbin1_sigma_25ns",
            "ecalPFClusterCor{}_EE_Full_ptbin2_mean_25ns",
            "ecalPFClusterCor{}_EE_Full_ptbin2_sigma_25ns",
            "ecalPFClusterCor{}_EE_Full_ptbin3_mean_25ns",
            "ecalPFClusterCor{}_EE_Full_ptbin3_sigma_25ns",
            "ecalPFClusterCor{}_EE_ZS_mean_25ns",
            "ecalPFClusterCor{}_EE_ZS_sigma_25ns",
            ]


def copy_tags_locally(tags,eras,prefix):
    for tag in tags:
        for era in eras:
            fulltag = tag.format(era['suffix'])
            cmd = "conddb copy {fulltag} -d {filename}".format(fulltag=fulltag,filename="{}{}.db".format(prefix,fulltag))
            subprocess.Popen(cmd.split(),stdin=subprocess.PIPE).communicate(input='y')
    
def combine_tags(tags,eras,file_prefix,tag_suffix,database,uploadtxt):
    copy_tags_locally(tags=tags,eras=eras,prefix=file_prefix)
    tag_files = []
    for tag in tags:
        combinedtag = tag.format(tag_suffix)
        
        for era in eras:
            fulltag = tag.format(era['suffix'])
            tag_file_db = "{}{}.db".format(file_prefix,fulltag)
            tag_file_txt = "{}{}.txt".format(file_prefix,fulltag)
            metadata = {"destinationDatabase": database,
                        "destinationTags": {combinedtag : {}}, 
                        "inputTag": fulltag,
                        "since": era["run"], 
                        "userText": uploadtxt
                        }
            with open(tag_file_txt,'w') as f:
                json.dump(metadata,f)
                
            tag_files.append(tag_file_db)
    return tag_files

        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='makes a list of files to run over')
    parser.add_argument('dbfilebase')
    parser.add_argument('--prod',action='store_true',help='upload to production database')
    parser.add_argument('--txt',required=True,help="user text for upload")
    parser.add_argument('--sc',action='store_true',help='do supercluster regressions')
    parser.add_argument('--elepho',action='store_true',help='do ele/pho regressions')
    parser.add_argument('--pfclus',action='store_true',help='do pfclus regressions')
    args = parser.parse_args()

    elepho_eras = [{"suffix" : "_2017ULV2", "run" : 1 },
                   {"suffix" : "_2018ULV1", "run" : 314472}]
    
    sc_eras = [{"suffix" : "", "run" : 1 },
               {"suffix" : "_2017UL", "run" : 288377},
               {"suffix" : "_2018UL", "run" : 314472}]
    
    pfcluseb_eras = [{"suffix" : "2017ULV1", "run" : 1 },
                     {"suffix" : "2018ULV1", "run" : 314472}]
    #we use 2018V1 for 2017UL endcap
    pfclusee_eras = [{"suffix" : "2018V1", "run" : 1 },
                     {"suffix" : "2018ULV1", "run" : 314472}]
    

    combined_tag_suffix = "_UL2017To2018V1"
    combined_pfclus_tag_suffix = "UL2017To2018V1"

    sc_tags = get_sc_tagnames()
    elepho_tags = get_elepho_tagnames()
    pfcluseb_tags = get_pfcluseb_tagnames()
    pfclusee_tags = get_pfclusee_tagnames()
    
    matched_files = glob.glob("{}*".format(args.dbfilebase))
    if matched_files:
        print "files\n {}\n exists, deleting in 10s".format(" ".join(matched_files))
        time.sleep(10)
        for f in matched_files:
            os.remove(f)


    if args.prod:
        print "uploading to PRODUCTION"
        database = "oracle://cms_orcon_prod/CMS_CONDITIONS"
    else: 
        print "uploading to dev"
        database = "oracle://cms_orcoff_prep/CMS_CONDITIONS"

        
    tag_files = []
    if args.sc:
        tag_files_sc = combine_tags(tags=sc_tags,eras=sc_eras,file_prefix=args.dbfilebase,
                                    tag_suffix=combined_tag_suffix,database=database,uploadtxt=args.txt)
        tag_files.extend(tag_files_sc)
        
    if args.elepho:
        tag_files_elepho = combine_tags(tags=elepho_tags,eras=elepho_eras,file_prefix=args.dbfilebase,
                                        tag_suffix=combined_tag_suffix,database=database,uploadtxt=args.txt)
        tag_files.extend(tag_files_elepho)
    
    if args.pfclus:
        tag_files_pfclus = combine_tags(tags=pfcluseb_tags,eras=pfcluseb_eras,file_prefix=args.dbfilebase,
                                        tag_suffix=combined_pfclus_tag_suffix,database=database,uploadtxt=args.txt)
        tag_files.extend(tag_files_pfclus)
        tag_files_pfclus = combine_tags(tags=pfclusee_tags,eras=pfclusee_eras,file_prefix=args.dbfilebase,
                                        tag_suffix=combined_pfclus_tag_suffix,database=database,uploadtxt=args.txt)
        tag_files.extend(tag_files_pfclus)

    if tag_files == []:
        print "no objects selected for upload, need to specify at least one of --sc , --phoele, --pfclus"
    else:
        upload_cmd = "uploadConditions.py {}".format(" ".join(tag_files))
        print ""
        print upload_cmd
        print "will upload in 10s"
        time.sleep(10)
        subprocess.Popen(upload_cmd.split()).communicate()
