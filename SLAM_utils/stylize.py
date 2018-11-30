# -*- coding: utf-8 -*-
"""
    #tode: 1.refine the identification of prominence. 2.indicate the main saliency in the output figure produced by show_stylization()

"""
import matplotlib
import matplotlib.pylab as pl
import numpy as np
import SLAM_utils.TextGrid as tg
from SLAM_utils import praatUtil
from SLAM_utils import swipe
import os

#handy funciotns
def get_extension(file): return os.path.splitext(file)[1]
def get_basename(file): return os.path.splitext(os.path.basename(file))[0]

#read a PitchTier as swipe file
class readPitchtier(swipe.Swipe):
	def __init__(self, file):
                try:
		    [self.time, self.pitch] = praatUtil.readBinPitchTier(file)
                except:
		    [self.time, self.pitch] = praatUtil.readPitchTier(file)

def hz2cent(f0_Hz):
    return 1200.0*np.log2( np.maximum(1E-5,np.double(f0_Hz) ))
def cent2hz(semitone):
    return np.double(2.0**(np.double(semitone) / 1200.0))
def hz2semitone(f0_Hz):
    return 12.0*np.log2( np.maximum(1E-5,np.double(f0_Hz) ))
def semitone2hz(semitone):
    return np.double(2.0**(np.double(semitone) / 12.0))
def sec2msec(sec):
    return 1000.0 * sec

def relst2register(semitones):
    #from relative semitones to register
    if isinstance(semitones,(int,float)):
        semitones = [semitones]
    result = []
    for st in semitones:
        if   st > 6  : result.append('H')
        elif st > 2  : result.append('h')
        elif st > -2  : result.append('m')
        elif st > -6  : result.append('l')
        elif st < -6  : result.append('L')
    return result

def averageRegisters(swipeFile,speakerTier=None):
    #if no speaker tier is provided, just take the average of the f0s
    if speakerTier is None:
        print('     No speaker tier given, just taking mean of f0s as average register')
        pitchs = [x for x in swipeFile if x]
        return np.mean(pitchs)

    #get all different speaker names
    speakerNames = set([interval.mark() for interval in speakerTier])
    registers     = {}
    #for each speaker, compute mean register
    for speaker in speakerNames:
        intervals = [interval for interval in speakerTier if interval.mark()==speaker]
        #on va calculer la moyenne=sum/n
        sumf0 = 0
        nf0 = 0
        for interval in intervals:
            imin, imax = swipeFile.time_bisect(interval.xmin(),interval.xmax())
            pitchs = [x for x in swipeFile.pitch[imin:imax] if x]
            sumf0 += np.sum(pitchs)
            nf0  += len(pitchs)
        if nf0:
            registers[speaker]=sumf0/np.double(nf0)
        else:
            registers[speaker]=None
    return registers

def SLAM1(semitones, tier=None, display=None, register=None):
    #this takes a sequence of semitones and applies the SLAM1 stylization

    #first, smooth the semitones curves using LOWESS
    if 100<len(semitones):
        r = int(len(semitones)/100.0)
        semitones = list(np.array(semitones)[::r])
    t = np.array(range(len(semitones)))/float(len(semitones))
    if 10<len(semitones):
        import SLAM_utils.lowess as lowess
        smooth = lowess.lowess(t,semitones)
    else:
        smooth = semitones

    start = smooth[0]
    stop = smooth[-1]
    style = relst2register(start)
    style+= relst2register(stop)
    #identify prominence. Either max or min
    #print('START/STOP/MAX', start, stop, np.max(smooth))
    xmax = np.max(smooth)
    xmin = np.min(smooth)
    maxdiffpositive = xmax - max(start,stop)
    maxdiffnegative = 0 #xmin # min(start, stop) - xmin

    #maxdiffpositive = np.max(np.abs([x-max(start,stop) for x in smooth]))
    #maxdiffnegative = 0
    #maxdiffnegative = np.abs(np.min([x-min(start,stop) for x in smooth]))

    #print('MAXPOS, MAXNEG')
    #print(maxdiffpositive, maxdiffnegative)
    if maxdiffpositive  > maxdiffnegative:
        #the max is further from boundaries than the min is
        extremum = maxdiffpositive
        posextremum = np.argmax(smooth)
        #print('EXTREMUM', extremum, t[posextremum])
        #print 'SMOOTH', semitones
    else:
        extremum = maxdiffnegative
        posextremum = np.argmin(smooth)
    if extremum>2:
        style+=relst2register(smooth[posextremum])
        if t[posextremum] < 0.33:
            style+='1'
        elif t[posextremum] < 0.66:
            style+='2'
        else:
            style+='3'
    style = ''.join(style)

    if display:
        show_stylization(semitones,smooth,style,tier=tier,register=register)

    #print('STYLE', style)
    return (style,smooth)

def show_stylization(original,smooth,style,tier=None,register=None,figId=1):
    semitones = original
    fig = matplotlib.pyplot.figure(figId)
    ax = fig.gca()
    #fig, ax = pl.subplots()
    if tier:
        fig.canvas.set_window_title('Figure {} - Melodic Contour of \'{}\' Transcribed as \'{}\''.format(figId,tier.mark(),style))
    else:
        fig.canvas.set_window_title('Figure {} - Melodic Contour Annotated as \'{}\''.format(figId,style))
    time = np.linspace(0, 1, len(semitones)) # normalized time
    # xtick (time) handeling
    num_intervals = 3
    num_xticks = num_intervals + 1
    xticks = np.linspace(0, 1, num_xticks)
    pl.xlim(xticks[0],xticks[-1])
    xticklabels = []
    for i, t in enumerate(xticks):
        if i: xticklabels.append('{:d}/{:d}'.format(i, num_intervals))
        else: xticklabels.append('0')
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    # ytick (pitch) handeling
    yticks_major = range(-6, 6 + 1, 4)
    yticks_minor = list(set(range(-8, 8 + 1, 2)) - set(yticks_major))
    ylim = [-6-4,6+4]
    pl.ylim(ylim)
    ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
    ax.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
    yticklabels_major = ['{:.0f}'.format(f) for f in yticks_major]
    yticklabels_minor = ['{:.0f}'.format(f) for f in yticks_minor]
    ax.set_yticklabels(yticklabels_major,minor=False,color='0')
    ax.set_yticklabels(yticklabels_minor,minor=True,color='.45')
    ax.set_xlabel('Normalized Time')
    pl.ylabel('Pitch (semitones)')
    if tier:
        # show mark and tonal annotation
        mark = tier.mark()
        style = mark + ' ' +  u'\u2192'+ ' ' + style
    if tier:
        # a second time axis in seconds
        ax2 = ax.twiny()
        xlim = [sec2msec(tier.xmin()), sec2msec(tier.xmax())]
        duration = sec2msec(tier.xmax() - tier.xmin())
        xticks2 = [x * duration + xlim[0] for x in xticks]
        xtick2labels = ['{:.0f} ms'.format(x) for x in xticks2]
        ax2.set_xlim(xlim)
        ax2.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks2))
        ax2.set_xticklabels(xtick2labels, fontsize=8.5)
        title = ax2.set_title(style, fontsize=14,fontweight='medium')
        title.set_y(1.06)
        fig.subplots_adjust(top=0.875)
    else:
        pl.title(style,style='',fontsize=14)
    if register != None:
        # a second frequency axis in log-scale of Hz
        yticks2_major = [register * semitone2hz(y) for y in yticks_major]
        yticks2_minor = [register * semitone2hz(y) for y in yticks_minor]
        ytick2labels_major = ['{:.0f} Hz'.format(y) for y in yticks2_major]
        ytick2labels_minor = ['{:.0f} Hz'.format(y) for y in yticks2_minor]
        ylim = ax.get_ylim()
        ylim2 = [register * semitone2hz(ylim[0]),register * semitone2hz(ylim[1])]
        ax3 = ax.twinx()
        ax3.set_yscale('log')
        ax3.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks2_major))
        ax3.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks2_minor))
        ax3.set_ylim(ylim2)
        ax3.set_yticklabels(ytick2labels_major,minor=False,color='0',fontsize=8.5)
        ax3.set_yticklabels(ytick2labels_minor,minor=True, color='.45',fontsize=8.5)
        ax3.grid(b=True, which='minor', color='.85',linestyle='-')
        ax3.grid(b=True, which='major',color='0', linestyle='-')
        ax2.grid(b=True, which='major',color='0', linestyle='-')
        ax2.set_zorder(ax3.get_zorder()+1)
        ax2.patch.set_visible(False)
        fig.subplots_adjust(right=0.875)
    ax.set_axisbelow(True)
    ax.set_zorder(ax2.get_zorder()+1)
    ax.patch.set_visible(False)
    lns1=ax.plot(time, semitones, 'b.') # input pitch
    lns2=ax.plot(time, smooth   , 'r') # smoothed pitch
    ax.legend(lns1+lns2,['Original Pitch','Pitch smoothed by LOWESS'])
    pl.show()

def stylizeObject(target,swipeFile, speakerTier=None,registers=None,stylizeFunction=SLAM1,estimate_mode=1):
    #get stylization for an object that implements the xmin() and xmax() methods.

    #get f0 values for target
    imin, imax = swipeFile.time_bisect(target.xmin(),target.xmax())
    pitchs_C = swipeFile.pitch[imin:imax]
    times_C = swipeFile.time[imin:imax]

    if len(pitchs_C)<2:
        #skipping interval (unvoiced)
        return ('_',[],[],[],[],[])

    #get corresponding interval in the speaker (i.e. support) tier
    speaker = None
    if speakerTier and isinstance(registers,dict):
        speakers_intervals = tg.getMatchingIntervals([target],speakerTier,strict=False,just_intersection=True)
        speakers = [i.mark() for i in speakers_intervals]
        speakersCount = dict( (x,speakers.count(x)) for x in set(speakers))
        #counting the speakers
        if len(speakersCount)>1:
            speaker = max(speakersCount,key=speakersCount.get)
            print('     Keeping %s'%speaker, speakersCount)
        else:
            #only one speaker for all target intervals
            speaker = speakers[0]

    if estimate_mode == 2:
        print('========== EXPERIMENT START ====')
        #get temporal indices
        #for target
        imin,imax = swipeFile.time_bisect(target.xmin(),target.xmax())
        if imin < imax: upper_bound = imax
        else: upper_bound = imax + 1
        target_int = range(imin,upper_bound)
        #for support
        support_int = []
        for i in speakers_intervals:
            if i.mark() == speaker:
                imin,imax = swipeFile.time_bisect(i.xmin(),i.xmax())
                if imin < imax: upper_bound = imax
                else: upper_bound = imax + 1
                support_int += range(imin,upper_bound)
        #get the temporal index of
        #the center of intersection of the support and the target
        inter = list(set(target_int) & (set(support_int)))
        center = inter[len(inter) // 2]

        #estimate register using Hann window
        r = 0.0
        c = 0.0
        half_width = max(center - support_int[0] + 1, support_int[-1] - center + 1)
        for t in support_int:
            #compute a Hann window
            w = 0.0
            #convoluate it with a rectangular function with its support as our target
            for center_mobile in inter:
                w += (np.cos(np.pi / 2.0 / float(half_width) * (t - center_mobile))) ** 2
            #w = 1 #debug: constant window
            r += w * swipeFile.pitch[t]
            c += w
        if c: r = r / c # normalization

    #get corresponding register value
    if not registers:
        #if a speaker tier is provided and registers is not already computed,
        #compute it.
        registers = averageRegisters(swipeFile,speakerTier)

    if speaker:
        #reference is the value of the registers for this speaker
        reference = registers[speaker]
        if not reference: return ('',[],[],[],[],[]) #bugfix
    else: #speaker == None
        if not is_numeric_paranoid(registers):
            print('WARNING : no speaker tier provided and reference is not numeric ! not stylizing.')
            return ('',[],[],[],[],[])
        #no speaker/support tier was provided, registers is only the average f0
        reference = registers

    if estimate_mode == 2:
        try:
            print('(new register, old register,diff): ({},{},{})'.format(r,reference, abs(r-reference)))
        except:
            print('(new register, old register): ({},{})'.format(r,reference))
            print(registers)
            exit(1)
        reference = r
        print('========== EXPERIMENT END ======')

    #delta with reference in semitones
    delta_pitchs_C = [1E-2*(hz2cent(pitch) - hz2cent(reference)) for pitch in pitchs_C]
    (style,smoothed) = stylizeFunction(delta_pitchs_C,tier=target,register=reference)

    smoothed_out = [cent2hz((100*delta + hz2cent(reference))) for delta in smoothed]
    #print(reference)
    return (style,delta_pitchs_C,smoothed,times_C, smoothed_out, reference)

# source:
# https://stackoverflow.com/questions/500328/identifying-numeric-and-array-types-in-numpy
def is_numeric_paranoid(obj):
    try:
        obj+obj, obj-obj, obj*obj, obj**obj, obj/obj
    except ZeroDivisionError:
        return True
    except Exception:
        return False
    else:
        return True
