#!/bin/env python2.7
# encoding: utf-8
from __future__ import print_function

import sys
import os
import subprocess
import re
import decimal
import tempfile
import logging
log = logging.getLogger(os.path.basename(__file__))
from pprint import pprint
from ctypes import *
import array
import traceback
import copy
__version__ = "MSFileReader 3.0 SP2 (3.0.29.0), Revision A, July 2014"
# XRawfile2(_x64).dll 3.0.29.0
# fregistry(_x64).dll 3.0.0.0
# Fileio(_x64).dll 3.0.0.0
# cf. https://thermo.flexnetoperations.com/control/thmo/login?username=frallain@gmail.com&password=B8g-72&action=authenticate&nextURL=index -> Utility Software

try :
    import comtypes
    from comtypes.client import GetModule, CreateObject
except (ImportError,NameError) as e:
    sys.exit('Please install comtypes >= 0.6.2 : http://pypi.python.org/pypi/comtypes/') 
    
try:
    from comtypes.gen import MSFileReaderLib
except ImportError:
    XRawfile2_dll_loaded = False
    XRawfile2_dll_path = []
    XRawfile2_dll_path.append( os.path.dirname(os.path.abspath(__file__) ) + os.sep + 'XRawfile2_x64.dll' )    # 64bits msFileReader aside raw.py
    XRawfile2_dll_path.append( u'C:\\Program Files\\Thermo\\MSFileReader\\XRawfile2_x64.dll' )    # 64bits msFileReader with 64bits system 
    XRawfile2_dll_path.append( os.path.dirname(os.path.abspath(__file__) ) + os.sep + 'XRawfile2.dll' )    # 32bits msFileReader aside raw.py
    XRawfile2_dll_path.append( u'C:\\Program Files (x86)\\Thermo\\MSFileReader\\XRawfile2.dll' )  # 32bits msFileReader with 64bits system 
    XRawfile2_dll_path.append( u'C:\\Program Files\\Thermo\\MSFileReader\\XRawfile2.dll' )        # 32bits msFileReader with 32bits system
    XRawfile2_dll_path_0 = copy.deepcopy(XRawfile2_dll_path)
    while not XRawfile2_dll_loaded:
        try :
            # TODO ? version with XRawfile2.dll integrated = no need to install MSFileReader, dll not registered to the COM server
            # problem : IXRawfile4 not found
            #  -> http://osdir.com/ml/python.comtypes.user/2008-07/msg00045.html messages 42-46 talk about it
            XRawfile2_dll_filename = XRawfile2_dll_path.pop(0)
            log.debug("Trying comtypes.client.GetModule " + XRawfile2_dll_filename + " ...")
            GetModule(XRawfile2_dll_filename) # -> generation
        except IndexError:
            msg = '1) The msFileReader DLL (XRawfile2.dll or XRawfile2_x64.dll) may not be installed and therefore not registered to the COM server' \
            '2) the msFileReader DLL may not be a these paths :\n' + '\n'.join(XRawfile2_dll_path_0)
            sys.exit(msg)
        except Exception as e:
            log.debug(e)
        else:
            log.debug('DLL path : ' + XRawfile2_dll_filename)
            XRawfile2_dll_loaded = True


def _to_float(x):
    try :
        out = float(x)
    except ValueError :
        out = str(x)
    return out


class ThermoRawfile(object):
    
    def __init__(self, filename, **kwargs):
        self.filename = os.path.abspath(filename)
        self.source = None
        
        try:
            log.debug("obj = CreateObject('MSFileReader.XRawfile')")
            obj = CreateObject('MSFileReader.XRawfile')
        except Exception as e:
            log.debug(e)
            try:
                log.debug("obj = CreateObject('XRawfile.XRawfile')")
                obj = CreateObject('XRawfile.XRawfile')
            except Exception as e: 
                log.debug(e)
                sys.exit('Please install the appropriate Thermo MSFileReader version depending of your Python version (32bits or 64bits)')

        self.source = obj

        try:
            error = obj.Open(filename)
        except WindowsError: 
            raise WindowsError(  "RAWfile {0} could not be opened, is the file accessible and not opened in Xcalibur/QualBrowser ?".format(self.filename) )
        if error: raise IOError( "RAWfile {0} could not be opened, is the file accessible ?".format(self.filename) )

        error = obj.SetCurrentController(c_long(0),c_long(1))
        if error:
            obj.Close()
            raise IOError( "Open error {} : {}".format(self.filename,error))

        self.StartTime = self.GetStartTime()
        self.EndTime = self.GetEndTime()
        self.FirstSpectrumNumber = self.GetFirstSpectrumNumber()
        self.LastSpectrumNumber = self.GetLastSpectrumNumber()
        self.LowMass = self.GetLowMass()
        self.HighMass = self.GetHighMass()
        self.MassResolution = self.GetMassResolution()
        self.NumSpectra = self.GetNumSpectra()

        self.InstMethodNames = self.GetInstMethodNames()
        self.NumInstMethods = self.GetNumInstMethods()
        self.NumStatusLog = self.GetNumStatusLog()
        self.NumErrorLog = self.GetNumErrorLog()
        self.NumTuneData = self.GetNumTuneData()
        self.NumTrailerExtra = self.GetNumTrailerExtra()
        self.dll_version = self.Version()
        self.FileName = self.GetFileName()
        self.InstrumentDescription = self.GetInstrumentDescription()
        self.AcquisitionDate = self.GetAcquisitionDate()
        self.InstName = self.GetInstName()
        self.InstModel = self.GetInstModel()
        self.InstSoftwareVersion = self.GetInstSoftwareVersion()
        self.InstHardwareVersion = self.GetInstHardwareVersion()
        
        
    def Close(self): # DONE
        """Closes a raw file and frees the associated memory."""
        self.source.Close()
        
    def Version(self): # DONE : MSFileReader DLL version
        """This function returns the version number for the DLL."""
        MajorVersion, MinorVersion, SubMinorVersion, BuildNumber =  c_long(), c_long(), c_long(), c_long()
        error = self.source.Version(byref(MajorVersion), byref(MinorVersion), byref(SubMinorVersion), byref(BuildNumber))
        if error : raise IOError("Version error :", error)
        return '{}.{}.{}.{}'.format(MajorVersion.value, MinorVersion.value, SubMinorVersion.value, BuildNumber.value)
        
    def GetFileName(self): # DONE
        """Returns the fully qualified path name of an open raw file."""
        pbstrFileName = comtypes.automation.BSTR()
        error = self.source.GetFileName( byref(pbstrFileName) )
        if error : raise IOError("GetFileName error :", error)
        return pbstrFileName.value
        
    def GetCreatorID(self):
        """Returns the creator ID. The creator ID is the logon name of the user when the raw file was acquired."""
        pass

    def GetVersionNumber(self): # DONE
        '''Returns the file format version number'''
        versionNumber =  c_long()
        error = self.source.GetVersionNumber(byref(versionNumber))
        if error : raise IOError("GetVersionNumber error :", error)
        return versionNumber.value
        
    def GetCreationDate(self):
        """Returns the file creation date in DATE format."""
        pass
        
    def IsError(self):
        """Returns the error state flag of the raw file. A return value of TRUE indicates that an error has
        occurred. For information about the error, call the GetErrorCode or GetErrorMessage
        functions."""
        pass
        
    def IsNewFile(self):
        """Returns the creation state flag of the raw file. A return value of TRUE indicates that the file
        has not previously been saved."""
        pass
        
    def IsThereMSData(self):
        """This function checks to see if there is MS data in the raw file. A return value of TRUE means
        that the raw file contains MS data. You must open the raw file before performing this check."""
        pass

    def HasExpMethod(self):
        """This function checks to see if the raw file contains an experimental method. A return value of
        TRUE indicates that the raw file contains the method. You must open the raw file before
        performing this check."""
        pass
        
    def InAcquisition(self):
        """Returns the acquisition state flag of the raw file. A return value of TRUE indicates that the
        raw file is being acquired or that all open handles to the file during acquisition have not been
        closed."""
        pass
        
    def GetErrorCode(self):
        """Returns the error code of the raw file. A return value of 0 indicates that there is no error."""
        pass
        
    def GetErrorMessage(self): # DONE
        """Returns error information for the raw file as a descriptive string. If there is no error, the
        returned string is empty."""
        pbstrErrorMessage = comtypes.automation.BSTR()
        error = self.source.GetErrorMessage(byref(pbstrErrorMessage))
        if error : raise IOError ("GetErrorMessage error : ", error)
        return pbstrErrorMessage.value
        
    def GetWarningMessage(self):
        """Returns warning information for the raw file as a descriptive string. If there is no warning, the
        returned string is empty."""
        pass
        
    def RefreshViewOfFile(self):
        """Refreshes the view of a file currently being acquired. This function provides a more efficient
        mechanism for gaining access to new data in a raw file during acquisition without closing and
        reopening the raw file. This function has no effect with files that are not being acquired."""
        pass


        
    def GetNumberOfControllers(self):
        """Returns the number of registered device controllers in the raw file. A device controller
        represents an acquisition stream such as MS data, UV data, and so on. Devices that do not
        acquire data, such as autosamplers, are not registered with the raw file during acquisition."""
        pass
        
    def GetNumberOfControllersOfType(self):
        """Returns the number of registered device controllers of a particular type in the raw file. See
        Controller Type in the Enumerated Types section for a list of the available controller types
        and their respective values."""
        pass
        
    def GetControllerType(self):
        """Returns the type of the device controller registered at the specified index position in the raw
        file. Index values start at 0. See Controller Type in the Enumerated Types section for a list of
        the available controller types and their respective values."""
        pass
        
    def SetCurrentController(self):
        """Sets the current controller in the raw file. This function must be called before subsequent calls
        to access data specific to a device controller (for example, MS or UV data) may be made. All
        requests for data specific to a device controller are forwarded to the current controller until the
        current controller is changed. The controller number is used to indicate which device
        controller to use if there is more than one registered device controller of the same type (for
        example, multiple UV detectors). Controller numbers for each type are numbered starting
        at 1. See Controller Type in the Enumerated Types section for a list of the available controller
        types and their respective values."""
        pass
        
    def GetCurrentController(self):
        """Gets the current controller type and number for the raw file. The controller number is used to
        indicate which device controller to use if there is more than one registered device controller of
        the same type (for example, multiple UV detectors). Controller numbers for each type are
        numbered starting at 1. See Controller Type in the Enumerated Types section for a list of the
        available controller types and their respective values."""
        pass
        
        
        
    def GetExpectedRunTime(self):
        """Gets the expected acquisition run time for the current controller. The actual acquisition may
        be longer or shorter than this value. This value is intended to allow displays to show the
        expected run time on chromatograms. To obtain an accurate run time value during or after
        acquisition, use the GetEndTime function."""
        pass
        
    def GetNumTrailerExtra(self): # DONE
        """Gets the trailer extra entries recorded for the current controller. Trailer extra entries are only
        supported for MS device controllers and are used to store instrument specific information for
        each scan if used."""
        pnNumberOfTrailerExtraEntries = c_long()
        error = self.source.GetNumTrailerExtra(byref(pnNumberOfTrailerExtraEntries) )
        if error : raise IOError("GetNumTrailerExtra error :", error)
        return pnNumberOfTrailerExtraEntries.value
    

    def GetMaxIntegratedIntensity(self):
        """Gets the highest integrated intensity of all the scans for the current controller. This value is
        only relevant to MS device controllers."""
        pass
        
    def GetMaxIntensity(self):
        """Gets the highest base peak of all the scans for the current controller. This value is only relevant
        to MS device controllers."""
        pass
        


    def GetInletID(self):
        """Gets the inlet ID number for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        pass
        
    def GetErrorFlag(self):
        """Gets the error flag value for the current controller. This value is typically only set for raw files
        converted from other file formats."""
        pass
        
        
    def GetFlags(self):
        """Returns the acquisition flags field for the current controller. This value is typically only set for
        raw files converted from other file formats."""
        pass
        
    def GetAcquisitionFileName(self):
        """Returns the acquisition file name for the current controller. This value is typically only set for
        raw files converted from other file formats."""
        pass
        
    def GetAcquisitionDate(self): # DONE
        """Returns the acquisition date for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        pbstrAcquisitionDate = comtypes.automation.BSTR(None)
        error = self.source.GetAcquisitionDate(byref(pbstrAcquisitionDate))
        if error: raise IOError("GetAcquisitionDate error :", error)
        return pbstrAcquisitionDate.value
        
    def GetOperator(self):
        """Returns the operator name for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        pass
    
    def GetComment1(self):
        """Returns the first comment for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        pass
        
    def GetComment2(self):
        pass
        
    def GetFilters(self):
        """Returns the list of unique scan filters for the raw file. This function is only supported for MS
        device controllers. If the function succeeds, pvarFilterArray points to an array of BSTR fields,
        each containing a unique scan filter, and pnArraySize contains the number of scan filters in the
        pvarFilterArray."""
        pass
            
    def SetMassTolerance(self):
        """This function sets the mass tolerance that will be used with the raw file."""
        pass
        
    def GetMassTolerance(self):
        """This function gets the mass tolerance that is being used with the raw file. To set these values,
        use the SetMassTolerance() function."""
        pass
    
    

        
    ######## INSTRUMENT BEGIN
    def GetInstrumentDescription(self): # DONE
        """Returns the instrument description field for the current controller. This value is typically only
        set for raw files converted from other file formats."""
        pbstrInstrumentDescription = comtypes.automation.BSTR(None)
        error = self.source.GetInstrumentDescription(byref(pbstrInstrumentDescription))
        if error: raise IOError("GetInstrumentDescription error :", error)
        return pbstrInstrumentDescription.value
        
    def GetInstrumentID(self):
        """Gets the instrument ID number for the current controller. This value is typically only set for
        raw files converted from other file formats."""
        pass
        
    def GetInstName(self): # DONE
        """Returns the instrument name, if available, for the current controller."""
        pbstrInstName = comtypes.automation.BSTR(None)
        error = self.source.GetInstName(byref(pbstrInstName))
        if error: raise IOError("GetInstName error :", error)
        return pbstrInstName.value
    
    def GetInstModel(self): # DONE
        """Returns the instrument model, if available, for the current controller."""
        pbstrInstModel = comtypes.automation.BSTR(None)
        error = self.source.GetInstModel(byref(pbstrInstModel))
        if error: raise IOError("GetInstModel error :", error)
        return pbstrInstModel.value
    
    def GetInstSerialNumber(self):
        """Returns the serial number, if available, for the current controller."""
        pass
    
    def GetInstSoftwareVersion(self): # DONE
        '''Returns revision information for the current controller software, if available.'''
        InstSoftwareVersion = comtypes.automation.BSTR()
        error = self.source.GetInstSoftwareVersion(byref(InstSoftwareVersion) )
        if error : raise IOError("GetInstSoftwareVersion error :", error)
        return InstSoftwareVersion.value
                
    def GetInstHardwareVersion(self): # DONE
        '''Returns revision information for the current controller software, if available.'''
        InstHardwareVersion = comtypes.automation.BSTR()
        error = self.source.GetInstHardwareVersion(byref(InstHardwareVersion) )
        if error : raise IOError("GetInstHardwareVersion error :", error)
        return InstHardwareVersion.value
    
    def GetInstFlags(self):
        """Returns the experiment flags, if available, for the current controller. The returned string may
        contain one or more fields denoting information about the type of experiment performed.
        These are the currently defined experiment fields:
        TIM - total ion map
        NLM - neutral loss map
        PIM - parent ion map
        DDZMap - data-dependent ZoomScan map"""
        pass
    
    def GetInstNumChannelLabels(self):
        """Returns the number of channel labels specified for the current controller. This field is only
        relevant to channel devices such as UV detectors, A/D cards, and Analog inputs. Typically, the
        number of channel labels, if labels are available, is the same as the number of configured
        channels for the current controller."""
        pass
    
    def GetInstChannelLabel(self):
        """Returns the channel label, if available, at the specified index for the current controller. This
        field is only relevant to channel devices such as UV detectors, A/D cards, and Analog inputs.
        Channel label indices are numbered starting at 0."""
        pass
    ######## INSTRUMENT END



    
    def GetSegmentedMassListFromScanNum(self, scanNumber): # ?
        pass
        
    def GetScanEventForScanNum(self, scanNumber):
        """This function returns scan event information as a string for the specified scan number."""
        pass
    
    def GetSegmentAndScanEventForScanNum(self, scanNumber): # TODO ?
        """Returns the segment and scan event indexes for the specified scan."""
        pass
    

    def GetCycleNumberFromScanNumber(self, scanNumber):
        """This function returns the cycle number for the scan specified by nScanNumber from the scan
        index structure in the raw file."""
        pass
    
    def GetAValueFromScanNum(self, scanNumber): # ?
        """This function gets the A parameter value in the scan event. The value returned is either 0, 1,
        or 2 for parameter A off, parameter A on, or accept any parameter A, respectively."""
        pass
    
    def GetBValueFromScanNum(self, scanNumber): # ?
        """This function gets the B parameter value in the scan event. The value returned will be either
        0, 1, or 2 for parameter B off, parameter B on, or accept any parameter B, respectively."""
        pass
    
    def GetFValueFromScanNum(self, scanNumber): # ?
        """This function gets the F parameter value in the scan event. The value returned is either 0, 1,
        or 2 for parameter F off, parameter F on, or accept any parameter F, respectively."""
        pass
    
    def GetKValueFromScanNum(self, scanNumber): # ?
        pass
    
    def GetRValueFromScanNum(self, scanNumber): # ?
        pass
    
    def GetVValueFromScanNum(self, scanNumber): # ?
        pass
    
    def GetMSXMultiplexValueFromScanNum(self, scanNumber): # ?
        """This function gets the msx-multiplex parameter value in the scan event. The value returned is
        either 0, 1, or 2 for multiplex off, multiplex on, or accept any multiplex, respectively."""
        pass

    def GetNumberOfMassRangesFromScanNum(self, scanNumber):
        """This function gets the number of MassRange data items in the scan."""
        pass
        
    def GetMassRangeFromScanNum(self, scanNumber):
        """This function retrieves information about the mass range data of a scan (high and low
        masses). You can find the count of mass ranges for the scan by calling
        GetNumberOfMassRangesFromScanNum()."""
        pass
    
    def GetNumberOfSourceFragmentsFromScanNum(self, scanNumber):
        """This function gets the number of source fragments (or compensation voltages) in the scan."""
        pass
    
    def GetSourceFragmentValueFromScanNum(self, scanNumber):
        """This function retrieves information about one of the source fragment values of a scan. It is
        also the same value as the compensation voltage. You can find the count of source fragments
        for the scan by calling GetNumberOfSourceFragmentsFromScanNum ()."""
        pass
        pass
        
    def GetNumberOfSourceFragmentationMassRangesFromScanNum(self, scanNumber):
        """This function gets the number of source fragmentation mass ranges in the scan."""
        pass
    
    def GetSourceFragmentationMassRangeFromScanNum(self, scanNumber):
        """This function retrieves information about the source fragment mass range data of a scan (high
        and low source fragment masses). You can find the count of mass ranges for the scan by calling
        GetNumberOfSourceFragmentationMassRangesFromScanNum ()."""
        pass
    
    def GetIsolationWidthForScanNum(self, scanNumber):
        """This function returns the isolation width for the scan specified by nScanNumber and the
        transition specified by nMSOrder from the scan event structure in the raw file."""
        pass
    
    def GetCollisionEnergyForScanNum(self, scanNumber):
        """This function returns the collision energy for the scan specified by nScanNumber and the
        transition specified by nMSOrder from the scan event structure in the raw file. """
        pass
     
        
    def GetActivationTypeForScanNum(self, scanNumber):
        """This function returns the activation type for the scan specified by nScanNumber and the
        transition specified by nMSorder from the scan event structure in the RAW file.
        The value returned in the pnActivationType variable is one of the following:
        CID  0
        MPD 1
        ECD  2
        PQD 3
        ETD 4
        HCD 5
        Any activation type 6
        SA 7
        PTR 8
        NETD 9
        NPTR 10"""
        pass
        
    def GetMassAnalyzerTypeForScanNum(self, scanNumber):
        """This function returns the mass analyzer type for the scan specified by nScanNumber from the
        scan event structure in the RAW file. The value of nScanNumber must be within the range of
        scans or readings for the current controller. The range of scans or readings for the current
        controller may be obtained by calling GetFirstSpectrumNumber and
        GetLastSpectrumNumber.
        The value returned in the pnMassAnalyzerType variable is one of the following:
        ITMS  0
        TQMS 1
        SQMS  2
        TOFMS 3
        FTMS 4
        Sector 5"""
        pass
    
    def GetDetectorTypeForScanNum(self, scanNumber):
        """This function returns the detector type for the scan specified by nScanNumber from the scan
        event structure in the RAW file.
        The value returned in the pnDetectorType variable is one of the following:
        CID  0
        PQD  1
        ETD  2
        HCD  3"""
        pass
        
    def GetScanTypeForScanNum(self, scanNumber):
        """This function returns the scan type for the scan specified by nScanNumber from the scan
        event structure in the RAW file.
        The value returned in the pnScanType variable is one of the following:
        ScanTypeFull  0
        ScanTypeSIM  1
        ScanTypeZoom  2
        ScanTypeSRM  3"""
        pass
        

     
    def GetNumberOfMassCalibratorsFromScanNum(self, scanNumber): # DONE
        """This function gets the number of mass calibrators (each of which is a double) in the scan."""
        pnNumMassCalibrators = c_long()
        c_long(scanNumber)
        error = self.source.GetNumberOfMassCalibratorsFromScanNum(c_long(scanNumber), byref(pnNumMassCalibrators) )
        if error : raise IOError("GetNumberOfMassCalibratorsFromScanNum error :", error)
        return pnNumMassCalibrators.value
        
    def GetMassCalibrationValueFromScanNum(self, scanNumber, MassCalibrationIndex): # DONE
        """This function retrieves information about one of the mass calibration data values of a scan.
        You can find the count of mass calibrations for the scan by calling
        GetNumberOfMassCalibratorsFromScanNum()."""
        pdMassCalibrationValue = c_double()
        error = self.source.GetMassCalibrationValueFromScanNum(c_long(scanNumber), c_long(MassCalibrationIndex), byref(pdMassCalibrationValue) )
        if error : raise IOError("GetMassCalibrationValueFromScanNum error :", error)
        return pdMassCalibrationValue.value
     
    def GetFilterMassPrecision(self):
        """This function gets the mass precision for the filter associated with an MS scan."""
        pass
        
    def GetMassPrecisionEstimate(self, scanNumber): # DONE
        """This function is only applicable to scanning devices such as MS. It gets the mass precision
        information for an accurate mass spectrum (that is, acquired on an FTMS- or Orbitrap-class
        instrument).
         The format of the mass list returned is an array of double-precision
        values in the order of intensity, mass, accuracy in MMU, accuracy in PPM, and resolution."""
        pnArraySize = c_long()
        pvarMassList = comtypes.automation.VARIANT()
        error = self.source.GetMassPrecisionEstimate( c_long(scanNumber), byref(pvarMassList), byref(pnArraySize) )
        if error : raise IOError("GetMassPrecisionEstimate error :", error)
        return pvarMassList.value
     
    def IsQExactive(self): # DONE 
        """Checks the instrument name by calling GetInstName() and comparing the result to Q
        Exactive Orbitrap. If it matches, IsQExactive pVal is set to TRUE. Otherwise, pVal is set to
        FALSE.
        
        NOTE : not implemented in MSFileReader 3.0 SP2 (3.0.29.0)
        """
        # pVal = c_bool()
        pVal = c_long()
        error = self.source.IsQExactive( byref(pVal) )
        if error : raise IOError("IsQExactive error :", error)
        return pVal.value
    

    
    def GetMassResolution(self): # DONE
        """Gets the mass resolution value recorded for the current controller. The value is returned as one
        half of the mass resolution. For example, a unit resolution controller returns a value of 0.5.
        This value is only relevant to scanning controllers such as MS."""
        dHalfMassRes = c_double()
        error = self.source.GetMassResolution(byref(dHalfMassRes))
        if error : raise IOError("GetMassResolution error :", error)
        return dHalfMassRes.value
        
    def GetLowMass(self): # DONE
        """Gets the lowest mass or wavelength recorded for the current controller. This value is only
        relevant to scanning devices such as MS or PDA."""
        pdLowMass = c_double()
        error = self.source.GetLowMass(byref(pdLowMass))
        if error : raise IOError("GetLowMass error :", error)
        return pdLowMass.value
        
    def GetHighMass(self): # DONE
        """Gets the highest mass or wavelength recorded for the current controller. This value is only
        relevant to scanning devices such as MS or PDA."""
        pdHighMass = c_double()
        error = self.source.GetHighMass(byref(pdHighMass))
        if error : raise IOError("GetHighMass error :", error)
        return pdHighMass.value
    
    def GetStartTime(self): # DONE
        """Gets the start time of the first scan or reading for the current controller. This value is typically
        close to zero unless the device method contains a start delay."""
        pdStartTime = c_double()
        error = self.source.GetStartTime(byref(pdStartTime))
        if error : raise IOError("GetStartTime error :", error)
        return pdStartTime.value
    
    def GetEndTime(self): # DONE
        pdEndTime = c_double()
        error = self.source.GetEndTime(byref(pdEndTime))
        if error : raise IOError("GetEndTime error :", error)
        return pdEndTime.value
    
    def GetNumSpectra(self): # DONE
        """Gets the number of spectra acquired by the current controller. For non-scanning devices like 
        UV detectors, the number of readings per channel is returned."""
        numSpectra = c_long()
        error = self.source.GetNumSpectra(byref(numSpectra))
        if error : raise IOError("GetNumSpectra error :", error)
        return numSpectra.value
        
    def GetFirstSpectrumNumber(self): # DONE
        """Gets the first scan or reading number for the current controller. If data has been acquired, this
        value is always one."""
        pnFirstSpectrum = c_long()
        error = self.source.GetFirstSpectrumNumber(byref(pnFirstSpectrum))
        if error : raise IOError("GetFirstSpectrumNumber error :", error)
        return pnFirstSpectrum.value
        
    def GetLastSpectrumNumber(self): # DONE
        """Gets the last scan or reading number for the current controller."""
        pnLastSpectrum = c_long()
        error = self.source.GetLastSpectrumNumber(byref(pnLastSpectrum))
        if error : raise IOError("GetLastSpectrumNumber error :", error)
        return pnLastSpectrum.value
        
    def ScanNumFromRT(self,dRT): # DONE
        """Returns the closest matching scan number that corresponds to dRT for the current controller.
        For non-scanning devices, such as UV, the closest reading number is returned. The value of
        dRT must be within the acquisition run time for the current controller. The acquisition run
        time for the current controller may be obtained by calling GetStartTime and GetEndTime."""
        pnScanNumber = c_long()
        error = self.source.ScanNumFromRT(c_double(dRT),byref(pnScanNumber))
        if error : raise IOError( "scan {}, ScanNumFromRT error : {}".format(pnScanNumber,error) )
        else: return pnScanNumber.value

    def RTFromScanNum(self, nScanNumber): # DONE
        """Returns the closest matching run time or retention time that corresponds to nScanNumber for
        the current controller. For non-scanning devices, such as UV, the nScanNumber is the reading
        number."""
        pdRT = c_double()
        error = self.source.RTFromScanNum(c_long(nScanNumber),byref(pdRT))
        if error : raise IOError( "scan {}, RTFromScanNum error : {}".format(nScanNumber,str(error)) )
        else: return pdRT.value
        
    def IsProfileScanForScanNum(self, scanNumber): # DONE
        """Returns TRUE if the scan specified by nScanNumber is a profile scan, FALSE if the scan is a
        centroid scan."""
        pbIsProfileScan = c_long()
        error = self.source.IsProfileScanForScanNum(c_long(scanNumber), byref(pbIsProfileScan) )
        if error : raise IOError("IsProfileScanForScanNum error :", error)
        return bool(pbIsProfileScan.value)
        
    def IsCentroidScanForScanNum(self, scanNumber): # DONE
        """Returns TRUE if the scan specified by nScanNumber is a centroid scan, FALSE if the scan is a
        profile scan."""
        pbIsCentroidScan = c_long()
        error = self.source.IsCentroidScanForScanNum(c_long(scanNumber), byref(pbIsCentroidScan) )
        if error : raise IOError("IsCentroidScanForScanNum error :", error)
        return bool(pbIsCentroidScan.value)
        
    def GetFilterForScanNum(self, nScanNumber): # DONE ex:"FTMS + c NSI Full ms [300.00-1800.00]"
        """Returns the closest matching run time that corresponds to nScanNumber for the current
        controller. This function is only supported for MS device controllers. The value of
        nScanNumber must be within the range of scans for the current controller. The range of scans
        or readings for the current controller may be obtained by calling GetFirstSpectrumNumber
        and GetLastSpectrumNumber."""
        pbstrFilter = comtypes.automation.BSTR(None)
        error = self.source.GetFilterForScanNum(nScanNumber,byref(pbstrFilter))
        if error: raise IOError( "scan {}, GetFilterForScanNum error : {}".format(nScanNumber,str(error)) )
        else: return pbstrFilter.value
        
     # DONE
    def GetMassListFromScanNum(self, scanNumber, 
                                    filter="", 
                                    intensityCutoffType = 0, 
                                    intensityCutoffValue = 0, 
                                    maxNumberOfPeaks = 0, 
                                    centroidResult = False, 
                                    centroidPeakWidth = 0.0):
        '''To reduce the number of low intensity data peaks returned, an intensity cutoff,
        nIntensityCutoffType, may be applied. The available types of cutoff are None, Absolute
        (intensity), and Relative (relative intensity). The value of nIntensityCutoffValue is interpreted
        based on the value of nIntensityCutoffType :
        0 None (all values returned)
        1 Absolute (in intensity units)
        2 Relative (to base peak)

        To limit the total number of data peaks that are returned in the mass list, set
        nMaxNumberOfPeaks to a value greater than zero. To have all data peaks returned, set
        nMaxNumberOfPeaks to zero.
        
        To have profile scans centroided, set bCentroidResult to TRUE. This parameter is ignored for
        centroid scans.
        
        The pvarPeakFlags variable is currently (MSFileReader 3.0 SP2 (3.0.29.0), Revision A, July 2014) not used. This variable is reserved for future use to
        return flag information, such as saturation, about each mass intensity pair.
        
        FA (MSFileReader 3.0 SP2 (3.0.29.0), Revision A, July 2014): Returns Profile data for MS1 scans (if centroidResult is False) 
        and Centroid data for MS2 scans (no matters centroidResult is True or False). 
        Do not use centroidResult=True to retrieve centroid MS1 data but GetLabelData instead.
        '''

        massList = comtypes.automation.VARIANT()
        flags = comtypes.automation.VARIANT()
        pnArraySize2 = c_long()

        error = self.source.GetMassListFromScanNum(c_long(scanNumber), filter, intensityCutoffType, 
            intensityCutoffValue, maxNumberOfPeaks, centroidResult, c_double(centroidPeakWidth), massList, flags, byref(pnArraySize2))
        if error : raise IOError ("GetMassListFromScanNum error : ",error)
        return massList.value, flags.value
        
     # DONE
    def GetMassListRangeFromScanNum(self, scanNumber, 
                                            start_mz=None, 
                                            stop_mz=None, 
                                            filter="", 
                                            intensityCutoffType = 0, 
                                            intensityCutoffValue = 0, 
                                            maxNumberOfPeaks = 0, 
                                            centroidResult = True, 
                                            centroidPeakWidth =0.0):
        """FA: GetMassListFromScanNum avec possibilite de filtrer sur m/z, intensite ..."""
        if start_mz == None: start_mz = self.LowMass
        if stop_mz == None: stop_mz = self.HighMass
        # scanNumber # (long FAR* pnScanNumber, 
        #filter ="Full ms "                                 # LPCTSTR szFilter, 
        # intensityCutoffType = 0                             # long nIntensityCutoffType, 
        # intensityCutoffValue = 0                            # long nIntensityCutoffValue, 
        # maxNumberOfPeaks = 0                                # long nMaxNumberOfPeaks, 
        # centroidResult = 1                              # BOOL bCentroidResult, 
        # NOT in the doc : centroidPeakWidth =0.0                              # pdCentroidPeakWidth
        peakList = comtypes.automation.VARIANT()            # VARIANT FAR* pvarMassList,
        peakFlags = comtypes.automation.VARIANT()               # VARIANT FAR* pvarPeakFlags, 
        massRange1 = "{}-{}".format(start_mz, stop_mz) #LPCTSTR csMassRanges1, 
        pnArraySize = c_long()                              # long FAR* pnArraySize)
             # rawfile.source.GetMassListRangeFromScanNum(c_long(3366),"",0,0,0,0,c_double(0.0),peakList,flags,massRange1,byref(pnArraySize))
        error = self.source.GetMassListRangeFromScanNum(c_long(scanNumber), filter, intensityCutoffType, 
            intensityCutoffValue, maxNumberOfPeaks, centroidResult  ,c_double(centroidPeakWidth) ,peakList, peakFlags, massRange1, byref(pnArraySize))
        if error : raise IOError("GetMassListRangeFromScanNum error :", error)
        return peakList.value, peakFlags.value

    def GetAverageMassList(self, pnFirstAvgScanNumber,
                                pnLastAvgScanNumber,
                                pnFirstBkg1ScanNumber=0,
                                pnLastBkg1ScanNumber=0,
                                pnFirstBkg2ScanNumber=0,
                                pnLastBkg2ScanNumber=0,
                                szFilter="",
                                nIntensityCutoffType=0,
                                nIntensityCutoffValue=0,
                                nMaxNumberOfPeaks=0):
        """If no scan filter is supplied, the scans between pnFirstAvgScanNumber and pnLastAvgScanNumber that match the filter of the pnFirstAvgScanNumber, inclusive, are returned. Likewise, all the scans between pnFirstBkg1ScanNumber and pnLastBkg1ScanNumber and pnFirstBkg2ScanNumber and pnLastBkg2ScanNumber, inclusive, are averaged and subtracted from the pnFirstAvgScanNumber to pnLastAvgScanNumber averaged scans. 
        If a scan filter is provided, the scans in the preceding scan number ranges that match the scan filter are utilized in obtaining the background subtracted mass list. The specified scan numbers must be valid for the current controller. 
        If no background subtraction is performed, the background scan numbers should be set to zero. On return, the scan number variables contain the actual first and last scan numbers, respectively, for the scans used."""
        pass
        
    def GetAveragedMassSpectrum(self, listOfScanNumbers):
        """returns the average spectrum for the list of scans that are supplied
        to the function in pnScanNumbers.
        The format of the mass list returned is an array of double precision values in mass intensity pairs in ascending mass order (for example, mass 1, intensity 1, mass 2, intensity 2, mass 3, intensity 3, and so on).
        The pvarPeakFlags variable is currently not used. This variable is reserved for future use to return flag information, such as saturation, about each mass intensity pair"""
        # return peakList.value, peakFlags.value
        pass
        
    def GetAveragedLabelData(self, listOfScanNumbers):
        """This method enables you to read the averaged FT-PROFILE labels for the list of scans represented by the pnScanNumbers.
         The format of the mass list returned is an array of double precision values in mass intensity pairs in ascending mass order, for example, mass 1, intensity 1, mass 2, intensity 2, mass 3, intensity 3.
         The flags are returned as unsigned char values. These flags are saturated, fragmented, merged, exception, reference, and modified."""
         # return peakList.value, peakFlags.value
        pass
        
    def GetSummedMassSpectrum(self, listOfScanNumbers):
        """returns the summed spectrum for the list of scans that are
        supplied to the function in pnScanNumbers.
        The format of the mass list returned is an array of double precision values in mass intensity pairs in ascending mass order (for example, mass 1, intensity 1, mass 2, intensity 2, mass 3, intensity 3, and so on).
        The pvarPeakFlags variable is currently not used. This variable is reserved for future use to return flag information, such as saturation, about each mass intensity pair"""
        # return peakList.value, peakFlags.value
        pass
        
        
    def IncludeReferenceAndExceptionData(self, boolean): # DONE
        """Controls whether the reference and exception data is included in the spectral data when using the GetLabelData method. Reference and exception peaks are only present on instruments that can collect FTMS data. A value of TRUE causes the reference and exception data to be included in the spectrum, and a value of FALSE excludes this data."""
        error = self.source.IncludeReferenceAndExceptionData(c_bool(boolean))
        if error : raise IOError("IncludeReferenceAndExceptionData error :", error)
        return
        
    def GetLabelData(self, scanNumber):  # DONE : This is higher level function than GetMassListRangeFromScanNum, only for profile data (MS1).
        """This method enables you to read the FT-PROFILE labels of a scan represented by the scanNumber.
        The label data contains values of mass (double), intensity (double), resolution (float), baseline (float), noise (float) and charge (int).
        The flags are returned as unsigned char values. 
        The flags are saturated, fragmented, merged, exception, reference, and modified.
        NOTE : This is a higher level function than GetMassListRangeFromScanNum, only for profile data (MS1).
        """
        labels = comtypes.automation.VARIANT()
        flags = comtypes.automation.VARIANT()
        error = self.source.GetLabelData(labels,flags,c_long(scanNumber))
        if error : raise IOError("GetLabelData error :", error)
        return labels.value, flags.value    # tuple de taille 2 contenant chacun 6 vecteurs
        
    def GetNoiseData(self, scanNumber): # DONE, already included in GetLabelData ?
        """This method enables you to read the FT-PROFILE noise packets of a scan represented by the scanNumber.
        The noise packets contain values of mass (double), noise (float) and baseline (float).
        """
        NoisePacket = comtypes.automation.VARIANT()
        error = self.source.GetNoiseData(NoisePacket,c_long(scanNumber))
        if error : raise IOError("GetNoiseData error :", error)
        return NoisePacket.value
        
        
        
    def GetAllMSOrderData(self, scanNumber): # DONE, same as GetLabelData ?
        """This method enables you to obtain all of the precursor information from the scan (event).
        The FT-PROFILE labels of a scan are represented by nScanNumber. PvarFlags can be NULL if you do not want to receive the flags. The label data contains values of mass (double), intensity (double), resolution (float), baseline (float), noise (float), and charge (int). 
        The flags are returned as unsigned character values. The flags are saturated, fragmented, merged, exception, reference, and modified."""
        pvarDoubleData = comtypes.automation.VARIANT()
        pvarFlagsData = comtypes.automation.VARIANT()
        pnNumberOfMSOrders = c_long()
        error = self.source.GetAllMSOrderData(scanNumber,pvarDoubleData, pvarFlagsData, byref(pnNumberOfMSOrders) )
        return pvarDoubleData.value, pvarFlagsData.value, pnNumberOfMSOrders.value
        
    def GetFullMSOrderPrecursorDataFromScanNum(self, scanNumber): # TODO
        nMSOrder = c_long()
        pvarFullMSOrderPrecursorInfo = comtypes.automation.VARIANT()
        error = self.source.GetFullMSOrderPrecursorDataFromScanNum(scanNumber,pvarDoubleData, pvarFlagsData, byref(pnNumberOfMSOrders) )
        return pvarDoubleData.value, pvarFlagsData.value, pnNumberOfMSOrders.value
        
    def GetMSOrderForScanNum(self, scanNumber): # DONE
        """This function returns the MS order for the scan specified by nScanNumber from the scan
        event structure in the raw file.
        The value returned in the pnScanType variable is one of the following:
        Neutral gain -3
        Neutral loss -2
        Parent scan -1
        Any scan order 0
        MS  1
        MS2  2
        MS3  3
        MS4  4
        MS5  5
        MS6  6
        MS7  7
        MS8  8
        MS9  9
        """

        massOrder = c_long()
        error = self.source.GetMSOrderForScanNum(c_long(scanNumber),byref(massOrder))
        if error : raise IOError( "scan {} : GetMSOrderForScanNum error : {}".format(scanNumber,error) )
        elif scanNumber >= self.FirstSpectrumNumber and scanNumber <= self.LastSpectrumNumber : return massOrder.value
        else: return None
        
    def GetNumberOfMSOrdersFromScanNum(self, scanNumber):
        """This function gets the number of MS reaction data items in the scan event for the scan
        specified by nScanNumber and the transition specified by nMSOrder from the scan event
        structure in the raw file."""
        pass
        
        
    # # # # # # # # # # # # # PRECURSOR BEGIN
    def GetPrecursorInfoFromScanNum(self, scanNumber):  # DONE but VARIANT conversion to struct does not work : we only retrieve dIsolationMass and dMonoIsoMass AND does not work with Qexactive files
        """This function is used to retrieve information about the parent scans of a data-dependent MS n
        scan.
        You retrieve the scan number of the parent scan, the isolation mass used, the charge state, and
        the monoisotopic mass as determined by the instrument firmware. You will obtain access to
        the scan data of the parent scan in the form of a XSpectrumRead object.
        Further refine the charge state and the monoisotopic mass values from the actual parent scan
        data.
        NOTE : !!! VARIANT conversion to struct does not work : we only retrieve dIsolationMass and dMonoIsoMass AND this does not work with Qexactive files...
        """
        # struct PrecursorInfo
        # {
        # double dIsolationMass; # OK
        # double dMonoIsoMass; # OK
        # long nChargeState; # NOK but can be retrieved with GetTrailerExtraForScanNum
        # long nScanNumber; # NOK but last MS1...
        # }
        pvarPrecursorInfos = comtypes.automation.VARIANT()
        
        # https://pythonhosted.org/comtypes/#converting-data-types
        # pvarPrecursorInfos = array.array('f')
        
        pnArraySize = c_long()
        
        error = self.source.GetPrecursorInfoFromScanNum(scanNumber, pvarPrecursorInfos, byref(pnArraySize) )
        # HRESULT GetPrecursorInfoFromScanNum(long nScanNumber, 
                                        # VARIANT* pvarPrecursorInfos, 
                                        # LONG* pnArraySize)
        # print( "pnArraySize", pnArraySize )
        
        if error : raise IOError("GetPrecursorInfoFromScanNum error :", error)
        
        # http://stackoverflow.com/questions/386753/how-do-i-convert-part-of-a-python-tuple-byte-array-into-an-integer
        # http://docs.python.org/library/struct.html
        # import struct
        # from array import array
        # return struct.unpack_from('ddll',pvarPrecursorInfos) # WRONG : les 2 premières valeurs du vecteur sont dMonoIsoMass et dIsolationMass
        
        
        # http://stackoverflow.com/questions/1825715/how-to-pack-and-unpack-using-ctypes-structure-str
        # class PrecursorInfo(Structure):
            # _fields_ = [
                # ("dIsolationMass", c_double),
                # ("dMonoIsoMass", c_double),
                # ("nChargeState", c_long),
                # ("nScanNumber", c_long),
            # ]
            # def receiveSome(self, bytes):
                # fit = min(len(bytes), ctypes.sizeof(self))
                # ctypes.memmove(ctypes.addressof(self), bytes, fit)
        # p = PrecursorInfo()
        # result = p.receiveSome(pvarPrecursorInfos) # TypeError: object of type 'tagVARIANT' has no len()
        

        
        # pvarPrecursorInfos est un vecteur de 24 valeurs : 
        # les 2 premières varient en fonction du scanNumber et se révèlent être dIsolationMass , dMonoIsoMass
        # les 22 suivantes NE varient PASen fonction du scanNumber...

        # print(pvarPrecursorInfos.value) 
        # return 
        try: 
            dMonoIsoMass, dIsolationMass = pvarPrecursorInfos.value[:2]
        except ValueError: # need more than 0 values to unpack
            return None, None
        else:
            return dIsolationMass , dMonoIsoMass
        
    def GetPrecursorMassForScanNum(self, scanNumber, massOrder): # DONE
        """This function returns the precursor mass for the scan specified by nScanNumber and the
        transition specified by nMSorder from the scan event structure in the RAW file."""
        precursorMass = c_double()
        error = self.source.GetPrecursorMassForScanNum(c_long(scanNumber),c_long(massOrder),byref(precursorMass))
        if error : raise IOError( "scan {} : GetPrecursorMassForScanNum error : {}".format(scanNumber,error) )
        elif scanNumber >= self.FirstSpectrumNumber and scanNumber <= self.LastSpectrumNumber : return precursorMass.value
        else: return None
        
    def GetPrecursorRangeForScanNum(self, scanNumber, nMSOrder, ): # DONE
        """This function returns the first and last precursor mass values of the range and whether they are valid for the scan specified by nScanNumber and the transition specified by nMSOrder from the scan event structure in the raw file."""
        pdFirstPrecursorMass = c_double()
        pdLastPrecursorMass = c_double()
        pbIsValid = c_bool()
        error = self.source.GetPrecursorRangeForScanNum(c_long(scanNumber), c_long(nMSOrder), byref(pdFirstPrecursorMass), byref(pdLastPrecursorMass), byref(pbIsValid) )
        if error : raise IOError("GetPrecursorRangeForScanNum error :", error)
        return pdFirstPrecursorMass.value, pdLastPrecursorMass.value, pbIsValid.value
    # # # # # # # # # # # # # PRECURSOR END


        

    ############################################### XCALIBUR INTERFACE BEGIN
    def GetScanHeaderInfoForScanNum(self,scanNumber): # DONE "View/Scan header", upper part
        """For a given scan number, this function returns information from the scan header for the
        current controller.

        The validity of these parameters depends on the current controller. For example, pdLowMass,
        pdHighMass, pdTIC, pdBasePeakMass, and pdBasePeakIntensity are only likely to be set on
        return for MS or PDA controllers. PnNumChannels is only likely to be set on return for
        Analog, UV, and A/D Card controllers. PdUniformTime, and pdFrequency are only likely to be
        set on return for UV, and A/D Card controllers and may be valid for Analog controllers. In
        cases where the value is not set, a value of zero is returned.
        
        NOTE : XCALIBUR INTERFACE "View/Scan header", upper part
        """
        # long nScanNumber, 
        header = {}
        header['numPackets'] = c_long() # long FAR* pnNumPackets,    
        header['StartTime'] = c_double()                    # double FAR* pdStartTime,
        header['LowMass'] = c_double() # double FAR* pdLowMass, 
        header['HighMass'] = c_double() # double FAR* pdHighMass, 
        header['TIC'] = c_double() # double FAR* pdTIC, 
        header['BasePeakMass'] = c_double() # double FAR* pdBasePeakMass, 
        header['BasePeakIntensity'] = c_double() # double FAR* pdBasePeakIntensity, 
        header['numChannels'] = c_long() # long FAR* pnNumChannels,
        header['uniformTime'] = c_long() # long pbUniformTime,  
        header['Frequency'] = c_double() # double FAR* pdFrequency
        error = self.source.GetScanHeaderInfoForScanNum(c_long(scanNumber), header['numPackets'], header['StartTime'], header['LowMass'], header['HighMass'], 
                        header['TIC'], header['BasePeakMass'], header['BasePeakIntensity'], header['numChannels'], header['uniformTime'], header['Frequency'])
        if error : raise IOError("GetScanHeaderInfoForScanNum error :", error)
        for k in header:
            header[k] = header[k].value
        return header
        
    def GetTrailerExtraForScanNum(self,scanNum): # DONE "View/Scan header", lower part
        """Returns the recorded trailer extra entry labels and values for the current controller. This
        function is only valid for MS controllers.
        
        NOTE : XCALIBUR INTERFACE "View/Scan header", lower part
        """
        labels = comtypes.automation.VARIANT()
        values = comtypes.automation.VARIANT()
        val_num = c_long()
        error = self.source.GetTrailerExtraForScanNum(c_long(scanNum),labels,values,val_num)
        if error : raise IOError("GetTrailerExtraForScanNum error :", error)
        return dict(zip( map(lambda x: str(x[:-1]), labels.value) , map(_to_float, values.value) ))
        
    def GetNumTuneData(self): # DONE
        """Gets the number of tune data entries recorded for the current controller. Tune Data is only
        supported by MS controllers. Typically, if there is more than one tune data entry, each tune
        data entry corresponds to a particular acquisition segment."""
        pnNumTuneData = c_long()
        error = self.source.GetNumTuneData(byref(pnNumTuneData) )
        if error : raise IOError("GetNumTuneData error :", error)
        return pnNumTuneData.value
        
    def GetTuneData(self, nSegmentNumber): # DONE "View/Report/Tune Method"
        """Returns the recorded tune parameter labels and values for the current controller. This
        function is only valid for MS controllers. The value of nSegmentNumber must be within the
        range of one to the number of tune data items recorded for the current controller. The
        number of tune data items for the current controller may be obtained by calling
        GetNumTuneData.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Tune Method"
        """
        pvarLabels = comtypes.automation.VARIANT() 
        pvarValues = comtypes.automation.VARIANT() 
        pnArraySize = c_long()
        error = self.source.GetTuneData(c_long(nSegmentNumber),pvarLabels,pvarValues,byref(pnArraySize) )
        if error : raise IOError("GetTuneData error :", error)
        # return dict(zip(pvarLabels.value,pvarValues.value))
        # return dict(zip([label.rstrip(':') for label in pvarLabels.value],pvarValues.value))
        result = []
        for label, value in zip(pvarLabels.value,pvarValues.value):
            result.append(label)
            result.append(value)
            result.append('\n')
        return ''.join(result)
        
    def GetNumInstMethods(self): # DONE
        pnNumInstMethods = c_long()
        error = self.source.GetNumInstMethods(byref(pnNumInstMethods) )
        if error : raise IOError("GetNumInstMethods error : ", error) 
        return pnNumInstMethods.value
        """Returns the number of instrument methods contained in the raw file. Each instrument used
        in the acquisition with a method that was created in Instrument Setup (for example,
        autosampler, LC, MS, PDA) has its instrument method contained in the raw file."""
        pass
        
    def GetInstMethod(self, instMethodItem): # DONE "View/Report/Instrument Method"
        """Returns the channel label, if available, at the specified index for the current controller. This
        field is only relevant to channel devices such as UV detectors, A/D cards, and Analog inputs.
        Channel labels indices are numbered starting at 0.
        Returns the instrument method, if available, at the index specified in nInstMethodItem. The
        instrument method indices are numbered starting at 0. The number of instrument methods
        are obtained by calling GetNumInstMethods.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Instrument Method"
        """
        strInstMethod = comtypes.automation.BSTR()
        error = self.source.GetInstMethod(c_long(instMethodItem), byref(strInstMethod) )
        if error : raise IOError ("GetInstMethod error :", error)
        if sys.version_info.major == 2:
            return strInstMethod.value.encode('utf-8').replace('\r\n','\n')
        elif sys.version_info.major == 3:
            return strInstMethod.value.replace('\r\n','\n')
        
    def GetInstMethodNames(self): # DONE
        """This function returns the recorded names of the instrument methods for the current
        controller."""
        pnArraySize = c_long(0)
        pvarNames = comtypes.automation.VARIANT()
        error = self.source.GetInstMethodNames( byref(pnArraySize), byref(pvarNames) )
        if error : raise IOError("GetInstMethodNames error :", error)
        return pvarNames.value
        
    def ExtractInstMethodFromRaw(self,instMethodFileName): # DONE
        """This function enables you to save the embedded instrument method in the raw file in a
        separated method (.meth)) file. It overwrites any pre-existing method file in the same path
        with the same name."""
        error = self.source.ExtractInstMethodFromRaw(comtypes.automation.BSTR(instMethodFileName))
        if error : raise IOError("ExtractInstMethodFromRaw error :", error)
        return
    
    # # # # # # # "View/Report/Sample Information" BEGIN
    def GetVialNumber(self):
        """Gets the vial number for the current controller. This value is typically only set for raw files
        converted from other file formats.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetInjectionVolume(self):
        """Gets the injection volume for the current controller. This value is typically only set for raw
        files converted from other file formats.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetInjectionAmountUnits(self):
        """Returns the injection amount units for the current controller. This value is typically only set
        for raw files converted from other file formats.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSampleVolume(self):
        """Gets the sample volume value for the current controller. This value is typically only set for raw
        files converted from other file formats.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSampleWeight(self):
        """Gets the sample weight value for the current controller. This value is typically only set for raw
        files converted from other file formats.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSampleAmountUnits(self):
        """Returns the sample amount units for the current controller. This value is typically only set for
        raw files converted from other file formats.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
    
    def GetSampleVolumeUnits(self):
        """Returns the sample volume units for the current controller. This value is typically only set for
        raw files converted from other file formats.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowNumber(self):
        """Returns the sequence row number for this sample in an acquired sequence. The numbering
        starts at 1.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowSampleType(self):
        """Returns the sequence row sample type for this sample. See Sample Type in the Enumerated
        Types section for the possible sample type values.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowDataPath(self):
        """Returns the path of the directory where this raw file was acquired.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowRawFileName(self):
        """Returns the file name of the raw file when the raw file was acquired. This value is typically
        used in conjunction with GetSeqRowDataPath to obtain the fully qualified path name of the
        raw file when it was acquired.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowSampleName(self):
        """Returns the sample name value from the sequence row of the raw file.
        
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowSampleID(self):
        """Returns the sample ID value from the sequence row of the raw file.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowComment(self):
        """Returns the comment field from the sequence row of the raw file.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowLevelName(self):
        """Returns the level name from the sequence row of the raw file. This field is empty except for
        standard and QC sample types, which may contain a value if a processing method was
        specified in the sequence at the time of acquisition.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowUserText(self):
        """Returns a user text field from the sequence row of the raw file. There are five user text fields in
        the sequence row that are indexed 0 through 4.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowInstrumentMethod(self):
        """Returns the fully qualified path name of the instrument method used to acquire the raw file.
        If the raw file is created by file format conversion or acquired from a tuning program, this
        field is empty.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowProcessingMethod(self):
        """Returns the fully qualified path name of the processing method specified in the sequence used
        to acquire the raw file. If no processing method is specified at the time of acquisition, this field
        is empty.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowCalibrationFile(self):
        """Returns the fully qualified path name of the calibration file specified in the sequence used to
        acquire the raw file. If no calibration file is specified at the time of acquisition, this field is
        empty.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowVial(self):
        """Returns the vial or well number of the sample when it was acquired. If the raw file is not
        acquired using an autosampler, this value should be ignored.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowInjectionVolume(self):
        """Returns the autosampler injection volume from the sequence row for this sample.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowSampleWeight(self):
        """Returns the sample weight from the sequence row for this sample.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowSampleVolume(self):
        """Returns the sample volume from the sequence row for this sample.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowISTDAmount(self):
        """Returns the bulk ISTD correction amount from the sequence row for this sample.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowDilutionFactor(self):
        """Returns the bulk dilution factor (volume correction) from the sequence row for this sample.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowUserLabel(self):
        """Returns a user label field from the sequence row of the raw file. There are five user label fields
        in the sequence row that are indexed 0 through 4. The user label fields correspond one-to-one
        with the user text fields.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
        
    def GetSeqRowUserTextEx(self):
        """This function returns a user text field from the sequence row of the raw file. There are five
        user text fields in the sequence row that are indexed 0 through 4.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
    
    def GetSeqRowBarcode(self):
        """This function returns the barcode used to acquire the raw file. This field is empty if the raw
        file was created by file format conversion or acquired from a tuning program.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
    
    def GetSeqRowBarcodeStatus(self):
        """This function returns the barcode status from the raw file. This field is empty if the raw file
        was created by file format conversion or acquired from a tuning program.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Sample Information" part
        """
        pass
    # # # # # # # "View/Report/Sample Information" END
    
    def GetNumStatusLog(self): # DONE
        """Gets the number of status log entries recorded for the current controller."""
        pnNumberOfStatusLogEntries = c_long()
        error = self.source.GetNumStatusLog(byref(pnNumberOfStatusLogEntries))
        if error : raise IOError("GetNumStatusLog error :", error)
        return pnNumberOfStatusLogEntries.value
        
    def GetStatusLogForScanNum(self, scanNumber): # DONE "View/Report/Status Log"
        """Returns the recorded status log entry labels and values for the current controller.
        
        On return, pdStatusLogRT contains the retention time when the status log entry was recorded.
        This time may not be the same as the retention time corresponding to the specified scan
        number but is the closest status log entry to the scan time.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Status Log"
        """
        pdStatusLogRT = c_double()
        pvarLabels = comtypes.automation.VARIANT()
        pvarValues = comtypes.automation.VARIANT()
        pnArraySize = c_long()
        error = self.source.GetStatusLogForScanNum(c_long(scanNumber), byref(pdStatusLogRT), pvarLabels, pvarValues, byref(pnArraySize) ) 
        if error : raise IOError("GetStatusLogForScanNum error :", error)
        # return pdStatusLogRT, dict(zip([label.rstrip(':') for label in pvarLabels.value],pvarValues.value))
        return pdStatusLogRT, dict(zip([label.rstrip(':') for label in pvarLabels.value],pvarValues.value))
        
    def GetStatusLogForPos(self): # TODO
        """This function returns the recorded status log entry labels and values for the current controller."""
        pass
        
    def GetStatusLogPlottableIndex(self): # TODO
        """This function returns the recorded status log entry labels and values for the current controller."""
        pass
        
    def GetNumErrorLog(self): # DONE
        """Gets the number of error log entries recorded for the current controller."""
        pnNumberOfErrorLogEntries = c_long()
        error = self.source.GetNumErrorLog(byref(pnNumberOfErrorLogEntries))
        if error : raise IOError("GetNumErrorLog error :", error)
        return pnNumberOfErrorLogEntries.value
        
    def GetErrorLogItem(self, nItemNumber): # DONE "View/Report/Error Log"
        """Returns the specified error log item information and the retention time when the error
        occurred. The value of nItemNumber must be within the range of one to the number of error
        log items recorded for the current controller. The number of error log items for the current
        controller may be obtained by calling GetNumErrorLog.
        
        NOTE : XCALIBUR INTERFACE "View/Report/Error Log"
        """
        pdRT = c_double() # A valid pointer to a variable of type double to receive the retention time when the error occurred. This variable must exist.
        pbstrErrorMessage = comtypes.automation.BSTR()
        error = self.source.GetErrorLogItem(c_long(nItemNumber), byref(pdRT), byref(pbstrErrorMessage) )
        if error : raise IOError ("GetErrorLogItem error :", error)
        return pbstrErrorMessage.value, pdRT.value
    ############################################### XCALIBUR INTERFACE END
        
    # DONE
    def GetChroData(self, start_time=None, 
                        stop_time=None, 
                        start_mz=None, 
                        stop_mz=None, 
                        filter="Full ms ", 
                        nChroType1 = 0, 
                        nChroOperator = 0, 
                        nChroType2 = 0, 
                        Delay = 0.0 , 
                        SmoothingType = 0, 
                        SmoothingValue = 0):
        # start_mz and stop_mz specified by Qual browser 
        """FA: Generates Total Ion Chromatogram (TIC) and eXtracted Ion Chromatogram (XIC) for given time range and mz range
        """
        if start_time == None or start_time < self.StartTime: start_time = self.StartTime
        if stop_time == None or stop_time > self.EndTime: stop_time = self.EndTime
        if start_mz == None: start_mz = self.LowMass
        if stop_mz == None: stop_mz = self.HighMass
        massRange1 = "{}-{}".format(start_mz, stop_mz) #LPCTSTR szMassRanges1, 
        massRange2 = ""                                     # LPCTSTR szMassRanges2, 
        # Delay = 0.0                                         # double dDelay, 
        StartTime = c_double(start_time)                    # double FAR* pdStartTime,
        EndTime = c_double(stop_time)                       # double FAR* pdEndTime, 
        # SmoothingType = 0                                   # long nSmoothingType, 
        # SmoothingValue = 0                                  # long nSmoothingValue, 
        # The nSmoothingType :
        #   0 None (no smoothing)
        #   1 Boxcar http://en.wikipedia.org/wiki/Boxcar_function
        #   2 Gaussian http://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm
        # The value of nSmoothingValue must be an odd number in the range of 3-15 if smoothing is desired.
        pvarChroData = comtypes.automation.VARIANT()
        flags = comtypes.automation.VARIANT() 
        pnArraySize = c_long()
        error = self.source.GetChroData(nChroType1,nChroOperator,nChroType2,filter,massRange1,massRange2,Delay,
            byref(StartTime),byref(EndTime),SmoothingType,SmoothingValue,pvarChroData,flags,byref(pnArraySize))
        if error : raise IOError("GetChroData error :", error)
        # scan2tic = dict( zip( [self.ScanNumFromRT(rt) for rt in pvarChroData.value[0]], pvarChroData.value[1] ) )
        scan2tic = None
        return pvarChroData.value, scan2tic

    def GetChros(self,nChros, start_time, stop_time):  # DONE
        """FA: same as GetChroData..."""
        StartTime = c_double(start_time)
        EndTime = c_double(stop_time)
        pvarChroParamsArray = comtypes.automation.VARIANT()
        pvarSizeArray = comtypes.automation.VARIANT()
        pvarChroDataArray = comtypes.automation.VARIANT()
        pvarPeakFlagsArray = comtypes.automation.VARIANT()
        error = self.source.GetChros(nChros, byref(StartTime), byref(EndTime),
                        pvarChroParamsArray, pvarSizeArray, pvarChroDataArray, pvarPeakFlagsArray )
        if error : raise IOError("GetChros error :", error)
        return pvarChroDataArray.value
        
    def GetChroByCompoundName(self):
        pass
        
    def GetUniqueCompoundNames(self):
        """This function returns the list of unique compound names for the raw file."""
        pass
    
    def GetCompoundNameFromScanNum(self, scanNumber):
        """This function returns a compound name as a string for the specified scan number."""
        pass
        

    ################## Home made function
    def getXIC(self, start_time, stop_time, start_mz=None, stop_mz=None, centroid=True, profile=False, method='sum'):
        import numpy as np
        if start_mz == None: start_mz = self.LowMass
        if stop_mz == None: stop_mz = self.HighMass
        
        centroidData = {}
        profileData = {}
        mixedData = {}

        # RT interval
        for sid in xrange(self.FirstSpectrumNumber,self.LastSpectrumNumber+1):
            rt = self.RTFromScanNum(sid)
            order = self.GetMSOrderForScanNum(sid)
            if rt >= start_time and rt <= stop_time and order == 1:
                if centroid:
                    # centroid
                    data_GetLabelData, _ = self.GetLabelData(sid)
                    centroidData[sid] = np.array(data_GetLabelData[:2])
                    data = centroidData
                if profile:
                    # profile
                    data_GetMassListFromScanNum,f = self.GetMassListFromScanNum(sid,centroidResult = False)
                    profileData[sid] = np.array(data_GetMassListFromScanNum)
                    data = profileData
                if centroid and profile:
                    mixedData[sid] = np.concatenate( (centroidData[sid],profileData[sid]) , axis=1)
                    data = mixedData
        # debug_here()
        # M/Z interval
        for sid in data.iterkeys():
            data[sid] = data[sid][:,(data[sid][0]>=start_mz) & (data[sid][0]<=stop_mz)]
            try:
                if method == 'max': # max of the intensites encountered in the M/Z interval
                    data[sid] = data[sid][1].max() 
                elif method == 'sum': # sum of the intensites encountered in the M/Z interval
                    data[sid] = data[sid][1].sum()
                elif method == 'mean': # mean of the intensites encountered in the M/Z interval
                    data[sid] = data[sid][1].mean()
            except ValueError: # data[sid] = zero-size array
                data[sid] = 0.0
            # sids,intensities = zip(*max_intensities.items())
            # data =  np.array([[ self.RTFromScanNum(sid) for sid in sids],intensities])
            # data = data[:,data[0,:].argsort()] # sort data in rt order
        return [ self.RTFromScanNum(sid) for sid in data.iterkeys() ] , data.values()
    ##################

        
    def _GetStatusLogForRT(self): # USELESS, cf. GetStatusLogForScanNum
        pass
    
    def _GetStatusLogLabelsForScanNum(self): # USELESS, cf. GetStatusLogForScanNum
        pass
        
    def _GetStatusLogLabelsForRT(self): # USELESS, cf. GetStatusLogForScanNum
        pass
        
    def _GetStatusLogValueForScanNum(self): # USELESS, cf. GetStatusLogForScanNum
        pass
        
    def _GetStatusLogValueForRT(self): # USELESS, cf. GetStatusLogForScanNum
        pass
        
    def _GetTrailerExtraForRT(self): # USELESS, cf. GetTrailerExtraForScanNum
        pass
        
    def _GetTrailerExtraLabelsForScanNum(self): # USELESS, cf. GetTrailerExtraForScanNum
        pass
        
    def _GetTrailerExtraLabelsForRT(self): # USELESS, cf. GetTrailerExtraForScanNum
        pass
        
    def _GetTrailerExtraValueForScanNum(self): # USELESS, cf. GetTrailerExtraForScanNum
        pass
        
    def _GetTrailerExtraValueForRT(self): # USELESS, cf. GetTrailerExtraForScanNum
        pass
        
    def _GetTuneDataValue(self): # USELESS, cf. GetTuneData
        pass
        
    def _GetTuneDataLabels(self): # USELESS, cf. GetTuneData
        pass
        
    def _GetPrevMassListRangeFromScanNum(self): # USELESS, cf. GetMassListRangeFromScanNum
        pass
        
    def _GetMassListRangeFromRT(self):  # USELESS, cf. GetMassListRangeFromScanNum
        pass

    def _GetNextMassListRangeFromScanNum(self): # USELESS, cf. GetMassListRangeFromScanNum
        pass

    def _GetMassListFromRT(self): # USELESS, cf. GetMassListFromScanNum
        pass
        
    def _GetNextMassListFromScanNum(self): # USELESS, cf. GetMassListFromScanNum
        pass
        
    def _GetPrevMassListFromScanNum(self): # USELESS, cf. GetMassListFromScanNum
        pass
        
    def _GetFilterForScanRT(self): # USELESS, cf. GetFilterForScanNum
        """Returns the scan filter for the closest matching scan that corresponds to dRT for the current
        controller. This function is only supported for MS device controllers. The value of dRT must
        be within the acquisition run time for the current controller. The acquisition run time for the
        current controller may be obtained by calling GetStartTime and GetEndTime."""
        pass
        
    def _GetSegmentedMassListFromRT(self): # USELESS, cf. GetSegmentedMassListFromScanNum
        pass
        
if __name__ == "__main__":
    rawfile = ThermoRawfile(os.path.abspath(sys.argv[1]))

    print( 'Version', rawfile.Version() )

    print( 'GetFileName', rawfile.GetFileName() )
    print( 'GetVersionNumber', rawfile.GetVersionNumber() )
    print( 'GetErrorMessage',  rawfile.GetErrorMessage() )
    print( 'GetNumSpectra', rawfile.GetNumSpectra() )
    print( 'GetNumTuneData', rawfile.GetNumTuneData() )
    print( 'GetMassResolution', rawfile.GetMassResolution() )
    print( 'GetNumTrailerExtra', rawfile.GetNumTrailerExtra() )
    print( 'GetLowMass', rawfile.GetLowMass() )
    print( 'GetHighMass', rawfile.GetHighMass() )
    print( 'GetStartTime', rawfile.GetStartTime() )
    print( 'GetEndTime', rawfile.GetEndTime() )
    print( 'GetFirstSpectrumNumber', rawfile.GetFirstSpectrumNumber() )
    print( 'GetLastSpectrumNumber', rawfile.GetLastSpectrumNumber() )
    print( 'GetInstrumentDescription', rawfile.GetInstrumentDescription() )
    print( 'GetAcquisitionDate', rawfile.GetAcquisitionDate() )
    print( 'GetInstName', rawfile.GetInstName() )
    print( 'GetInstModel', rawfile.GetInstModel() )
    print( 'GetInstSoftwareVersion', rawfile.GetInstSoftwareVersion() )
    print( 'GetInstHardwareVersion', rawfile.GetInstHardwareVersion() )
    print( 'ScanNumFromRT(0.1)', rawfile.ScanNumFromRT(0.1) )
    print( 'RTFromScanNum(9)', rawfile.RTFromScanNum(9) )
    print( 'GetFilterForScanNum', rawfile.GetFilterForScanNum(9) )

    print( 'GetMassListFromScanNum', rawfile.GetMassListFromScanNum(9) )
    print( 'GetMassListRangeFromScanNum', rawfile.GetMassListRangeFromScanNum(9) )

    scan = 788
    print( 'IsProfileScanForScanNum', rawfile.IsProfileScanForScanNum(scan) )
    print( 'IsCentroidScanForScanNum', rawfile.IsCentroidScanForScanNum(scan) )
    print( 'GetPrecursorMassForScanNum(scan)', rawfile.GetPrecursorMassForScanNum(scan, 0) )
    # print( 'GetPrecursorMassForScanNum(scan)', rawfile.GetPrecursorMassForScanNum(scan, 1) )
    # sys.exit()
    MassPrecisionEstimate = rawfile.GetMassPrecisionEstimate(scan)
    print( 'GetMassPrecisionEstimate(scan)', MassPrecisionEstimate )
    print( 'GetPrecursorInfoFromScanNum(scan)' )
    dIsolationMass , dMonoIsoMass = rawfile.GetPrecursorInfoFromScanNum(scan)
    print( 'dIsolationMass' , dIsolationMass )
    print( 'dMonoIsoMass' , dMonoIsoMass )
    
    for i in range(rawfile.GetNumberOfMassCalibratorsFromScanNum(scan)+1):
        print( 'GetMassCalibrationValueFromScanNum', i , rawfile.GetMassCalibrationValueFromScanNum(scan, i) )
    
    rawfile.ExtractInstMethodFromRaw(rawfile.filename + '.meth')
    
    print( 'GetLabelData', len(rawfile.GetLabelData(9)[0]) )
    
    print( 'GetScanHeaderInfoForScanNum' )
    pprint(rawfile.GetScanHeaderInfoForScanNum(scan))
    
    print( 'GetTrailerExtraForScanNum')
    pprint( rawfile.GetTrailerExtraForScanNum(scan))

    print( 'GetNumStatusLog', rawfile.GetNumStatusLog() )
    print( 'GetStatusLogForScanNum' )
    pprint( rawfile.GetStatusLogForScanNum(scan))
    
    print( 'GetNumErrorLog', rawfile.GetNumErrorLog() )
    for i in range(rawfile.GetNumErrorLog()):
        print( 'GetErrorLogItem', i , rawfile.GetErrorLogItem(i) )
    
    
    
    
    print( 'IsQExactive', rawfile.IsQExactive() ) # Not implemented in MSFileReader 3.0.29.0

    print( '\nGetTuneData' )
    print(( rawfile.GetTuneData(0) ) )
    
    print( rawfile.GetInstMethod(0) )
    print( 'GetErrorMessage',  rawfile.GetErrorMessage() )

    print( 'GetNumInstMethods', rawfile.GetNumInstMethods() )
    print( 'GetInstMethodNames', rawfile.GetInstMethodNames() )
    for i in range(rawfile.GetNumInstMethods()):
        print( '-------------------------------------------------------------------------------')
        print( rawfile.GetInstMethod(i) )
        print( '-------------------------------------------------------------------------------' )
    rawfile.Close()
