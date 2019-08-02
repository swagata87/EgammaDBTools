# EgammaDBTools

This is a set of tools useful to E/gamma for interacting with the database. In short this means uploading energy regressions to the database

## Installation 

This needs to compiled inside CMSSW. In theory it has no dependences on its exact location but it expects to be RecoEgamma/EgammaDBTools in the CMSSW src directory. Any recent CMSSW version should work although of course if there are fundamental changes in the DB format, there may be problems

```
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git cms-init
git clone git@github.com:cms-egamma/EgammaDBTools.git RecoEgamma/EgammaDBTools
scram b -j 16
```

## AlCa Terminology

It is worth reading the [AlCa tutorials](https://indico.cern.ch/event/828624/) and that remains the reference. Below is a summary relavent to e/gamma.

* **payload**: an object in the database containing conditions, eg in our case GBRForestD
* **IOV**: interval validity; a time period, usually run range, for which a payload is valid. This enables different payloads to be used for different data periods, in our case, it allows the 2017UL conditions to be used for 2017 data and 2018YL conditions to be used for 2018 data. Note, currently this is only used for data, MC is all at the same time (run number = 1). 
* **tag**: an identifier corrresponding to a payload or group of payloads with their IOVs. Not seen by CMSSW code. So if we have 2017UL, 2018UL conditions, we will have a tag <basename>_2017UL and <basename>_2018UL and include the appropriate one.  
* **label**: Allows to distingush between multiple tags all providing a payload of the same type. E/gamma's type is mostly GBRForestD so each one must be labelled apporately to identify it. The CMSSW code then knows to ask for GBRForestD with label X for regression X.  
* **global tag**: a collection of tags defining the conditions appropriate to the given workflow 

Our goal is to provide a list of conditions appropriate for the running conditions. Taking the Ultra Legacy (UL) as an example, we need to provide payloads appropriate to each year; 2016, 2017 , 2018. This means for MC we make a tag corresponding to each payload for a given year for inclusion in the MC year specific global tag, eg 106X_upgrade2018_realistic_vX, 106X_mc2017_realistic_vX. This is because MC is currently not time / run dependent. For data, using IOVs, we combine the three years into a single tag corresponding to the 3 payloads. This allows a single global tag to be used for the data. 


## Example Workflow

At this point it is assumed that you have created GBRForestD objects and have them in various root files you wish to then upload to the database. 

The steps are as follows:
1. read the GBRForests from the .root files and write it to a local database file with a given tag 
2. upload those tags in the local database file to the central database
3. if needed, combine those tags to create a single tag for data which uses run number to determine which GBRForest to read
4. queue those tags into the appropriate global tag

### conversion from root to db format

This is done by [gbrForestDBWriter.py](test/gbrForestDBWriter.py). This calls the [GBRForestDBWriter](plugins/GBRForestDBWriter.cc) plugin to do the work via cmsRun. Example command:

```
cmsRun RecoEgamma/EgammaDBTools/test/gbrForestDBWriter.py gbrFilename=input.root fileLabel=EBCorrection dbTag=electron_eb_ecalOnly_1To300_0p2To2_mean_2018ULV1 dbLabel=electron_eb_ecalOnly_1To300_0p2To2_mean dbFilename=output
```

This reads in from *input.root* a GBRForestD with name *EBCorrection* and writes it to a file *output.db* (it automatically adds .db) with label *electron_eb_ecalOnly_1To300_0p2To2_mean* and tagname *electron_eb_ecalOnly_1To300_0p2To2_mean_2018ULV1*. Note, it will append to, not overwrite the output file *output.db*.

gbrForestDBWriter.py cmdline options:
* gbrFilename : 
  * .root file with the GBRForestD object you want to upload
* fileLabel:
  *  name of the GBRForestD in the .root file
* dbLabel:
  * label for the database (note, its not clear to me that this actually gets used for anything at this stage as its reset when queuing for the global tag but fine we do it anyways)
* dbTag:
  * name of the tag for the database
* dbFilename:
  * name of the output database file. A ".db" is added to it and the file is appended not overwritten

Note to save time, several simple scripts were written to automate this for the UL production, they were
* [makeSCRegDB.py](test/makeSCRegDB.py)
* [makeEleRegDB.py](test/makeEleRegDB.py)
* [makePhoRegDB.py](test/makePhoRegDB.py)

Note as written makePhoRegDB.py appends to the file makeEleRegDB.py wrote just to keep them in the same file.  

### Uploading to the database

First, note to do this you must be a member of cms-cond-dropbox e-group. Subscript in the normal way for e-groups. 

The local .db file must now be uploaded to the database. The AlCa tool is the [ConditionUpload service](https://twiki.cern.ch/twiki/bin/view/CMS/ConditionUploader) via  the script "uploadConditions.py" which is part of the normal CMSSW release release. 

To automate this tedious procedure, we use the [egRegUpload.py](test/egRegUpload.py) script which simply uploads all the tags in a given .db file to either the prep (default) or production database. 

```
python RecoEgamma/EgammaDBTools/test/egRegUpload.py filename.db -txt "upload message"
```

or
```
python RecoEgamma/EgammaDBTools/test/egRegUpload.py filename.db --txt "uploadmessage" --prod
```
will upload all the tags in filename.db to the prep or production databases as appropriate. Use the prep as testing, do not test with prod! The prep database can be read from local/grid jobs.

Note, it is not a good idea to override existing tags and it becomes forbidden (hopefully enforced by db rules) once they are actually used in production. 

This tool is rather simple and will make many temporary files (two for each tag, a copy of the .db file and a .txt file for the meta data) called regRegUpload_{nr}_tagname, which can be safely deleted afterwards. 

It will require you to type your cern username and password halfway through the process to start the upload. 


### Combining different payloads into a single tag with IOVs

For the data we need to create a single tag with all three years (or how many are availible) with the appropriate interval of validity which can then be included in the data global tag so a single tag can be used for all three years. 

This is done via the [makeMultiEraULRegTag.py](test/makeMultiEraULRegTag.py) script which reads the specified tag from the databases, makes a new tag with the appropriate IOVs and then uploads. It is hardcoded to do the UL style regressions combinations for the three years and should be modified as appropriate. 

```
python RecoEgamma/EgammaDBTools/test/makeMultiEraULRegTag.py regCombTmp/regCombTmp --txt "upload message"
```
with the "--prod" string indicating to upload to production.  It also makes a bunch of temporary files for uploading so the first argument is the best name of that which is then added to. Note: it will delete all files starting with that pattern! It also assumes the directory exists, otherwise it will fail. 







