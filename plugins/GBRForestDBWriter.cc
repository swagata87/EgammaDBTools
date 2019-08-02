
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"


#include "CondFormats/EgammaObjects/interface/GBRForestD.h"
#include "CondFormats/DataRecord/interface/GBRWrapperRcd.h"
#include "CondCore/DBOutputService/interface/PoolDBOutputService.h"

#include "TFile.h"

#include <string>

class GBRForestDBWriter : public edm::EDAnalyzer {
public:
  struct GBRForestData {
    std::string filename;
    std::string fileLabel;
    std::string dbLabel;
    explicit GBRForestData(const edm::ParameterSet& config):
      filename(config.getParameter<std::string>("filename")),
      fileLabel(config.getParameter<std::string>("fileLabel")),
      dbLabel(config.getParameter<std::string>("dbLabel")){}
    static edm::ParameterSetDescription makePSetDescription(){
      edm::ParameterSetDescription desc;
      desc.add<std::string>("filename","");
      desc.add<std::string>("fileLabel","");
      desc.add<std::string>("dbLabel","");
      return desc;
    }
      
  };

  explicit GBRForestDBWriter(const edm::ParameterSet&);
  ~GBRForestDBWriter();
  
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  
  
private:
  virtual void beginJob() override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  virtual void endJob() override;
  
    virtual void beginRun(edm::Run const&, edm::EventSetup const&) override{}
  virtual void endRun(edm::Run const&, edm::EventSetup const&) override{}
  virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override{}
  virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override{}
  
  std::vector<GBRForestData> gbrForestData_;

};

GBRForestD* getForestFromFile(const std::string& filename,
			       const std::string& forestName)
{
  TFile* file = TFile::Open(filename.c_str(),"READ");
  std::cout <<file->Get(forestName.c_str())<<std::endl;
  GBRForestD* forest = reinterpret_cast<GBRForestD*>(file->Get(forestName.c_str()));
  if(!forest) std::cout <<"forest not found "<<forestName<<" \""<<filename<<"\""<<std::endl;
  delete file;
  return forest;
}

void writeGBRForest(cond::service::PoolDBOutputService& dbService,
		    const std::string& dbLabel,
		    const std::string& filename,
		    const std::string& fileLabel)
{
  const GBRForestD* forest = getForestFromFile(filename,fileLabel);
  dbService.writeOne(forest,dbService.beginOfTime(),dbLabel);
}


GBRForestDBWriter::GBRForestDBWriter(const edm::ParameterSet& iConfig) 
{
  const auto gbrForests = iConfig.getParameter<std::vector<edm::ParameterSet> >("gbrForests");
  for(const auto& pset : gbrForests) gbrForestData_.push_back(GBRForestData(pset));
}

GBRForestDBWriter::~GBRForestDBWriter()
{

}
		  		
void GBRForestDBWriter::beginJob()
{
  edm::Service<cond::service::PoolDBOutputService> db;
  if (db.isAvailable()) {
    for(const auto& data : gbrForestData_){
      writeGBRForest(*db,data.dbLabel,data.filename,data.fileLabel);
    }
  }
}

void GBRForestDBWriter::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    
}

void  GBRForestDBWriter::endJob() 
{

}

void GBRForestDBWriter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.addVPSet("gbrForests",GBRForestData::makePSetDescription());
  descriptions.addDefault(desc);
}

DEFINE_FWK_MODULE(GBRForestDBWriter);
