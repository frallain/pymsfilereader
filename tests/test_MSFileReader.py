#!/bin/env python2.7
# encoding: utf-8
import ctypes
import os
import re
import sys
import time

IS_32_BITS_PYTHON = ctypes.sizeof(ctypes.c_voidp)==4
# 4 for 32 bit or 8 for 64 bit. 

from fixtures import *


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


def test_Version(rawfile):
    assert re.match(r"\d+\.\d+\.\d+\.\d+", rawfile.Version())

def test_GetFileName(rawfile, rawfilename):
    assert rawfile.GetFileName() == os.path.abspath(rawfilename)

def test_GetCreatorID(rawfile):
    assert rawfile.GetCreatorID() == 'Administrator'

def test_GetVersionNumber(rawfile):
    assert rawfile.GetVersionNumber() == 50

def test_GetCreationDate(rawfile):
    creation_date_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', rawfile.GetCreationDate())
    assert creation_date_iso == '1970-01-01T10:37:55Z'

def test_IsError(rawfile):
    assert rawfile.IsError() == False

def test_IsNewFile(rawfile):
    assert rawfile.IsNewFile() == False

def test_IsThereMSData(rawfile):
    assert rawfile.IsThereMSData() == True

def test_HasExpMethod(rawfile):
    assert rawfile.HasExpMethod() == True

def test_InAcquisition(rawfile):
    assert rawfile.InAcquisition() == False

def test_GetErrorCode(rawfile):
    assert rawfile.GetErrorCode() == False

def test_GetErrorMessage(rawfile):
    assert rawfile.GetErrorMessage() == ''

def test_GetWarningMessage(rawfile):
    assert rawfile.GetWarningMessage() == ''

def test_RefreshViewOfFile(rawfile):
    assert rawfile.RefreshViewOfFile() == None

def test_GetNumberOfControllers(rawfile):
    assert rawfile.GetNumberOfControllers() == 1

def test_GetNumberOfControllersOfType_minus1(rawfile):
    assert rawfile.GetNumberOfControllersOfType(-1) == 0

def test_GetNumberOfControllersOfType_zero(rawfile):
    assert rawfile.GetNumberOfControllersOfType(0) == 1

def test_GetNumberOfControllersOfType_plus1(rawfile):
    assert rawfile.GetNumberOfControllersOfType(1) == 0

def test_GetNumberOfControllersOfType_plus2(rawfile):
    assert rawfile.GetNumberOfControllersOfType(2) == 0

def test_GetNumberOfControllersOfType_plus3(rawfile):
    assert rawfile.GetNumberOfControllersOfType(3) == 0

def test_GetNumberOfControllersOfType_plus4(rawfile):
    assert rawfile.GetNumberOfControllersOfType(4) == 0

def test_GetControllerType_zero(rawfile):
    assert rawfile.GetControllerType(0) == 'MS'

# def test_GetControllerType_one(rawfile):
#     assert rawfile.GetControllerType(1) == 1

def test_GetCurrentController(rawfile):
    assert rawfile.GetCurrentController() == (0, 1)


    # print( 'GetCurrentController()',  rawfile.GetCurrentController() )
    # # print( 'SetCurrentController(4,1)',  rawfile.SetCurrentController(4,1) )

    # print( 'GetCurrentController()',  rawfile.GetCurrentController() )
    # # print( 'SetCurrentController(0,1)',  rawfile.SetCurrentController(0,1) )

    # print( 'GetCurrentController()',  rawfile.GetCurrentController() )

def test_GetExpectedRunTime(rawfile):
    assert rawfile.GetExpectedRunTime() == 100.0

def test_GetMaxIntegratedIntensity(rawfile):
    assert rawfile.GetMaxIntegratedIntensity() == 1120672896.0

def test_GetMaxIntensity(rawfile):
    assert rawfile.GetMaxIntensity() == 0

def test_GetInletID(rawfile):
    assert rawfile.GetInletID() == 0

def test_GetErrorFlag(rawfile):
    assert rawfile.GetErrorFlag() == 0

def test_GetFlags(rawfile):
    assert rawfile.GetFlags() == ''

def test_GetAcquisitionFileName(rawfile):
    assert rawfile.GetAcquisitionFileName() == ''

def test_GetOperator(rawfile):
    assert rawfile.GetOperator() == ''

def test_GetComment1(rawfile):
    assert rawfile.GetComment1() == ''

def test_GetComment2(rawfile):
    assert rawfile.GetComment2() == ''

def test_GetFilters(rawfile, filters_3_0, filters_3_1):
    DLL_VERSION = rawfile.VersionAsATuple()
    if DLL_VERSION.major<=3  and DLL_VERSION.minor<1:
        # GetFilters results for 3.0-
        assert rawfile.GetFilters() == filters_3_0
        assert len(rawfile.GetFilters()) == 1724
    else:
        # GetFilters results for 3.1+
        assert rawfile.GetFilters() == filters_3_1
        assert len(rawfile.GetFilters()) == 1690

def test_GetMassTolerance(rawfile):
    assert rawfile.GetMassTolerance() == (False, 500.0, 0)

def test_SetMassTolerance(rawfile):
    rawfile.SetMassTolerance(userDefined=True, massTolerance=555.0, units=2)
    assert rawfile.GetMassTolerance() == (True, 555.0, 2)

def test_GetMassResolution(rawfile):
    assert rawfile.GetMassResolution() == 0.5

def test_GetNumTrailerExtra(rawfile):
    assert rawfile.GetNumTrailerExtra() == 3316

def test_GetLowMass(rawfile):
    assert rawfile.GetLowMass() == 100.0

def test_GetHighMass(rawfile):
    assert rawfile.GetHighMass() == 2000.0

def test_GetStartTime(rawfile):
    assert rawfile.GetStartTime() == 0.005666666666666667

def test_GetEndTime(rawfile):
    assert rawfile.GetEndTime() == 99.97766666666666

def test_GetNumSpectra(rawfile):
    assert rawfile.GetNumSpectra() == 3316

def test_GetFirstSpectrumNumber(rawfile):
    assert rawfile.GetFirstSpectrumNumber() == 1

def test_GetLastSpectrumNumber(rawfile):
    assert rawfile.GetLastSpectrumNumber() == 3316

def test_GetAcquisitionDate(rawfile):
    assert rawfile.GetAcquisitionDate() == ''

def test_GetUniqueCompoundNames(rawfile):
    assert rawfile.GetUniqueCompoundNames() == ('',)


    # print( '############################################## INSTRUMENT BEGIN')

def test_GetInstrumentDescription(rawfile):
    assert rawfile.GetInstrumentDescription() == ''

def test_GetInstrumentID(rawfile):
    assert rawfile.GetInstrumentID() == 0

def test_GetInstSerialNumber(rawfile):
    assert rawfile.GetInstSerialNumber() == 'LC000718'

def test_GetInstName(rawfile):
    assert rawfile.GetInstName() == 'LCQ'

def test_GetInstModel(rawfile):
    assert rawfile.GetInstModel() == 'LCQ'

def test_GetInstSoftwareVersion(rawfile):
    assert rawfile.GetInstSoftwareVersion() == '1.3'

def test_GetInstHardwareVersion(rawfile):
    assert rawfile.GetInstHardwareVersion() == ''

def test_GetInstFlags(rawfile):
    assert rawfile.GetInstFlags() == ''

def test_GetInstNumChannelLabels(rawfile):
    assert rawfile.GetInstNumChannelLabels() == 0

# def test_GetInstChannelLabel(rawfile):
#     assert rawfile.GetInstChannelLabel(0) == 0

def test_IsQExactive(rawfile):
    assert rawfile.IsQExactive() == False

    # scanNumber = 1
# print( '############################################## XCALIBUR INTERFACE BEGIN')

def test_GetScanHeaderInfoForScanNum(rawfile):
    scanheader = rawfile.GetScanHeaderInfoForScanNum(scanNumber=1)

    assert scanheader['numPackets'] == 0
    assert scanheader['StartTime'] == 0.005666666666666667
    assert scanheader['LowMass'] == 300.0
    assert scanheader['HighMass'] == 2000.0
    assert scanheader['TIC'] == 0.0
    assert scanheader['BasePeakMass'] == 0.0
    assert scanheader['BasePeakIntensity'] == 0.0
    assert scanheader['numChannels'] == 0
    assert scanheader['uniformTime'] == 0
    assert scanheader['Frequency'] == 0.0

def test_GetTrailerExtraForScanNum(rawfile):
    scantrailer = rawfile.GetTrailerExtraForScanNum(scanNumber=1)
    assert scantrailer['Wideband Activation'] == 'Off'
    assert scantrailer['Micro Scan Count'] == 3.0
    assert scantrailer['Ion Injection Time (ms)'] == 49.98
    assert scantrailer['Scan Segment'] == 1.0
    assert scantrailer['Scan Event'] == 1.0
    assert scantrailer['Elapsed Scan Time (sec)'] == 1.38
    assert scantrailer['API Source CID Energy'] == 0.0
    assert scantrailer['Resolution'] == 'Low'
    assert scantrailer['Average Scan by Inst'] == 'No'
    assert scantrailer['BackGd Subtracted by Inst'] == 'No'
    assert scantrailer['Charge State'] == 0.0

def test_GetNumTuneData(rawfile):
    assert rawfile.GetNumTuneData() == 2

def test_GetTuneData(rawfile):
    assert rawfile.GetTuneData(0) == 'Capillary Temp (C):200.00\nAPCI Vaporizer Temp (C):450.00\nAGC:On\nAGC Off Ion Time (ms):5.00\nSheath Gas Flow ():0.00\nAux Gas Flow ():0.00\nSource Type:ESI\nInjection Waveforms:Off\n\nPOSITIVE POLARITY\nSource Voltage (kV):0.00\nSource Current (uA):80.00\nCapillary Voltage (V):25.00\nTube Lens Offset (V):10.00\nMultipole RF Amplifier (Vp-p):400.00\nMultipole 1 Offset (V):-7.00\nMultipole 2 Offset (V):-28.50\nInterMultipole Lens Voltage (V):-16.00\nTrap DC Offset Voltage (V):-10.00\nZoom Micro Scans:5\nZoom AGC Target:20000000.00\nZoom Max Ion Time (ms):50.00\nFull Micro Scans:3\nFull AGC Target:50000000.00\nFull Max Ion Time (ms):50.00\nSIM Micro Scans:5\nSIM AGC Target:40000000.00\nSIM Max Ion Time (ms):200.00\nMSn Micro Scans:3\nMSn AGC Target:40000000.00\nMSn Max Ion Time (ms):200.00\n\nNEGATIVE POLARITY\nSource Voltage (kV):4.00\nSource Current (uA):100.00\nCapillary Voltage (V):10.00\nTube Lens Offset (V):-50.00\nMultipole RF Amplifier (Vp-p):400.00\nMultipole 1 Offset (V):3.00\nMultipole 2 Offset (V):7.00\nInterMultipole Lens Voltage (V):16.00\nTrap DC Offset Voltage (V):10.00\nZoom Micro Scans:5\nZoom AGC Target:10000000.00\nZoom Max Ion Time (ms):50.00\nFull Micro Scans:3\nFull AGC Target:10000000.00\nFull Max Ion Time (ms):50.00\nSIM Micro Scans:5\nSIM AGC Target:20000000.00\nSIM Max Ion Time (ms):200.00\nMSn Micro Scans:3\nMSn AGC Target:20000000.00\nMSn Max Ion Time (ms):200.00\n'

def test_GetNumInstMethods(rawfile):
    assert rawfile.GetNumInstMethods() == 1

def test_GetInstMethodNames(rawfile):
    assert rawfile.GetInstMethodNames() == ('LCQ',)

def test_GetInstMethod(rawfile, instmethod):
    assert rawfile.GetInstMethod(0) == instmethod

def test_ExtractInstMethodFromRaw(rawfile):
    method_filename = rawfile.filename + '.meth'
    try:
        os.remove(method_filename)
    except FileNotFoundError:
        pass
    rawfile.ExtractInstMethodFromRaw(method_filename)
    assert os.path.exists(method_filename)

# # # # # # # "View/Report/Sample Information" BEGIN

def test_GetVialNumber(rawfile):
    assert rawfile.GetVialNumber() == 0

def test_GetInjectionVolume(rawfile):
    assert rawfile.GetInjectionVolume() == 0

def test_GetInjectionAmountUnits(rawfile):
    assert rawfile.GetInjectionAmountUnits() == ''

def test_GetSampleVolume(rawfile):
    assert rawfile.GetSampleVolume() == 0.0

def test_GetSampleVolumeUnits(rawfile):
    assert rawfile.GetSampleVolumeUnits() == ''

def test_GetSampleWeight(rawfile):
    assert rawfile.GetSampleWeight() == 0.0

def test_GetSampleAmountUnits(rawfile):
    assert rawfile.GetSampleAmountUnits() == ''

def test_GetSeqRowNumber(rawfile):
    assert rawfile.GetSeqRowNumber() == 1

def test_GetSeqRowSampleType(rawfile):
    assert rawfile.GetSeqRowSampleType() == 'Unknown'

def test_GetSeqRowDataPath(rawfile):
    assert rawfile.GetSeqRowDataPath() == ''

def test_GetSeqRowRawFileName(rawfile):
    assert rawfile.GetSeqRowRawFileName() == 'Shew_246a_LCQa_15Oct04_Andro_0904-2_4-20.RAW'

def test_GetSeqRowSampleName(rawfile):
    assert rawfile.GetSeqRowSampleName() == ''

def test_GetSeqRowSampleID(rawfile):
    assert rawfile.GetSeqRowSampleID() == ''

def test_GetSeqRowComment(rawfile):
    assert rawfile.GetSeqRowComment() == ''

def test_GetSeqRowLevelName(rawfile):
    assert rawfile.GetSeqRowLevelName() == ''

def test_GetSeqRowUserText(rawfile):
    assert rawfile.GetSeqRowUserText(index=0) == ''

def test_GetSeqRowInstrumentMethod(rawfile):
    assert rawfile.GetSeqRowInstrumentMethod() == r'C:\xcalibur\methods\Std 100 min\4-20ddTop3_100min.meth'

def test_GetSeqRowProcessingMethod(rawfile):
    assert rawfile.GetSeqRowProcessingMethod() == ''

def test_GetSeqRowCalibrationFile(rawfile):
    assert rawfile.GetSeqRowCalibrationFile() == ''

def test_GetSeqRowVial(rawfile):
    assert rawfile.GetSeqRowVial() == ''

def test_GetSeqRowInjectionVolume(rawfile):
    assert rawfile.GetSeqRowInjectionVolume() == 0.0

def test_GetSeqRowSampleWeight(rawfile):
    assert rawfile.GetSeqRowSampleWeight() == 0.0

def test_GetSeqRowSampleVolume(rawfile):
    assert rawfile.GetSeqRowSampleVolume() == 0.0

def test_GetSeqRowISTDAmount(rawfile):
    assert rawfile.GetSeqRowISTDAmount() == 0.0

def test_GetSeqRowDilutionFactor(rawfile):
    assert rawfile.GetSeqRowDilutionFactor() == 1.0

def test_GetSeqRowUserLabel0(rawfile):
    assert rawfile.GetSeqRowUserLabel(index=0) == 'Study'

def test_GetSeqRowUserLabel1(rawfile):
    assert rawfile.GetSeqRowUserLabel(index=1) == 'Client'

def test_GetSeqRowUserLabel2(rawfile):
    assert rawfile.GetSeqRowUserLabel(index=2) == 'Laboratory'

def test_GetSeqRowUserLabel3(rawfile):
    assert rawfile.GetSeqRowUserLabel(index=3) == 'Company'

def test_GetSeqRowUserLabel4(rawfile):
    assert rawfile.GetSeqRowUserLabel(index=4) == 'Phone'

def test_GetSeqRowUserTextEx0(rawfile):
    assert rawfile.GetSeqRowUserTextEx(index=0) == ''

def test_GetSeqRowUserTextEx1(rawfile):
    assert rawfile.GetSeqRowUserTextEx(index=1) == ''

def test_GetSeqRowUserTextEx2(rawfile):
    assert rawfile.GetSeqRowUserTextEx(index=2) == ''

def test_GetSeqRowUserTextEx3(rawfile):
    assert rawfile.GetSeqRowUserTextEx(index=3) == ''

def test_GetSeqRowUserTextEx4(rawfile):
    assert rawfile.GetSeqRowUserTextEx(index=4) == ''

def test_GetSeqRowBarcode(rawfile):
    assert rawfile.GetSeqRowBarcode() == ''

def test_GetSeqRowBarcodeStatus(rawfile):
    assert rawfile.GetSeqRowBarcodeStatus() == 0


def test_GetNumStatusLog(rawfile):
    assert rawfile.GetNumStatusLog() == 2767

def test_GetStatusLogForScanNum(rawfile):
    assert rawfile.GetStatusLogForScanNum(scanNumber=1) == (0.052666667848825455, [('API SOURCE', ''), ('Source Voltage (kV)', '0.03'), ('Source Current (uA)', '0.10'), ('Vaporizer Thermocouple OK', 'No'), ('Vaporizer Temp (C)', '-0.00'), ('Sheath Gas Flow Rate ()', '-0.20'), ('Aux Gas Flow Rate()', '-0.27'), ('Capillary RTD OK', 'Yes'), ('Capillary Voltage (V)', '25.39'), ('Capillary Temp (C)', '199.50'), ('Tube Lens Voltage (V, set point)', '10.00'), ('8 kV supply at limit', 'No'), ('', ''), ('VACUUM', ''), ('Vacuum OK', 'Yes'), ('Ion Gauge Pressure OK', 'Yes'), ('Ion Gauge Status', 'On'), ('Ion Gauge (x10e-5 Torr)', '1.64'), ('Convectron Pressure OK', 'Yes'), ('Convectron Gauge (Torr)', '0.94'), ('', ''), ('TURBO PUMP', ''), ('Status', 'Running'), ('Life (hours)', '54878'), ('Speed (rpm)', '60000'), ('Power (Watts)', '73'), ('Temperature (C)', '40.00'), ('', ''), ('ION OPTICS', ''), ('Multipole Frequency On', 'Yes'), ('Multipole 1 Offset (V)', '-6.74'), ('Lens Voltage (V)', '-15.15'), ('Multipole 2 Offset (V)', '-28.11'), ('Multipole RF Amplitude (Vp-p, set point)', '400.00'), ('Coarse Trap DC Offset (V)', '-9.88'), ('', ''), ('MAIN RF', ''), ('Reference Sine Wave OK', 'Yes'), ('Standing Wave Ratio OK', 'Yes'), ('Main RF DAC (steps)', '-33.00'), ('Main RF Detected (V)', '-0.00'), ('RF Detector Temp (C)', '37.45'), ('Main RF Modulation (V)', '0.04'), ('Main RF Amplifier (Vp-p)', '8.74'), ('RF Generator Temp (C)', '27.73'), ('', ''), ('ION DETECTION SYSTEM', ''), ('Multiplier Actual (V)', '-1182.88'), ('', ''), ('POWER SUPPLIES', ''), ('+5V Supply Voltage (V)', '5.14'), ('-15V Supply Voltage (V)', '-14.97'), ('+15V Supply Voltage (V)', '14.94'), ('+24V Supply Voltage (V)', '24.13'), ('-28V Supply Voltage (V)', '-28.09'), ('+28V Supply Voltage (V)', '28.29'), ('+28V Supply Current (Amps)', '0.80'), ('+35V Supply Voltage (V)', '35.55'), ('+36V Supply Voltage (V)', '36.22'), ('-150V Supply Voltage (V)', '-148.98'), ('+150V Supply Voltage (V)', '150.86'), ('-205V Supply Voltage (V)', '-203.87'), ('+205V Supply Voltage (V)', '205.34'), ('Ambient Temp (C)', '27.68'), ('', ''), ('INSTRUMENT STATUS', ''), ('Instrument', 'On'), ('Analysis', 'Acquiring'), ('', ''), ('SYRINGE PUMP', ''), ('Status', 'Ready'), ('Flow Rate (uL/min)', '3.00'), ('Infused Volume (uL)', '0.00'), ('Syringe Diameter (mm)', '2.30'), ('', ''), ('DIGITAL INPUTS', ''), ('READY IN is active', 'No'), ('START IN is active', 'No'), ('Divert/Inject valve', 'Load')])

def test_GetStatusLogForPos(rawfile, statuslogforpos0):
    assert rawfile.GetStatusLogForPos(position=0) == statuslogforpos0

def test_GetStatusLogPlottableIndex(rawfile):
    assert rawfile.GetStatusLogPlottableIndex() == (('Source Voltage (kV):', 'Source Current (uA):', 'Vaporizer Temp (C):', 'Sheath Gas Flow Rate ():', 'Aux Gas Flow Rate():', 'Capillary Voltage (V):', 'Capillary Temp (C):', 'Tube Lens Voltage (V, set point):', 'Ion Gauge (x10e-5 Torr):', 'Convectron Gauge (Torr):', 'Life (hours):', 'Speed (rpm):', 'Power (Watts):', 'Temperature (C):', 'Multipole 1 Offset (V):', 'Lens Voltage (V):', 'Multipole 2 Offset (V):', 'Multipole RF Amplitude (Vp-p, set point):', 'Coarse Trap DC Offset (V):', 'Main RF DAC (steps):', 'Main RF Detected (V):', 'RF Detector Temp (C):', 'Main RF Modulation (V):', 'Main RF Amplifier (Vp-p):', 'RF Generator Temp (C):', 'Multiplier Actual (V):', '+5V Supply Voltage (V):', '-15V Supply Voltage (V):', '+15V Supply Voltage (V):', '+24V Supply Voltage (V):', '-28V Supply Voltage (V):', '+28V Supply Voltage (V):', '+28V Supply Current (Amps):', '+35V Supply Voltage (V):', '+36V Supply Voltage (V):', '-150V Supply Voltage (V):', '+150V Supply Voltage (V):', '-205V Supply Voltage (V):', '+205V Supply Voltage (V):', 'Ambient Temp (C):', 'Flow Rate (uL/min):', 'Infused Volume (uL):', 'Syringe Diameter (mm):'), (1, 2, 4, 5, 6, 8, 9, 10, 17, 19, 23, 24, 25, 26, 30, 31, 32, 33, 34, 39, 40, 41, 42, 43, 44, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 71, 72, 73))

def test_GetNumErrorLog(rawfile):
    assert rawfile.GetNumErrorLog() == 1289

def test_GetErrorLogItem(rawfile):
    assert rawfile.GetErrorLogItem(0) == ('Dynamic exclusion list is full. Mass 1026.89 has been dropped.', 15.657333374023438)

def test_GetMassListFromScanNum(rawfile):
    assert rawfile.GetMassListFromScanNum(scanNumber=1) == (((), ()), None)

def test_GetMassListRangeFromScanNum(rawfile):
    assert rawfile.GetMassListRangeFromScanNum(scanNumber=1) == (((), ()), None)

def test_GetSegmentedMassListFromScanNum(rawfile):
    assert rawfile.GetSegmentedMassListFromScanNum(scanNumber=1) == (((), ()), None, (0,), 1)

def test_GetAverageMassList(rawfile):
    assert rawfile.GetAverageMassList(firstAvgScanNumber=1, lastAvgScanNumber=11) == (((), ()), None)

def test_GetAveragedMassSpectrum(rawfile):
    assert rawfile.GetAveragedMassSpectrum(listOfScanNumbers=[1,2,3]) == (((), ()), None)

def test_GetSummedMassSpectrum(rawfile):
    assert rawfile.GetSummedMassSpectrum(listOfScanNumbers=[1,2,3]) == (((), ()), None)

def test_GetLabelData(rawfile):
    labels, flags = rawfile.GetLabelData(scanNumber=1)
    assert labels.mass == ()
    assert labels.intensity == ()
    assert labels.resolution == ()
    assert labels.baseline == ()
    assert labels.noise == ()
    assert labels.charge == ()
    assert flags.saturated == ()
    assert flags.fragmented == ()
    assert flags.merged == ()
    assert flags.exception == ()
    assert flags.reference == ()
    assert flags.modified == ()

def test_GetAveragedLabelData(rawfile):
    values, flags = rawfile.GetAveragedLabelData(listOfScanNumbers=[1,2,3])
    assert values == (((), (), (), (), (), ()))
    assert flags.saturated == ()
    assert flags.fragmented == ()
    assert flags.merged == ()
    assert flags.exception == ()
    assert flags.reference == ()
    assert flags.modified == ()


def test_GetAllMSOrderData(rawfile):
    labels, flags, numberOfMSOrders = rawfile.GetAllMSOrderData(scanNumber=1)
    assert labels.mass == ()
    assert labels.intensity == ()
    assert labels.resolution == ()
    assert labels.baseline == ()
    assert labels.noise == ()
    assert labels.charge == ()
    assert flags.activation_type == ()
    assert flags.is_precursor_range_valid == ()
    assert numberOfMSOrders == 0

def test_GetChroData(rawfile, chrodata):
    chroData, peakFlags = rawfile.GetChroData(startTime=rawfile.StartTime,
                                                 endTime=rawfile.EndTime,
                                                 massRange1="{}-{}".format(rawfile.LowMass, rawfile.HighMass),
                                                 scanFilter="Full ms ")
    assert chroData == chrodata
    assert peakFlags == None

# def test_GetChroByCompoundName(rawfile):
#     assert rawfile.GetChroByCompoundName(["methyltestosterone"]) == ''

# def test_GetMassPrecisionEstimate(rawfile):
#     assert rawfile.GetMassPrecisionEstimate(scanNumber=1) == ''

def test_GetFullMSOrderPrecursorDataFromScanNum(rawfile):
    precursorData = rawfile.GetFullMSOrderPrecursorDataFromScanNum(scanNumber=1, MSOrder=0)
    assert precursorData.precursorMass == 50.0
    assert precursorData.isolationWidth == 1.0
    assert precursorData.collisionEnergy == 25.0

    if (sys.version_info.major, sys.version_info.minor) == (2, 7) and IS_32_BITS_PYTHON:
        assert precursorData.collisionEnergyValid >= 1e+100
    else:
        assert precursorData.collisionEnergyValid <= 1e-200

    assert precursorData.rangeIsValid == 0.0
    assert precursorData.firstPrecursorMass == 0.0
    assert precursorData.lastPrecursorMass == 0.0

def test_GetPrecursorInfoFromScanNum(rawfile):
    assert rawfile.GetPrecursorInfoFromScanNum(scanNumber=1) == None
