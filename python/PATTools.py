#!/usr/bin/env python

import FWCore.ParameterSet.Config as cms

def pruneMCLeptons(process):
    process.load('SUSYBSMAnalysis.Zprime2muAnalysis.PrunedMCLeptons_cfi')
    obj = process.prunedMCLeptons
    
    for x in (process.muonMatch, process.electronMatch):
        # Switch to Use the new GEN+SIM particles created above.
        x.matched = cms.InputTag('prunedMCLeptons')
        
        # Default PAT muon/electron-MC matching requires, in addition
        # to deltaR < 0.5, the MC and reconstructed leptons to have
        # the same charge, and (reco pt - gen pt)/gen pt <
        # 0.5. Disable these two cuts.
        x.checkCharge = False
        x.maxDPtRel = 1e6

    process.patDefaultSequence = cms.Sequence(obj * process.patDefaultSequence._seq)
 
def switchHLTProcessName(process, name):
    # As the correct trigger process name is different from the
    # default "HLT" for some MC samples, this is a simple tool to
    # switch this in all places that it's needed.
    process.patTrigger.processName = name
    process.patTriggerEvent.processName = name

def addHEEPId(process):
    # Run the HEEP electron id. This must be done at PAT tuple making
    # time and cannot be done later unless some modifications are done
    # the GsfElectron/GsfElectronCore classes.
    from SHarper.HEEPAnalyzer.HEEPSelectionCuts_cfi import heepBarrelCuts, heepEndcapCuts
    from SHarper.HEEPAnalyzer.HEEPEventParameters_cfi import heepEventPara
    process.HEEPId = cms.EDProducer('HEEPIdValueMapProducer',
                                    eleLabel = cms.InputTag('gedGsfElectrons'),
                                    barrelCuts = heepBarrelCuts,
                                    endcapCuts = heepEndcapCuts,
                                    eleIsolEffectiveAreas = heepEventPara.eleIsolEffectiveAreas,
                                    applyRhoCorrToEleIsol = heepEventPara.applyRhoCorrToEleIsol,
                                    #eleRhoCorrLabel = heepEventPara.eleRhoCorrTag,#? possible options
				    	#eleRhoCorrTag = cms.InputTag("fixedGridRhoFastjetAll"),
    					#eleRhoCorr2012Tag = cms.InputTag("kt6PFJets","rho"),
				    eleRhoCorrLabel = cms.InputTag("kt6PFJetsForIsolation","rho"),
				    verticesLabel = cms.InputTag("offlinePrimaryVerticesWithBS"),
                                    writeIdAsInt = cms.bool(True),
                                    )

    # For isolation correction
    from RecoJets.JetProducers.kt4PFJets_cfi import kt4PFJets
    process.kt6PFJetsForIsolation = kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
    process.kt6PFJetsForIsolation.Rho_EtaMax = cms.double(2.5)
    
    # Embed the HEEP cut bitwords into the userData of the
    # patElectrons so we can use it to cut on at dilepton-making time
    # instead of necessarily dropping them in the selectedPatElectrons
    # or cleanPatElectrons steps.
    process.patElectrons.userData.userInts.src.append('HEEPId')
    
    process.patDefaultSequence.replace(process.patElectrons, process.kt6PFJetsForIsolation * process.HEEPId * process.patElectrons)


# Some scraps to aid in debugging that can be put in your top-level
# config (could be turned into functions a la the above):
'''
# At the end of the job, print out a table summarizing the PAT
# candidates seen/made.
process.patDefaultSequence.remove(process.selectedPatCandidateSummary)
process.selectedPatCandidateSummary.perEvent = cms.untracked.bool(True)
process.selectedPatCandidateSummary.dumpItems = cms.untracked.bool(True)
process.patDefaultSequence *= process.selectedPatCandidateSummary

# Print messages tracing through the execution of the
# analyzers/producers (e.g. beginJob/beginRun/analyze/endRun/endJob).
process.Tracer = cms.Service('Tracer')
process.SimpleMemoryCheck = cms.Service('SimpleMemoryCheck')

# To print every event the content (the branch names) of the
# edm::Event.
process.eca = cms.EDAnalyzer('EventContentAnalyzer')
process.peca = cms.Path(process.eca)

# Dump extensive L1 and HLT trigger info (objects, path results).
process.load('L1Trigger.L1ExtraFromDigis.l1extratest_cfi')
process.load('HLTrigger.HLTcore.triggerSummaryAnalyzerAOD_cfi')
#process.triggerSummaryAnalyzerAOD.inputTag = cms.InputTag('hltTriggerSummaryAOD', '', hltProcessName)
process.ptrigAnalyzer = cms.Path(process.l1extratest*process.triggerSummaryAnalyzerAOD)

# Dump the list of genParticles in a format similar to that from
# turning on PYTHIA's verbosity.
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.printTree = cms.EDAnalyzer(
    'ParticleListDrawer',
    maxEventsToPrint = cms.untracked.int32(-1),
    src = cms.InputTag('genParticles'),
    printOnlyHardInteraction = cms.untracked.bool(True),
    useMessageLogger = cms.untracked.bool(True)
    )
process.MessageLogger.categories.append('ParticleListDrawer')
process.ptree = cms.Path(process.printTree)

# Print tables of the results of module/path execution and timing info.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

# Make MessageLogger print a message every event with (run, lumi,
# event) numbers.
process.MessageLogger.cerr.FwkReport.reportEvery = 1

# Extra options for controlling how CMSSW works.
process.source.noEventSort = cms.untracked.bool(True)
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

'''
