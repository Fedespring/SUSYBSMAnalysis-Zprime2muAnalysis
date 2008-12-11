import FWCore.ParameterSet.Config as cms

from ResolutionDataSets_cff import dataSets

def attachHistos(process, **kwargs):
    module = process.Zprime2muHistos = cms.EDAnalyzer(
        'Zprime2muHistos',
        process.Zprime2muAnalysisCommon,
        dataSets,
        dataSet = cms.string('Zp1000'),        # Which set of parameters from dataSets to use.
        leptonsFromDileptons = cms.bool(False) # Whether only to fill the lepton plots from leptons that make it into dileptons.
        )

    process.analysisHistos = cms.Path(module)

    for key, val in kwargs.items():
        setattr(module, key, val)

__all__ = ['attachHistos']