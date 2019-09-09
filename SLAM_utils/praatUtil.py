# -*- coding: utf-8 -*-
"""

@package praatUtil This module contains some utility functions to seamlessly
	incorporate Praat analysis functionality into Python

@copyright GNU Public License
@author written 2009-2014 by Christian Herbst (www.christian-herbst.org)
@author Partially supported by the SOMACCA advanced ERC grant, University of Vienna,
	Dept. of Cognitive Biology

@note
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.
@par
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
@par
You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>.

"""

import numpy, sys, struct

# try tp enable javaobj for analor file support
javaobj_installed = True
try:
    import javaobj
except Exception as e:
    javaobj_installed = False


def writeBinPitchTier(fileName, dataX, dataY):

    with open(fileName, "wb") as bin:

        # check data lengths
        if len(dataX) != len(dataY):
            raise IOError('dataX and dataY should have the same length !')

        # metadata & data format
        mdType = numpy.dtype([\
              ('header','S22'),
              ('xMin','>d'),\
              ('xMax','>d'),\
              ('nb','>i4')])

        numpy.array([\
              ("ooBinaryFile\tPitchTier",\
              min(dataX),\
              max(dataX),\
              len(dataX))],\
              dtype=mdType).tofile(bin)

        # write data as 2D-array
        dType = numpy.dtype([('x', '>d'), ('y', '>d')])
        dataXY = [(x, y) for x, y in zip(dataX, dataY)]
        Z = numpy.array(dataXY, dtype=dType)
        Z.tofile(bin)


def isGoodMonoWav(fileName):
    metadataType = numpy.dtype([\
          ('FileTypeBlocID','S4'),
          ('FileSize'      ,'i4'),\
          ('FileFormatID'  ,'S4'),\
          ('FormatBlocID'  ,'S4'),\
          ('BlocSize'      ,'i4'),\
          ('AudioFormat'   ,'i2'),\
          ('NbrCanaux'     ,'i2'),\
          ('Frequence'     ,'i4'),\
          ('BytePerSec'    ,'i4'),\
          ('BytePerBloc'   ,'i4'),\
          ('BitsPerSample' ,'i4'),\
          ('DataBlocID'    ,'S4'),\
          ('DataSize'      ,'i4')])

    with open(fileName, "rb") as bin:
        md = numpy.fromfile(bin, dtype=metadataType, count=1)[0]

    FileTypeBlocID = md['FileTypeBlocID'].astype(str)
    FileFormatID = md['FileFormatID'].astype(str)
    NbrCanaux = md['NbrCanaux'].astype(int)

    if NbrCanaux > 1:
        print(
            'Error: Swipe requires monochannel wav but {} contains {} channels !'
            .format(fileName, NbrCanaux))

    return (FileTypeBlocID == 'RIFF' and FileFormatID == 'WAVE'
            and NbrCanaux == 1)


def readPitchTier2(fileName):

    metadataType = numpy.dtype([\
         ('xMin'  ,'>d'),\
         ('xMax'  ,'>d'),\
         ('nb'    ,'>i4')])
    dataType = numpy.dtype([('x', '>d'), ('y', '>d')])

    with open(fileName, "rb") as bin:

        isAnalorFile = False
        marshaller = None
        if javaobj_installed:  # try as Analor file
            try:
                marshaller = javaobj.JavaObjectUnmarshaller(bin)
                if marshaller == None: raise IOError
            except IOError:
                marshaller = None
        if marshaller:
            while True:
                pobj = marshaller.readObject()
                if pobj == 'FIN' or \
                   pobj == '' :
                    break
                if pobj == 'F0':
                    xMin, xMax = marshaller.readObject()
                    deltaT = marshaller.readObject()
                    vect_x, vect_y = marshaller.readObject()
                    vect_x = numpy.array(vect_x)
                    vect_y = numpy.array(vect_y)
                    vect_y = 2.0**vect_y  # log2 to linear scale
                    isAnalorFile = True
        if not isAnalorFile:
            # return the cursor and try as Praat file
            bin.seek(0, 0)
            header = bin.read(12)
            if header == b'ooBinaryFile':
                # binray collection file or pitchtier file
                sys.stdout.write('Praat Binary ')
                sys.stdout.flush()
                sub_header = bin.read(ord(bin.read(1)))
                if sub_header == b'Collection':
                    sys.stdout.write('Collection ')
                    sys.stdout.flush()
                    jump2(bin, keyword=b'\x09PitchTier')
                elif sub_header == b'PitchTier':
                    sys.stdout.write('PitchTier ')
                    sys.stdout.flush()
                else:
                    raise IOError('Type non-supported !')

                # metadata
                md = numpy.fromfile(bin, dtype=metadataType, count=1)[0]
                nb = md['nb'].astype(int)

                # read data as 2D-array
                data = numpy.fromfile(bin, dtype=dataType, count=nb)
                # check file end
                if sub_header == b'PitchTier' and len(bin.read()) > 0:
                    raise EOFError
                vect_x = data['x']
                vect_y = data['y']
            else:
                # read pitchtier object from short text file
                vect_x, vect_y = readPitchTier(fileName)

    return (vect_x, vect_y)


def jump2(ifile, keyword):
    binstr = b''
    while ifile:
        binstr += ifile.read(1)
        if len(binstr) > len(keyword):
            binstr = binstr[1:]
        if binstr == keyword:
            break
    lg = struct.unpack('>h', ifile.read(2))[0]
    if lg == -1:
        lg = lg.astype('>H')
    objname = ifile.read(lg).decode('ascii')  # skip embeded oo name


def readPitchTier(fileName):
    """
	reads Praat PitchTier data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and the
		corresponding F0 (inaccurately called "pitch" in Praat) data
	"""
    dataX, dataY, metaData = readPraatShortTextFile(fileName, 'PitchTier')
    return dataX, dataY


def readIntensityTier(fileName):
    """
	reads Praat IntensityTier data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and data
	"""
    dataX, dataY, metaData = readPraatShortTextFile(fileName, 'Intensity')
    return dataX, dataY


def readPraatShortTextFile(fileName, obj):
    """
	this function reads a Praat pitch tier file (saved as a 'short text file')
	@param fileName
	@param obj the file type. Currently we support these file types (as defined
		internally by Praat):
			- Harmonicity 2
			- PitchTier
			- Intensity
			- SpectrumTier
			- Spectrum 2
			- Cepstrum 1
	@return a two-dimensional array of floats, the first row
		(index = 0) representing the time offsets of data values, and the
		second row representing the detected fundamental frequency values
	"""
    file = open(fileName, "r")
    cnt = 0
    numDataPoints = 0
    offset = 0
    dataX = []
    dataY = []
    dataIdx = 0
    timeStep = 0
    timeOffset = 0

    arrFileTypes = [
     'Harmonicity 2', 'PitchTier', 'Intensity', 'SpectrumTier', \
      'Spectrum 2', 'Cepstrum 1'
    ]

    if not obj in arrFileTypes:
        raise Exception('readPraatShortTextFile - file type must be: ' +
                        ', '.join(arrFileTypes))
    metaData = []
    for line in file:
        line = line.strip()
        cnt += 1
        #print cnt, line # debug information
        if cnt > 6:
            if obj == 'Harmonicity 2' or obj == 'Intensity 2':
                if cnt > 13:
                    val = float(line)
                    if val > -100:
                        dataY.append(val)
                    else:
                        dataY.append(None)
                    dataX.append(timeOffset + float(dataIdx) * timeStep)
                    dataIdx += 1
                else:
                    if cnt == 7:
                        timeStep = float(line)
                    if cnt == 8:
                        timeOffset = float(line)
            else:
                # read data here
                if cnt % 2 == 0:
                    dataY.append(float(line))
                    dataIdx += 1
                else:
                    dataX.append(float(line))
        else:
            if cnt > 3:
                metaData.append(line)
            # error checking and loop initialization
            if cnt == 1:
                if line != "File type = \"ooTextFile\"":
                    raise Exception ("file " + fileName \
                     + " is not a Praat pitch" + " tier file")
            if cnt == 2:
                err = False
                #print line
                if obj == 'Harmonicity':
                    if line != "Object class = \"Harmonicity\"" \
                      and line != "Object class = \"Harmonicity 2\"":
                        err = True
                elif obj == 'Intensity':
                    if line != "Object class = \"IntensityTier\"" \
                      and line != "Object class = \"Intensity 2\"":
                        err = True
                else:
                    if line != "Object class = \"" + obj + "\"":
                        err = True
                if err == True:
                    raise Exception("file " + fileName + " is not a Praat " +
                                    obj + " file")
            if cnt == 6:
                if line[0:15] == 'points: size = ':
                    numDataPoints = int(line.split('=')[1].strip())
                    raise Exception (\
                     "only the 'short text file' type is supported. " \
                     + " Save your Praat " + obj \
                     + " with 'Write to short text file.")
                else:
                    numDataPoints = int(line)
    return (numpy.array(dataX), numpy.array(dataY), metaData)
