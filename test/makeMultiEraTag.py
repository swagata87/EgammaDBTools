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


def copy_tags_locally(tags,eras,prefix):
    for tag in tags:
        for era in eras:
            fulltag = tag.format(era['suffix'])
            cmd = "conddb copy {fulltag} -d {filename}".format(fulltag=fulltag,filename="{}{}.db".format(prefix,fulltag))
            subprocess.Popen(cmd.split(),stdin=subprocess.PIPE).communicate(input='y')
    
def combine_tags(tags,eras,file_prefix,tag_suffix,database,uploadtxt):
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
    args = parser.parse_args()

    elepho_eras = [{"suffix" : "_2017ULV2", "run" : 1 },
                   {"suffix" : "_2018ULV1", "run" : 314472}]
    
    sc_eras = [{"suffix" : "", "run" : 1 },
               {"suffix" : "_2017UL", "run" : 288377},
               {"suffix" : "_2018UL", "run" : 314472}]
    
    combined_tag_suffix = "_UL2017To2018V1"

    sc_tags = get_sc_tagnames()
    elepho_tags = get_elepho_tagnames()
    
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

    
    copy_tags_locally(tags=sc_tags,eras=sc_eras,prefix=args.dbfilebase)
    copy_tags_locally(tags=elepho_tags,eras=elepho_eras,prefix=args.dbfilebase) 
    
    tag_files_sc = combine_tags(tags=sc_tags,eras=sc_eras,file_prefix=args.dbfilebase,tag_suffix=combined_tag_suffix,database=database,uploadtxt=args.txt)
    tag_files_elepho = combine_tags(tags=elepho_tags,eras=elepho_eras,file_prefix=args.dbfilebase,tag_suffix=combined_tag_suffix,database=database,uploadtxt=args.txt)
    
    upload_cmd = "uploadConditions.py {} {}".format(" ".join(tag_files_sc)," ".join(tag_files_elepho))

    print upload_cmd
    import time
    print "will upload in 10s"
    time.sleep(10)
    subprocess.Popen(upload_cmd.split()).communicate()
