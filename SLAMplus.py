# -*- coding: utf-8 -*-
#   SLAM : a method for the automatic Stylization and LAbelling of speech Melody
#   Copyright (C) 2014  Julie BELIAO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
"""
#####################################################################
Automatic Stylizer.
#####################################################################

Takes a wavefile and a textgrid file as an input and compute the
styles of all the intervals of a desired tier with the SLAM algorithm.

PARAMETERS:

I/O:
---
* srcFile : path to the wave or PitchTier file to process
* inputTextgridFile  : path to the input TextGrid file
* outputTextgridFile : path to the output TextGrid file

tiers of interest:
------------------
* speakerTier : average register of each speaker is computed
                using this tier. For each different label in
                this tier, we assume a different speaker, for
                whom the average register is computed.
* targetTier  : The tier whose intervals will be stylized using
                SLAM


display & export:
-------
* displayExamples : True or False: whether or not to display examples
                   of stylized f0 segments
* displaySummary : True or False: whether or not to display a small
                   summary of the distribution of the stylizes
* exportFigures :  True or False: whether or not to export the result
                   tonal analysis in PDF file
* exportTag :      True or False: whether or not to export the tag
                   in TextGrid File
#####################################################################"""

timeStep = .001  #in seconds, step for swipe pitch analysis
voicedThreshold = 0.2  #for swipe
alpha = 1  # for register ranger estimation

#Tiers for the speaker and the target intervals, put your own tier names
#speakerTier= 'periode'
#targetTier = 'pivot'

speakerTier = 'IUs' # commentary.
targetTier = 'ICs'
tagTier = 'mot'

#display and exportation
examplesDisplayCount = 1  #number of example plots to do. Possibly 0
exportFigures = True
exportTag = True

#END OF PARAMETERS (don't touch below please)
#------------------------------------------------------

#imports
import sys, glob, os, re, time
os.chdir(sys.path[0])
from SLAM_utils import TextGrid, swipe, stylize, praatUtil
import numpy as np
import matplotlib.backends.backend_pdf as pdfLib
import matplotlib.pylab as pl
import SLAM_utils.TextGrid as tgLib
import SLAM_utils.progress as progLib

change = stylize.input_SLAM(
    """
Current parameters are:
  tier providing units of register estimation (support) : %s
  tier providing units to stylize (target)              : %s
  tier providing additional descriptive contents (tag)  : %s
  min. value of the width of tonal zone (ie. minDELTA)  : %d (semitones)
  reference frequency for saliency detection            : %d (ie. %s)
  Number of examples to display                         : %d
  Export result in PDF                                  : %d (1 for True; 0 for False)
  Export tag in TextGrid                                : %d (1 for True; 0 for False)
  ENTER = ok
  anything+ENTER = change

  """ %
    (speakerTier, targetTier, tagTier,
     stylize.minDELTA, stylize.freqRefSaliency, stylize.detMode2str(stylize.freqRefSaliency),
     examplesDisplayCount, exportFigures,exportTag))

print(change)

if len(change):
    new = stylize.input_SLAM('reference tier (empty = keep %s) : ' %
                             speakerTier)
    if len(new): speakerTier = new
    new = stylize.input_SLAM('target tier (empty = keep %s) : ' % targetTier)
    if len(new): targetTier = new
    new = stylize.input_SLAM('tag tier (empty = keep %s) : ' % tagTier)
    if len(new): tagTier = new

    new = stylize.input_SLAM('number of displays (empty = keep %d) : ' %
                             examplesDisplayCount)
    if len(new): examplesDisplayCount = int(new)

    new = stylize.input_SLAM('export figures in PDF file (empty = keep %d) : ' %
                exportFigures)
    if len(new): exportFigures = int(new)

    new = stylize.input_SLAM('export tag in TextGrid file (empty = keep %d) : ' %
                exportTag)
    if len(new): exportTag = int(new)

#all styles, for statistics
stylesGlo = []
stylesDynLoc = []
totalN = 0

#seperate input files into tgFiles and srcFiles
tmpFiles = glob.glob('./data/*.*')
tgFiles = []
srcFiles = []
hybirdFiles = []
while tmpFiles:
    filename = tmpFiles.pop(0)
    if re.search(r'\.TEXTGRID$', filename, re.IGNORECASE):
        # Praat TextGrid
        tgFiles.append(filename)
    elif re.search(r'\.(COLLECTION|OR)$', filename, re.IGNORECASE) :
        # hybrid files : Praat Collection / Analor File
        srcFiles.append(filename)
    else:
        srcFiles.append(filename)

t1 = time.time()
tgFiles = sorted(tgFiles)
while (tgFiles):
    #take a tg file from tgFiles and its related src file(s) from SrcFiles
    inputTextgridFile = tgFiles.pop(0)
    basename = stylize.get_basename(inputTextgridFile)

    extension = stylize.get_extension(inputTextgridFile)
    outputTextgridFile = './output/{}{}'.format(basename, extension)
    #outputPitchTierFile = './output/{}{}'.format(basename, ".PitchTier")
    outputFigureFile = './output/{}{}'.format(basename, ".pdf")
    srcFilesPaired = \
    [filename for filename in srcFiles \
        if stylize.get_basename(filename).lower() == basename.lower()]
    for filename in srcFilesPaired:
        srcFiles.remove(filename)

    #Create TextGrid object
    print('')
    print(('Handling %s....' % basename))
    print('Loading input TextGrid...')
    tg = TextGrid.TextGrid()
    tg.read(inputTextgridFile)
    tierNames = [t.name() for t in tg]

    while targetTier not in tierNames:
        print(
            '    TextGrid does not have a tier named %s for target. Available tiers are:'
            % targetTier)
        for t in tierNames:
            print('        %s' % t)
        targetTier = stylize.input_SLAM(
            'Type the tier name to use as target (+ENTER):')
    while speakerTier not in tierNames and speakerTier:
        print(
            '    TextGrid does not have a tier named %s for support. Available tiers are:'
            % speakerTier)
        for t in tierNames:
            print('        %s' % t)
        speakerTier = stylize.input_SLAM(
            'Type the tier name for support (or any categorizing variable):')
    while tagTier not in tierNames and tagTier:
        print(
            '    TextGrid does not have a tier named %s for tag. Available tiers are:'
            % tagTier)
        for t in tierNames:
            print('        %s' % t)
        tagTier = stylize.input_SLAM(
            'Type the tier name indicating tag Tier (or any categorizing variable):'
        )

    #create interval tier for output
    newTier = TextGrid.IntervalTier(name='%sStyleGlo' % targetTier,
                                    xmin=tg[targetTier].xmin(),
                                    xmax=tg[targetTier].xmax())
    newTierLoc = TextGrid.IntervalTier(name='%sStyleLoc' % targetTier,
                                       xmin=tg[targetTier].xmin(),
                                       xmax=tg[targetTier].xmax())
    #create a new tier called exportTag
    #when the binary flag exportTag is turned on
    if exportTag:
        newTierTag = TextGrid.IntervalTier(name='exportTag',
                                           xmin=tg[targetTier].xmin(),
                                           xmax=tg[targetTier].xmax())


    #Create swipe object from wave file or external PitchTier file
    inputPitch = None
    #try as PitchTier files (supported formats: short text and binary)
    if not inputPitch:
        for file in srcFilesPaired:
            try:
                inputPitch = stylize.readPitchtierPlus(file)
            except Exception as e:
                inputPitch = None
                print(e)
                continue
            print('Reading pitch from PitchTier file {}'.format(file))
            break
    # try as wave files
    if not inputPitch:
        for file in srcFilesPaired:
            if not praatUtil.isGoodMonoWav(file): continue
            try:
                inputPitch = swipe.Swipe(file,
                                         pMin=75,
                                         pMax=500,
                                         s=timeStep,
                                         t=voicedThreshold,
                                         mel=False)
            except:
                inputPitch = None
                continue
            print('Computing pitch on wave file {}'.format(file))
            break
    # unknown format
    if not inputPitch:
        print('Error: source files {} are not supported !'.format(srcFilesPaired))
        continue

    print('Computing average register for each speaker')
    """
    try:
        registers = stylize.averageRegisters(inputPitch, tg[speakerTier])
    except:
        continue
    """

    print('Stylizing each interval of the target tier')

    #computing at which iterations to give progress
    LEN = float(len(tg[targetTier]))
    totalN += LEN
    POSdisplay = set([int(float(i) / 100.0 * LEN) for i in range(0,100,10)])
    smooth_total = []
    time_total = []
    pl.rcParams["figure.figsize"] = [13, 7]
    fig = pl.figure()
    support = None
    haveImgInbuf = False
    if exportFigures:
        pdf = pdfLib.PdfPages(outputFigureFile)

    prog = progLib.Progress(len(tg[targetTier]))
    for pos, targetIntv in enumerate(tg[targetTier]):
        if pos in POSdisplay:
            print('Stylizing: {} contours'.format(prog.progressstring(pos)))

        supportIntvs = stylize.getSupportIntvs(targetIntv,
                                               supportTier=tg[speakerTier])
        try:
            tag = stylize.getTags(targetIntv, tg[tagTier])
        except:
            tag = None
        #compute style of current interval
        out = \
            stylize.stylizeObject(\
            targetIntv = targetIntv, supportIntvs = supportIntvs,\
            inputPitch = inputPitch, alpha=alpha)
        if out:
            (style_glo,style_loc,\
            targetTimes,deltaTargetPitch, deltaTargetPitchSmooth, \
            reference, reference_loc, rangeRegisterInSemitones, loccalDynamicRegister) = out
        else:
            # when stylization fails, fill output tiers with empty content
            # then skip visulization
            style_glo = ""
            style_loc = ""
            concatenatedTag = ""

            newInterval = TextGrid.Interval(targetIntv.xmin(), targetIntv.xmax(),
                                            style_glo)
            newTier.append(newInterval)
            newIntervalLoc = TextGrid.Interval(targetIntv.xmin(),
                                               targetIntv.xmax(), style_loc)
            newTierLoc.append(newIntervalLoc)
            if exportTag:
                newIntervalTag = TextGrid.Interval(targetIntv.xmin(),
                                           targetIntv.xmax(), concatenatedTag)
                newTierTag.append(newIntervalTag)

            continue

        # debug
        if len(style_glo) != 2 and len(style_glo) != 4 and len(style_glo) != 6:
            print((
                'Error: a global style code {} incorrect !'.format(style_glo)))
            exit()
            #continue
        if len(style_loc) != 2 and len(style_loc) != 4 and len(style_loc) != 6:
            print(
                ('Error: a local style code{} incorrect !'.format(style_loc)))
            exit()
            #continue

        #prepare exportation of smoothed
        if isinstance(deltaTargetPitchSmooth, (np.ndarray, list)):
            if len(deltaTargetPitchSmooth) == len(targetTimes):
                reference_semitones = stylize.hz2semitone(reference)
                smooth_hz = [
                    stylize.semitone2hz(delta + reference_semitones)
                    for delta in deltaTargetPitchSmooth
                ]
                smooth_total = np.concatenate((smooth_total, smooth_hz))
                time_total = np.concatenate((time_total, targetTimes))

        # give null stylization on empty segment
        if targetIntv.mark():
            stylesGlo += [style_glo]
            stylesDynLoc += [style_loc]
        else:
            style_glo = '';
            style_loc = '';

        #then add an interval with that style to the (new) style tier
        newInterval = TextGrid.Interval(targetIntv.xmin(), targetIntv.xmax(),
                                        style_glo)
        newTier.append(newInterval)
        newIntervalLoc = TextGrid.Interval(targetIntv.xmin(),
                                           targetIntv.xmax(), style_loc)
        newTierLoc.append(newIntervalLoc)

        if exportTag:
            # concatenate tags falling in the target interval and
            if targetIntv.mark():
                concatenatedTag = tag
            else:
                # give null tag for empty target
                concatenatedTag = ""

            # put the concatenated result in newIntervalTag
            newIntervalTag = TextGrid.Interval(targetIntv.xmin(),
                                           targetIntv.xmax(), concatenatedTag)
            newTierTag.append(newIntervalTag)

        #compute figure either for examples or for export in PDF file
        if support != None:
            supportPreviousXmin = support.time[0]
            support = stylize.intv2customPitchObj(supportIntvs, inputPitch)
            is_new_support = (support.time[0] != supportPreviousXmin)

            if exportFigures and is_new_support and haveImgInbuf:
                try:
                    pdf.savefig(fig)
                    if examplesDisplayCount:
                        pl.show()
                        examplesDisplayCount -= 1
                    fig.clf()
                    haveImgInbuf = False
                except:
                    # debug
                    print('Error: fail to save figures in PDF !')
                    #pl.show();
                    fig.clf()
                    haveImgInbuf = False
        else:
            supportPreviousXmin = None
            support = stylize.intv2customPitchObj(supportIntvs, inputPitch)
            is_new_support = True

        # draw figure
        try:
            fig = pl.gcf()
            fig = stylize.show_stylization(\
                original=deltaTargetPitch,\
                smooth=deltaTargetPitchSmooth,\
                style1=style_glo,\
                style2=style_loc,\
                targetIntv=targetIntv,\
                register=reference,\
                register_loc=loccalDynamicRegister,\
                support=support,\
                time_org=targetTimes,\
                figIn=fig, is_new_support=is_new_support,
                rangeRegisterInSemitones = rangeRegisterInSemitones, alpha=alpha,tag = tag,\
                supportName=speakerTier,targetName=targetTier,tagName=tagTier )
            haveImgInbuf = True

        except:
            pass

    if exportFigures and haveImgInbuf:
        pdf.savefig(fig)
        if examplesDisplayCount:
            pl.show()
            examplesDisplayCount -= 1
        fig.clf()
        haveImgInbuf = False

    print('Stylizing: {} contours'.format(prog.progressstring(len(tg[targetTier]))))
    #done, now writing tier into textgrid and saving textgrid
    print(('Saving computed styles in file %s' % outputTextgridFile))
    tg.append(newTier)
    tg.append(newTierLoc)
    if exportTag:
        tg.append(newTierTag)
    tg.write(outputTextgridFile)
    #print('Exporting smoothed pitchs in Binary PitchTierfile %s' %
    #      outputPitchTierFile)
    #praatUtil.writeBinPitchTier(outputPitchTierFile, time_total, smooth_total)
    print('Exporting figures in PDF file %s' % outputFigureFile)
    if exportFigures: pdf.close()
    pl.close()
    print('List of files remained to be analyzed: '.format(len(tgFiles)))
    for i, name in enumerate(tgFiles):
        print('{}: {}'.format(i, name))

#Now output statistics
#---------------------
labs = ['Stylization over Global Register',\
        'Stylization over Local Register']

for i, styles in enumerate([stylesGlo, stylesDynLoc]):
    print(('Type of Stylization: {}'.format(labs[i])))
    count = {}
    for unique_style in set(styles):
        if not len(unique_style): continue
        count[unique_style] = styles.count(unique_style)

    #valeurs triees par importance decroissante
    unsorted_values = np.array(list(count.values()))
    nbStylesRaw = len(unsorted_values)
    total = float(sum(unsorted_values))

    #remove styles that appear less than 0.5 percents of the time
    """
    for style in list(count.keys()):
        if count[style] / total < 0.005: del count[style]
    """

    unsorted_values = np.array(list(count.values()))
    stylesNames = list(count.keys())
    argsort = np.argsort(unsorted_values)[::-1]  # from most to less important
    sorted_values = unsorted_values[argsort]

    total = float(sum(unsorted_values))
    L = min(len(list(count.keys())), 20)
    print("""
------------------------------------------------------------------
SLAM analysis overall summary:
------------------------------------------------------------------
- %d intervals to stylize.
- %d intervals with a non empty contour (others are unvoiced)
- %d distinctive forms of contour appearing in total
------------------------------------------------------------------
- The form of contour along with their frequency are:"""%(
    totalN,\
    len(styles),\
    len(set(styles))))
    styleNames = sorted(count, key=count.get)
    styleNames.reverse()
    for styleName in styleNames:
        print(
            ('\t%s\t:\t:%0.1f%% (%d occurrences)' %
             (styleName, count[styleName] / total * 100.0, count[styleName])))
    print('''

x------------------------------------------x-----------------------------x
| explained proportion of the observations | number of forms of contours |
|         (percents)                       |                             |
x------------------------------------------x-----------------------------x''')
    cumulative_values = np.cumsum(sorted_values)
    cumulative_values = cumulative_values / float(cumulative_values[-1])
    for P in [70, 75, 80, 85, 90, 95, 99]:
        N = np.nonzero(cumulative_values > float(P) / 100.0)[0][0] + 1
        print(
            '|                %2.0f                        |         %2.0f          |'
            % (P, N))
    print('x------------------------------------------x---------------------x')

print('SLAM: done in {}'.format(stylize.get_duration(t1, time.time())))
