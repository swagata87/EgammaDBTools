#!/usr/bin/env python
import os
import time
import subprocess
import sys
import json
import argparse
import shutil

"""
Simple script which reads in a database file and uploads all the tags to the main db
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='makes a list of files to run over')
    parser.add_argument('dbfile')
    parser.add_argument('--prod',action='store_true',help='upload to production database')
    parser.add_argument('--txt',required=True,help="user text for upload")
    args = parser.parse_args()

    cmd = "conddb --db {filename} listTags".format(filename=args.dbfile)
    out,err = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()

    txtfile = args.dbfile.replace(".db",".txt")
    if args.dbfile==txtfile:
        print "db file {} does not end in .db".format(args.dbfile)
        sys.exit()

    tags = []
    for line in out.split("\n"):
        try:
            if line.split()[2]=="GBRForestD":
                tags.append(line.split()[0])
        except IndexError:
            pass

    upload_cmd = "uploadConditions.py"

    if args.prod:
        print "uploading to PRODUCTION"
        database = "oracle://cms_orcon_prod/CMS_CONDITIONS"
    else: 
        print "uploading to dev"
        database = "oracle://cms_orcoff_prep/CMS_CONDITIONS"
    

    for tagnr,tag in enumerate(tags):
        outfilename = "regUpload_{tagnr}_{tag}.{{suffex}}".format(tagnr=tagnr,tag=tag)
        tag_file_txt = outfilename.format(suffex='txt')
        tag_file_db = outfilename.format(suffex='db')
    
        shutil.copyfile(args.dbfile,tag_file_db)
    
        metadata = {"destinationDatabase": database,
                    "destinationTags": {tag : {}}, 
                    "inputTag": tag,
                    "since": 1, 
                    "userText": args.txt
                    }
        with open(tag_file_txt,'w') as f:
            json.dump(metadata,f)
            
        with open(tag_file_txt,'r') as f:
            print f.readlines()

        upload_cmd += " "+tag_file_db

    print upload_cmd
    import time
    print "will upload in 10s"
    time.sleep(10)
    subprocess.Popen(upload_cmd.split()).communicate()
