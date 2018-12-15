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
#####################################################################"""


timeStep = .001 #in seconds, step for swipe pitch analysis
voicedThreshold = 0.2 #for swipe
alpha = 1 # for register ranger estimation

#Tiers for the speaker and the target intervals, put your own tier names
#speakerTier= 'periode'
#targetTier = 'pivot'

speakerTier= 'periode'
targetTier = 'Macro'
tagTier= 'pivot'

#display and exportation
examplesDisplayCount = 1 #number of example plots to do. Possibly 0
exportFigures = True


#END OF PARAMETERS (don't touch below please)
#------------------------------------------------------

#imports
from SLAM_utils import TextGrid, swipe, stylize, praatUtil
import sys, glob, os, re,time
import numpy as np
import matplotlib.backends.backend_pdf as pdfLib
import matplotlib.pylab as pl
import SLAM_utils.TextGrid as tgLib

change = stylize.input_SLAM("""
Current parameters are:
  tier to use for categorizing registers : %s
  tier to stylize                        : %s
  Number of examples to display          : %d
  Export result in PDF                   : %d
  ENTER = ok
  anything+ENTER = change

  """%(speakerTier, targetTier,examplesDisplayCount, exportFigures))

print(change)

if len(change):
    new = stylize.input_SLAM('reference tier (empty = keep %s) : '%speakerTier)
    if len(new):speakerTier=new
    new = stylize.input_SLAM('target tier (empty = keep %s) : '%targetTier)
    if len(new):targetTier=new
    new = stylize.input_SLAM('number of displays (empty = keep %d) : '%examplesDisplayCount)
    if len(new):examplesDisplayCount=int(new)
    new = input('export figures in PDF file (empty = keep %d) : '%exportFigures)
    if len(new):exportFigures=int(new)

#all styles, for statistics
stylesGlo = []
stylesDynLoc = []
totalN=0

#seperate input files into tgFiles and srcFiles
tmpFiles = glob.glob('./data/*.*')
tgFiles = []
srcFiles = []
while tmpFiles:
    filename = tmpFiles.pop(0)
    if re.search(r'\.TEXTGRID$', filename, re.IGNORECASE):
        tgFiles.append(filename)
    else:
        srcFiles.append(filename)


t1 = time.time()
while tgFiles:
    #take a tg file from tgFiles and its related src file(s) from SrcFiles
    inputTextgridFile = tgFiles.pop(0)
    basename = stylize.get_basename(inputTextgridFile)
    extension = stylize.get_extension(inputTextgridFile)
    outputTextgridFile = './output/{}{}'.format(basename, extension)
    outputPitchTierFile = './output/{}{}'.format(basename, ".PitchTier")
    outputFigureFile = './output/{}{}'.format(basename, ".pdf")
    srcFile = \
    [filename for filename in srcFiles \
        if stylize.get_basename(filename).lower() == basename.lower()]
    for filename in srcFile: srcFiles.remove(filename)

    #Create TextGrid object
    print('')
    print(('Handling %s....'%basename))
    print('Loading input TextGrid...')
    tg = TextGrid.TextGrid()
    tg.read(inputTextgridFile)
    tierNames = [t.name() for t in tg]

    while targetTier not in tierNames:
        print('    TextGrid does not have a tier named %s for target. Available tiers are:'%targetTier)
        for t in tierNames: print('        %s'%t)
        targetTier=stylize.input_SLAM('Type the tier name to use as target (+ENTER):')
    while speakerTier not in tierNames and speakerTier:
        print('    TextGrid does not have a tier named %s for speaker/support Tier. Available tiers are:'%speakerTier)
        for t in tierNames: print('        %s'%t)
        speakerTier=stylize.input_SLAM('Type the tier name indicating speaker/support Tier (or any categorizing variable):')

    #create interval tier for output
    newTier = TextGrid.IntervalTier(name = '%sStyleGlo'%targetTier, 
                  xmin = tg[targetTier].xmin(), xmax=tg[targetTier].xmax()) 
    newTierLoc = TextGrid.IntervalTier(name = '%sStyleLoc'%targetTier, 
                  xmin = tg[targetTier].xmin(), xmax=tg[targetTier].xmax()) 

    #Create swipe object from wave file or external PitchTier file
    inputPitch = None
    #try as PitchTier files (supported formats: short text and binary)
    if not inputPitch:
        for file in srcFile:
            try: inputPitch = stylize.readPitchtier(file)
            except: 
                  inputPitch = None;
                  continue
            print('Reading pitch from PitchTier file {}'.format(file)); break
    # try as wave files
    if not inputPitch:
        for file in srcFile:
            if not praatUtil.isGoodMonoWav(file): continue
            try: inputPitch = swipe.Swipe(file, pMin=75, pMax=500, s=timeStep, t=voicedThreshold, mel=False)
            except:
                  inputPitch = None;
                  continue
            print('Computing pitch on wave file {}'.format(file)); break
    # unknown format
    if not inputPitch:
        print('Error: source files {} are not supported !'.format(srcFile))
        continue

    print('Computing average register for each speaker')
    try:
        registers = stylize.averageRegisters(inputPitch, tg[speakerTier])
    except:
        continue

    print('Stylizing each interval of the target tier')

    #computing at which iterations to give progress
    LEN = float(len(tg[targetTier]))
    totalN+=LEN
    POSdisplay = set([int(float(i)/100.0*LEN) for i in range(0,100,10)])
    smooth_total = []
    time_total = []
    pl.rcParams["figure.figsize"] = [12,6]
    fig = pl.figure()
    support = None
    haveImgInbuf = False
    if exportFigures:
        pdf = pdfLib.PdfPages(outputFigureFile)

    for pos,targetIntv in enumerate(tg[targetTier]):
        if pos in POSdisplay:
            print('stylizing: %d %%'%(pos/LEN*100.0))

        supportIntvs = stylize.getSupportIntvs(targetIntv,supportTier=tg[speakerTier])
        tag = stylize.getTags(targetIntv,tg[tagTier])
        #compute style of current interval
        out = \
            stylize.stylizeObject(\
            targetIntv = targetIntv, supportIntvs = supportIntvs,\
            inputPitch = inputPitch,\
            registers = registers, alpha=alpha)
        if out == None: 
            continue
        else:
            (style_glo,style_loc,\
            targetTimes,deltaTargetPitch, deltaTargetPitchSmooth, \
            reference, reference_loc, rangeRegisterInSemitones, loccalDynamicRegister) = out
        
        # debug
        if len(style_glo) !=2 and len(style_glo) !=4 :
              print(('Error: a global style code {} incorrect !'.format(style_glo)))
              exit()
              #continue
        if len(style_loc) !=2 and len(style_loc) !=4 :
              print(('Error: a local style code{} incorrect !'.format(style_loc)))
              exit()
              #continue

        #prepare exportation of smoothed
        if isinstance(deltaTargetPitchSmooth, (np.ndarray,list)):
            if len(deltaTargetPitchSmooth)==len(targetTimes):
                reference_semitones = stylize.hz2semitone(reference)
                smooth_hz = [stylize.semitone2hz(delta + reference_semitones) for delta in deltaTargetPitchSmooth]
                smooth_total = np.concatenate((smooth_total,smooth_hz))
                time_total = np.concatenate((time_total,targetTimes))

        #exp
        EXP_TOPICAL_MARKER = True
        if EXP_TOPICAL_MARKER:
              if 'preN'.lower() in (targetIntv.mark()).lower():
                  stylesGlo += [style_glo]
                  stylesDynLoc += [style_loc]
                  #print(u'{}: {},{}'.format(targetIntv.mark(),style_glo,style_loc))#debug
        else:
              stylesGlo += [style_glo]
              stylesDynLoc += [style_loc]

        #then add an interval with that style to the (new) style tier
        newInterval = TextGrid.Interval(targetIntv.xmin(), targetIntv.xmax(), style_glo)
        newTier.append(newInterval)
        newIntervalLoc = TextGrid.Interval(targetIntv.xmin(), targetIntv.xmax(), style_loc)
        newTierLoc.append(newIntervalLoc)

        #compute figure either for examples or for export in PDF file
        if support != None:
            supportPreviousXmin = support.time[0]
            support = stylize.intv2customPitchObj(supportIntvs,inputPitch)
            is_new_support = (support.time[0] != supportPreviousXmin)
            
            if exportFigures and is_new_support and haveImgInbuf:
                  try:
                        pdf.savefig(fig)
                        if examplesDisplayCount: pl.show(); examplesDisplayCount-=1
                        fig.clf()
                        haveImgInbuf = False
                  except:
                        # debug
                        print('Error: fail to save figures in PDF !')
                        #pl.show();
                        fig.clf()
                        haveImgInbuf = False
        else :
            supportPreviousXmin = None
            support = stylize.intv2customPitchObj(supportIntvs,inputPitch)
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
                  rangeRegisterInSemitones = rangeRegisterInSemitones, alpha=alpha, tag =tag)
              haveImgInbuf = True

        except:
              pass
              
    if exportFigures and haveImgInbuf:
            pdf.savefig(fig)
            if examplesDisplayCount: pl.show(); examplesDisplayCount-=1
            fig.clf()
            haveImgInbuf = False

    #done, now writing tier into textgrid and saving textgrid
    print(('Saving computed styles in file %s'%outputTextgridFile))
    tg.append(newTier)
    tg.append(newTierLoc)
    tg.write(outputTextgridFile)
    print('Exporting smoothed pitchs in Binary PitchTierfile %s'%outputPitchTierFile)
    praatUtil.writeBinPitchTier(outputPitchTierFile,time_total,smooth_total)
    print('Exporting figures in PDF file %s'%outputFigureFile)
    if exportFigures: pdf.close()
    pl.close()

#Now output statistics
#---------------------
labs = ['Stylization over Global Register',\
        'Stylization over Local Register']
for i,styles in enumerate([stylesGlo,stylesDynLoc]):
      print(('style name:{}'.format(labs[i])))
      count = {}
      for unique_style in set(styles):
          if not len(unique_style):continue
          count[unique_style] = styles.count(unique_style)


      #valeurs triees par importance decroissante
      unsorted_values = np.array(list(count.values()))
      nbStylesRaw = len(unsorted_values)
      total = float(sum(unsorted_values))

      #remove styles that appear less than 0.5 percents of the time
      for style in list(count.keys()):
          if count[style]/total < 0.005: del count[style]

      unsorted_values = np.array(list(count.values()))
      stylesNames = list(count.keys())
      argsort = np.argsort(unsorted_values)[::-1] # from most to less important
      sorted_values = unsorted_values[argsort]

      total = float(sum(unsorted_values))
      L = min(len(list(count.keys())),20)
      print("""
------------------------------------------------------------------
SLAM analysis overall summary:
------------------------------------------------------------------
- %d intervals to stylize.
- %d intervals with a non empty style (others are unvoiced)
- %d resulting styles appearing in total
- %d resulting nonnegligible styles (appearing more than 0.5%% of the time)
------------------------------------------------------------------
- The %d most important nonnegligible styles along with their frequency are:"""%(
      totalN,\
      len(styles),\
      len(set(styles)),\
      len(count),\
      L))
      styleNames=sorted(count,key=count.get)
      styleNames.reverse()
      for styleName in styleNames[:L]:
          print(('\t%s\t:\t:%0.1f%% (%d occurrences)'%(styleName,count[styleName]/total*100.0,count[styleName])))
      print('''

x------------------------------------------x---------------------x
| explained proportion of the observations | number of styles    |
|         (percents)                       |                     |
x------------------------------------------x---------------------x''')
      cumulative_values = np.cumsum(sorted_values)
      cumulative_values = cumulative_values/float(cumulative_values[-1])
      for P in [70, 75, 80, 85, 90, 95, 99]:
          N = np.nonzero(cumulative_values>float(P)/100.0)[0][0]+1
          print('|                %2.0f                        |         %2.0f          |'%(P,N))
      print('x------------------------------------------x---------------------x')

print "... done in", stylize.get_duration(t1_secs = t1, t2_secs = time.time())
