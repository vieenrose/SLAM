# -*- coding: utf-8 -*-
# classes for Praat TextGrid data structures, and HTK .mlf files
# Kyle Gorman <kgorman@ling.upenn.edu>
# Modifications : Antoine Liutkus <antoine@liutkus.net> & Julie Beliao <julie@beliao.fr>

# TODO: documentation

import codecs
import chardet
import re
import struct

# try tp enable javaobj for analor file support
javaobj_installed = True
try:
    import javaobj
except Exception as e:
    javaobj_installed = False

def auto_decode(input):
    if input:
        if isinstance(input,(str,unicode)):
            encoding = chardet.detect(input)['encoding']
            return input.decode(encoding)
        elif isinstance(input,list):
            encoding = chardet.detect(''.join(input))['encoding']
            ret = []
            for x in input:
                if x: x = x.decode(encoding)
                ret.append(x)
            return ret
        else:
            return input
    else:
        return input

def detectEncoding(f):
    """
    This helper method returns the file encoding corresponding to path f.
    This handles UTF-8, which is itself an ASCII extension, so also ASCII.
    """
    encoding = 'ascii'
    try:
        with codecs.open(f, 'r', encoding='utf-16') as source:
            source.readline()  # Read one line to ensure correct encoding
    except UnicodeError:
        try:
            with codecs.open(
                    f, 'r', encoding='utf-8-sig'
            ) as source:  #revised utf-8 to utf-8-sig for utf-8 with byte order mark (BOM)
                source.readline()  # Read one line to ensure correct encoding
        except UnicodeError:
            with codecs.open(f, 'r', encoding='ascii') as source:
                source.readline()  # Read one line to ensure correct encoding
        else:
            encoding = 'utf-8-sig'  #revised utf-8 to utf-8-sig for utf-8 with byte order mark (BOM)
    else:
        encoding = 'utf-16'

    return encoding


class mlf:
    """" read in a HTK .mlf file. iterating over it gives you a list of
        TextGrids """

    def __init__(self, file):
        self.__items = []
        self.__n = 0
        text = open(file, 'r')
        text.readline()  # get rid of header
        while 1:  # loop over text
            name = text.readline()[1:-1]
            if name:
                grid = TextGrid()
                phon = IntervalTier('phones')
                word = IntervalTier('words')
                wmrk = ''
                wsrt = 0.
                wend = 0.
                while 1:  # loop over the lines in each grid
                    line = text.readline().rstrip().split()
                    if len(line) == 4:  # word on this baby
                        pmin = float(line[0]) / 10e6
                        pmax = float(line[1]) / 10e6
                        phon.append(Interval(pmin, pmax, line[2]))
                        if wmrk:
                            word.append(Interval(wsrt, wend, wmrk))
                        wmrk = line[3]
                        wsrt = pmin
                        wend = pmax
                    elif len(line) == 3:  # just phone
                        pmin = float(line[0]) / 10e6
                        pmax = float(line[1]) / 10e6
                        phon.append(Interval(pmin, pmax, line[2]))
                        wend = pmax
                    else:  # it's a period
                        word.append(Interval(wsrt, wend, wmrk))
                        self.__items.append(grid)
                        break
                grid.append(phon)
                grid.append(word)
                self.__n += 1
            else:
                text.close()
                break

    def __iter__(self):
        return iter(self.__items)

    def __len__(self):
        return self.__n

    def __str__(self):
        return u'<MLF instance with %d TextGrids>' % self.__n


class TextGrid():
    """ represents Praat TextGrids as list of different types of tiers """

    def __str__(self):
        return u'<TextGrid with %d tiers>' % self.__n

    def __iter__(self):
        return iter(self.__tiers)

    def __len__(self):
        return self.__n

    def __getitem__(self, i):
        """ return the (i-1)th tier """
        if isinstance(i, int):
            return self.__tiers[i]
        elif isinstance(i, str) or isinstance(i, unicode):
            for tier in self.__tiers:
                if tier.name() == i:
                    return tier
            return None

    def xmin(self):
        return self.__xmin

    def xmax(self):
        return self.__xmax

    def span(self, xmin=True, xmax=True):
        res = ()
        if xmin == True:
            res = res + (self.__xmin, )
        if xmax == True:
            res = res + (self.__xmax, )
        return res

    def append(self, tier):
        self.__tiers.append(tier)
        if self.__xmax is not None:
            self.__xmax = max(self.__xmax, tier.xmax())
        else:
            self.__xmax = tier.xmax()
        if self.__xmin is not None:
            self.__xmin = min(self.__xmin, tier.xmin())
        else:
            self.__xmin = tier.xmin()
        self.__n += 1

    def extractTextGridFromAnalorFile(self, file):

        SuccessOrNot = False
        marshaller = None
        with open(file, 'rb') as ifile:
            try:
                marshaller = javaobj.JavaObjectUnmarshaller(ifile)
                if marshaller == None: raise IOError
            except IOError:
                ifile.seek(0, 0)
                return SuccessOrNot

            while True:

                # get one object
                pobj = marshaller.readObject()
                if pobj == 'FIN' or \
                                  pobj == '' :
                    break
                if pobj == 'F0':
                    self.xmin, self.xmax = marshaller.readObject()

                # check if is at the tiers' header
                if pobj == 'TIRES':

                    # get tier number
                    tier_num = marshaller.readObject()
                    tier_num = struct.unpack('>i', tier_num)[0]

                    while tier_num:
                        # get the metadata of tier
                        tlims = marshaller.readObject()
                        typ = auto_decode(marshaller.readObject())
                        nom = auto_decode(marshaller.readObject())
                        mots = auto_decode(marshaller.readObject())
                        bornes = marshaller.readObject()
                        nomGuide = auto_decode(marshaller.readObject())

                        # translation between 2 type naming
                        # between Analor and Praat version
                        if typ == 'INTERVALLE':
                            tier_type = 'IntervalTier'
                        elif typ == 'POINT':
                            tier_type = 'TextTier'
                        else:
                            raise Exception('Tiertype does not exist.')

                        # form a tier
                        if tier_type == u'IntervalTier':
                            tier = IntervalTier(nom,  tlims[0],
                                             tlims[-1])  # redundant FIXME
                        else:
                            tier = PointTier(nom,  tlims[0],  tlims[-1]) # redundant FIXME


                        if tier_type == 'IntervalTier':
                            for x1, x2, text in zip(bornes, bornes[1:], mots):
                                tier.append(Interval(x1, x2, text))
                        elif tier_type == 'TextTier':
                            for x1, text in zip(bornes, mots):
                                tier.append(Point(x1, x2, text))
                        else:
                            raise Exception('Tiertype does not exist.')

                        # uncount the number of tiers remain to process
                        if tier_num > 0:
                            tier_num -= 1

                        if not SuccessOrNot: SuccessOrNot = True
                        self.append(tier)

        return SuccessOrNot

    def jump2(self, ifile, keyword):
        binstr = b''
        keyword_found = False
        while ifile:
            binstr += ifile.read(1)
            if len(binstr) > len(keyword):
                binstr = binstr[1:]
            if binstr == keyword:
                keyword_found = True
                break
        lg = struct.unpack('>h', ifile.read(2))[0]
        if lg == -1:
            lg = lg.astype('>H')
        objname = ifile.read(lg).decode('ascii')  # skip embeded oo name

        return keyword_found

    def __init__(self, name=None):
        self.__tiers = []
        self.__n = 0
        self.__xmin = None
        self.__xmax = None
        self.__name = name  # this is just for the MLF case
        self.__encoding = 'utf-8'  #default

    def read(self, file):
        # try as an Analor file (.or) if the support is enabled
        isAnalorFile = False
        if javaobj_installed:
            isAnalorFile = self.extractTextGridFromAnalorFile(file)

        if not isAnalorFile:
            # try as a binary file
            with open(file, 'rb') as ifile:
                # try as a Praat TextGrid / Collection binrary file
                if ifile.read(12) == b'ooBinaryFile':

                    def bin2str(ifile):
                        textlen = struct.unpack('>h', ifile.read(2))[0]
                        # Single byte characters
                        if textlen >= 0:
                            return ifile.read(textlen).decode('ascii')
                        # Multi byte characters have initial len -1 and then \xff bytes
                        elif textlen == -1:
                            textlen = struct.unpack('>h', ifile.read(2))[0]
                            data = ifile.read(textlen * 2)
                            # Hack to go from number to unicode in python3 and python2
                            fun = unichr if 'unichr' in __builtins__ else chr
                            charlist = (data[i:i + 2]
                                        for i in range(0, len(data), 2))
                            return u''.join(
                                fun(struct.unpack('>h', i)[0])
                                for i in charlist)

                    type_obj = ifile.read(ord(ifile.read(1)))
                    if type_obj == b'Collection':  # skip oo type
                        if not self.jump2(ifile, b'\x08TextGrid'):
                            raise Exception('TextGrid object not found !')
                    elif type_obj != b'TextGrid':
                        raise Exception(
                            'Praat binary file have a unsupported format !')

                    self.__xmin = struct.unpack('>d', ifile.read(8))[0]
                    self.__xmax = struct.unpack('>d', ifile.read(8))[0]
                    ifile.read(1)  # skip <exists>
                    m = struct.unpack('>i', ifile.read(4))[0]
                    for i in range(m):  # loop over grids
                        tier_type = ifile.read(ord(
                            ifile.read(1))).decode('ascii')
                        name = bin2str(ifile)
                        imin = struct.unpack('>d', ifile.read(8))[0]
                        imax = struct.unpack('>d', ifile.read(8))[0]
                        n = struct.unpack('>i', ifile.read(4))[0]
                        if tier_type == u'IntervalTier':
                            tier = IntervalTier(name, imin,
                                            imax)  # redundant FIXME
                        else:
                            tier = PointTier(name, imin, imax) # redundant FIXME
                        try:
                            for j in range(n):
                                jmin = struct.unpack('>d', ifile.read(8))[0]
                                if tier_type == 'IntervalTier':
                                    jmax = struct.unpack('>d',
                                                         ifile.read(8))[0]
                                jmrk = bin2str(ifile)
                                if tier_type == 'IntervalTier':
                                    tier.append(Interval(jmin, jmax, jmrk))
                                elif tier_type == 'TextTier':
                                    tier.append(Point(jmin, jmrk))
                                else:
                                    raise Exception('Tiertype does not exist.')
                        except IndexError:
                            pass
                        self.append(tier)

                # read a TextGrid file in long/ short text format
                else:

                    codec = detectEncoding(file)
                    with codecs.open(file, 'r', encoding=codec) as ifile:

                        def nn(ifile, pat):
                            line = next(ifile)
                            return pat.search(line).group(1)

                        regfloat = re.compile('([\d.]+)\s*$', flags=re.UNICODE)
                        regint = re.compile('([\d]+)\s*$', flags=re.UNICODE)
                        regstr = re.compile('"(.*)"\s*$', flags=re.UNICODE)
                        # Skip the Headers and empty line
                        next(ifile), next(ifile), next(ifile)

                        self.__xmin = float(nn(ifile, regfloat))
                        self.__xmax = float(nn(ifile, regfloat))

                        # Skip <exists>
                        line = next(ifile)
                        short = line.strip() == b'<exists>'
                        m = int(nn(ifile, regint))
                        not short and next(ifile)
                        for i in range(m):
                            not short and next(
                                ifile)  # skip item[]: and item[\d]:
                            tier_type = nn(ifile, regstr)
                            name = nn(ifile, regstr)
                            imin = float(nn(ifile, regfloat))
                            imax = float(nn(ifile, regfloat))
                            if tier_type == u'IntervalTier':
                                tier = IntervalTier(name, imin,
                                                imax)  # redundant FIXME
                            else:
                                tier = PointTier(name, imin, imax) # redundant FIXME

                            try:
                                for j in range(int(nn(ifile, regint))):
                                    not short and next(
                                        ifile)  # skip intervals [\d]
                                    x1 = float(nn(ifile, regfloat))
                                    if tier_type == u'IntervalTier':
                                        x2 = float(nn(ifile, regfloat))
                                        t = nn(ifile, regstr)
                                        tier.append(Interval(x1, x2, t))

                                    else:
                                        t = nn(ifile, regstr)
                                        tier.append(Point(x1, t))

                            except IndexError:
                                pass

                            self.append(tier)

    def write(self, text):
        import sys
        """ write it into a text file that Praat can read """
        print(self.__encoding)
        text = codecs.open(text, 'w', 'utf-8')

        text.write('File type = "ooTextFile"\n')
        text.write('Object class = "TextGrid"\n\n')
        text.write('xmin = %f\n' % self.__xmin)
        text.write('xmax = %f\n' % self.__xmax)
        text.write('tiers? <exists>\n')
        text.write('size = %d\n' % self.__n)
        text.write('item []:\n')

        for (tier, n) in zip(self.__tiers, range(1, self.__n + 1)):
            text.write('\titem [%d]:\n' % n)
            if tier.__class__ == IntervalTier:
                text.write('\t\tclass = "IntervalTier"\n')
                text.write('\t\tname = "%s"\n' % tier.name())
                text.write('\t\txmin = %f\n' % tier.xmin())
                text.write('\t\txmax = %f\n' % tier.xmax())
                text.write('\t\tintervals: size = %d\n' % len(tier))
                for (interval, o) in zip(tier, range(1, len(tier) + 1)):
                    text.write('\t\t\tintervals [%d]:\n' % o)
                    text.write('\t\t\t\txmin = %f\n' % interval.xmin())
                    text.write('\t\t\t\txmax = %f\n' % interval.xmax())
                    #text.write('\t\t\t\ttext = "%s"\n' % interval.mark())
                    text.write('\t\t\t\ttext = "%s"\n' % interval.mark().replace('"',"'")) # replace double quote by single quote to avoid format error
            else:  # PointTier
                text.write('\t\tclass = "TextTier"\n')
                text.write('\t\tname = "%s"\n' % tier.name())
                text.write('\t\txmin = %f\n' % tier.xmin())
                text.write('\t\txmax = %f\n' % tier.xmax())
                text.write('\t\tpoints: size = %d\n' % len(tier))
                for (point, o) in zip(tier, range(1, len(tier) + 1)):
                    text.write('\t\t\tpoints [%d]:\n' % o)
                    text.write('\t\t\t\ttime = %f\n' % point.time())
                    text.write('\t\t\t\tmark = "%s"\n' % point.mark())
        text.close()


class IntervalTier:
    """ represents IntervalTier as a list plus some features: min/max time,
        size, and tier name """

    def __init__(self, name=None, xmin=None, xmax=None):
        self.__n = 0
        self.__name = name
        self.__xmin = xmin
        self.__xmax = xmax
        self.__intervals = []

    def __str__(self):
        return u'<IntervalTier "%s" with %d points>' % (self.__name, self.__n)

    def __iter__(self):
        return iter(self.__intervals)

    def __len__(self):
        return self.__n

    def __getitem__(self, i):
        """ return the (i-1)th interval """
        return self.__intervals[i]

    def xmin(self):
        return self.__xmin

    def xmax(self):
        return self.__xmax

    def span(self, xmin=True, xmax=True):
        res = ()
        if xmin: res = res + (self.__xmin, )
        if xmax: res = res + (self.__xmax, )
        return res

    def name(self):
        return self.__name

    def setname(self, name):
        self.__name = name

    def closest(self, positions, end=False):
        def argmin(distances, pos):
            #featuring ugly argmin, but I don't want to import numpy for this
            minimum = 100000
            res = 100000
            for i, d in enumerate(distances):
                if d < minimum:
                    res = i
                    minimum = d
            return res

        try:
            result = []
            for pos in positions:
                if end:
                    distances = [abs(pos - i.xmax()) for i in self.__intervals]
                else:
                    distances = [abs(pos - i.xmin()) for i in self.__intervals]
                result.append(argmin(distances, pos))
            return result
        except TypeError:
            return argmin(distances, positions)

    def append(self, interval):
        self.__intervals.append(interval)
        if self.__xmax is not None:
            self.__xmax = max(self.__xmax, interval.xmax())
        else:
            self.__xmax = interval.xmax()
        if self.__xmin is not None:
            self.__xmin = min(self.__xmin, interval.xmin())
        else:
            self.__xmin = interval.xmin()
        self.__n += 1

    def read(self, file):
        text = open(file, 'r')
        text.readline()  # header junk
        text.readline()
        text.readline()
        self.__xmin = float(text.readline().rstrip().split()[2])
        self.__xmax = float(text.readline().rstrip().split()[2])
        self.__n = int(text.readline().rstrip().split()[3])
        for i in range(self.__n):
            text.readline().rstrip()  # header
            imin = float(text.readline().rstrip().split()[2])
            imax = float(text.readline().rstrip().split()[2])
            imrk = text.readline().rstrip().split()[2].replace('"', '')  # txt
            self.__intervals.append(Interval(imin, imax, imrk))
        text.close()

    def write(self, file):
        text = open(file, 'w')
        text.write('File type = "ooTextFile"\n')
        text.write('Object class = "IntervalTier"\n\n')
        text.write('xmin = %f\n' % self.__xmin)
        text.write('xmax = %f\n' % self.__xmax)
        text.write('intervals: size = %d\n' % self.__n)
        for (interval, n) in zip(self.__intervals, range(1, self.__n + 1)):
            text.write('intervals [%d]:\n' % n)
            text.write('\txmin = %f\n' % interval.xmin())
            text.write('\txmax = %f\n' % interval.xmax())
            text.write('\ttext = "%s"\n' % interval.mark())
        text.close()


class PointTier:
    """ represents PointTier (also called TextTier for some reason) as a list
        plus some features: min/max time, size, and tier name """

    def __init__(self, name=None, xmin=None, xmax=None):
        self.__n = 0
        self.__name = name
        self.__xmin = xmin
        self.__xmax = xmax
        self.__points = []

    def __str__(self):
        return u'<PointTier "%s" with %d points>' % (self.__name, self.__n)

    def __iter__(self):
        return iter(self.__points)

    def __len__(self):
        return self.__n

    def __getitem__(self, i):
        """ return the (i-1)th tier """
        return self.__points[i]

    def name(self):
        return self.__name

    def xmin(self):
        return self.__xmin

    def xmax(self):
        return self.__xmax

    def span(self, xmin=True, xmax=True):
        res = ()
        if xmin: res = res + (self.__xmin, )
        if xmax: res = res + (self.__xmax, )
        return res

    def append(self, point):
        self.__points.append(point)
        self.__xmax = point.time()
        self.__n += 1

    def read(self, file):
        text = open(file, 'r')
        text.readline()  # header junk
        text.readline()
        text.readline()
        self.__xmin = float(text.readline().rstrip().split()[2])
        self.__xmax = float(text.readline().rstrip().split()[2])
        self.__n = int(text.readline().rstrip().split()[3])
        for i in range(self.__n):
            text.readline().rstrip()  # header
            itim = float(text.readline().rstrip().split()[2])
            imrk = text.readline().rstrip().split()[2].replace('"', '')  # txt
            self.__points.append(Point(imrk, itim))
        text.close()

    def write(self, file):
        text = open(file, 'w')
        text.write('File type = "ooTextFile"\n')
        text.write('Object class = "TextTier"\n\n')
        text.write('xmin = %f\n' % self.__xmin)
        text.write('xmax = %f\n' % self.__xmax)
        text.write('points: size = %d\n' % self.__n)
        for (point, n) in zip(self.__points, range(1, self.__n + 1)):
            text.write('points [%d]:\n' % n)
            text.write('\ttime = %f\n' % point.time())
            text.write('\tmark = "%s"\n' % point.mark())
        text.close()


class Interval:
    """ represent an Interval """

    def __init__(self, xmin, xmax, mark):
        self.__xmin = xmin
        self.__xmax = xmax
        self.__mark = mark
        self.uid = ''

    def __str__(self):
        return u'<Interval "%s" %f:%f>' % (self.__mark, self.__xmin,
                                          self.__xmax)

    def xmin(self):
        return self.__xmin

    def xmax(self):
        return self.__xmax

    def span(self, xmin=True, xmax=True):
        res = ()
        if xmin: res = res + (self.__xmin, )
        if xmax: res = res + (self.__xmax, )
        return res

    def duration(self):
        return self.__xmax - self.__xmin

    def mark(self):
        return self.__mark

    def tostring(self):
        return self.__mark


class Point:
    """ represent a Point """

    def __init__(self, time, mark):
        self.__time = time
        self.__mark = mark

    def __str__(self):
        return u'<Point "%s" at %f>' % (self.__mark, self.__time)

    def time(self):
        return self.__time

    def mark(self):
        return self.__mark

    def xmin(self):
        return self.__time

    def xmax(self):
        return self.__time


def getUniqueIntervals(intervals):
    #keeps unique intervals in the list. The decision is made using the
    #xmin and xmax properties of the intervals. Both are differents in
    #returned list
    result = []
    cles = []
    for interval in intervals:
        cle = hash((interval.xmin(), interval.xmax()))
        if cle not in cles:
            result.append(interval)
            cles.append(cle)
    return result


def getMatchingIntervals(intervals, tier, strict=True,
                         just_intersection=False):
    if not len(intervals): return []
    eps = 1E-5
    #aggregating intervals into time segments
    startSlices = []
    stopSlices = []
    for interval in sorted(intervals, key=lambda i: i.xmin()):
        start = interval.xmin()
        stop = interval.xmax()
        startMatch = [
            pos for pos, x in enumerate(stopSlices) if abs(start - x) < eps
        ]
        stopMatch = [
            pos for pos, x in enumerate(startSlices) if abs(stop - x) < eps
        ]
        if len(startMatch) or len(stopMatch):
            for match in startMatch:
                stopSlices[match] = stop
            for match in stopMatch:
                startSlices[match] = start
            continue
        startSlices.append(start)
        stopSlices.append(stop)
    #now finding intervals in tier which are contained by at least one of the slices,
    #either strictly or partly
    matching = []
    for interval in tier:
        start = interval.xmin()
        stop = interval.xmax()
        found = False
        for (startslice, stopslice) in zip(startSlices, stopSlices):
            if strict:
                if ((start >= startslice) and (stop <= stopslice)):
                    found = True
            else:
                if just_intersection == False:
                    if (((start <= stopslice) and (stop >= stopslice)) or
                        ((start <= startslice) and (stop >= startslice))):
                        found = True
                else:
                    if (min(stopslice, stop) - max(startslice, start) > 0):
                        found = True
        if found:
            matching.append(interval)
    matching.sort(key=lambda inter: inter.xmax())
    return matching
