import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

# Define a process
process = cms.Process("Demo")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )
process.source = cms.Source("EmptySource",)

# Read arguments
options = VarParsing("analysis")
options.register('gbrFilename','',VarParsing.multiplicity.singleton,VarParsing.varType.string,"gbr filename")
options.register('fileLabel','',VarParsing.multiplicity.singleton,VarParsing.varType.string,"label in file")
options.register('dbLabel','',VarParsing.multiplicity.singleton,VarParsing.varType.string,"label in db")
options.register('dbFilename','',VarParsing.multiplicity.singleton,VarParsing.varType.string,"db filename")
options.register('dbTag','',VarParsing.multiplicity.singleton,VarParsing.varType.string,"db tag")


options.parseArguments()

process.gbrForestDBWriter = cms.EDAnalyzer(
    'GBRForestDBWriter',
    gbrForests = cms.VPSet(
        cms.PSet(
            filename = cms.string(options.gbrFilename),
            fileLabel = cms.string(options.fileLabel),
            dbLabel = cms.string(options.dbLabel),
            )
        )
    )


# Write output        
process.load("CondCore.CondDB.CondDB_cfi")
process.CondDB.connect = 'sqlite_file:%s.db' % options.dbFilename
process.PoolDBOutputService = cms.Service("PoolDBOutputService",
                                          process.CondDB,
                                          timetype = cms.untracked.string('runnumber'),
                                          toPut = cms.VPSet(
        cms.PSet(
            record = cms.string(options.dbLabel),
            tag    = cms.string(options.dbTag),
            ),
        )
                                          )
# Run                                    
process.p = cms.Path(process.gbrForestDBWriter)
