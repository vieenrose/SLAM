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

def show_stylization(original,smooth,style,tier=None,register=None,figId=1,support=None,time_org=None, pdf=None):

    # alias
    intv = tier
    fid = figId

    # parameters
    num_time_partitions_per_target = 3
    num_freq_boundaries = 4
    freq_min = -6
    freq_max = +6
    #figfmt = 'png'

    fig, ax = pl.subplots()
    # put window title
    fig_window_title = 'Figure {} - Melodic Contour of \'{}\' Transcribed as \'{}\''.format(fid,intv.mark(),style)
    fig.canvas.set_window_title(fig_window_title)
    # make time axis
    xlim = [sec2msec(time_org[0]),sec2msec(time_org[-1])]
    xticks = np.linspace(xlim[0], xlim[1], num_time_partitions_per_target+1)
    xticks_major = xlim
    xticks_minor = sorted(list(set(xticks) - set(xlim)))
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks_major))
    ax.xaxis.set_minor_locator(matplotlib.ticker.FixedLocator(xticks_minor))
    xticks_labels_major = ['{:.0f} ms'.format(x) for x in xticks_major]
    xticks_labels_minor = ['{:.0f}'.format(x) for x in xticks_minor]
    ax.set_xticklabels([],minor=False,fontsize=7)
    #ax.set_xticklabels(xticks_labels_minor,minor=True)
    
    ax.grid(b=True,which='major', axis='x', color='0')
    ax.grid(b=True,which='minor', axis='x',color='.9')
    # make frequency axis
    yticks_major = np.linspace(freq_min, freq_max, num_freq_boundaries)
    freq_step_major = (freq_max - freq_min) / (num_freq_boundaries - 1)
    yticks_minor = np.linspace(freq_min - freq_step_major/2, freq_max+freq_step_major/2, num_freq_boundaries + 1)
    yticklabels_major = ['{:.0f} ST'.format(f) for f in yticks_major]
    yticklabels_minor = ['{:.0f}'.format(f) for f in yticks_minor]
    ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
    ax.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
    ax.set_yticklabels(yticklabels_major,minor=False)
    ax.set_yticklabels(yticklabels_minor,minor=True)
    tot_yticks = np.concatenate((yticks_major,yticks_minor))
    ylim = [min(tot_yticks),max(tot_yticks)]
    pl.ylim(ylim)
    
    # make 2nd freauency axis
    ax2 = ax.twinx()
    ytick2labels_major = ['{:.0f}'.format(register*semitone2hz(y)) for y in yticks_major]
    ytick2labels_minor = ['{:.0f} Hz'.format(register*semitone2hz(y)) for y in yticks_minor]
    ax2.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
    ax2.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
    ax2.set_yticklabels(ytick2labels_major,minor=False)
    ax2.set_yticklabels(ytick2labels_minor,minor=True)
    
    pl.ylim(min(tot_yticks),max(tot_yticks))
    # draw support (debug)
    supp_intv = sec2msec(support[0])
    supp_org = hz2semitone(support[1]) - hz2semitone(register)
    supp_mark = support[2]
    ax2.plot(supp_intv,supp_org, 'b.')
    # draw target
    target_intv = sec2msec(time_org)
    lns1=ax2.plot(target_intv,smooth,'r',linewidth=3.5)
    lns2=ax2.plot(target_intv,original,'g.',linewidth=3.5)
    tot_intv = np.concatenate((supp_intv,target_intv))
    pl.xlim(min(min(tot_intv),xticks[0]),max(max(tot_intv),xticks[-1]))
    ax.grid(b=True,which='major', axis='y', color='0')
    title = ax.set_title('Support: ' + supp_mark, fontweight='medium')
    title.set_y(1.035)
    
    # annotation
    style = 'Target: ' + tier.mark() + ' ' +  u'\u2192'+ ' ' + style
    ax.set_xlabel(xlabel=style,fontsize=12,fontweight='medium')
    ax.xaxis.set_label_coords(0.5, -0.1)
    fig.subplots_adjust(bottom=0.14)
    
    # annotation2
    xlim=ax.get_xlim()
    diff_xlim = max(xlim)-min(xlim)
    diff_ylim = max(ylim)-min(ylim)
    x1 = (xticks_major[0]-xlim[0])/diff_xlim
    x2 = (xticks_major[1]-xlim[0])/diff_xlim
    ax.annotate(xticks_labels_major[0],xy=(x1-0.1,-0.07),xycoords='axes fraction',fontsize=10)
    ax.annotate(xticks_labels_major[1],xy=(x2,-0.07),xycoords='axes fraction',fontsize=10)
    ax2.legend(['Input Pitch','Pitch Smoothed by LOWESS'])

    # let us plot the figure!
    #pl.show()
    #fig.savefig('figures/{}_fig{}.{}'.format(file_basename, figId, figfmt), format=figfmt,dpi=300)
    pdf.savefig(fig)

def intv2pitch(intv,swipeFile):
    imin, imax = swipeFile.time_bisect(intv.xmin(),intv.xmax())
    pitch = swipeFile.pitch[imin:imax]
    time = swipeFile.time[imin:imax]
    return [time,pitch]

def getMaxMatchIntv(target,support):
    candidateIntvs = tg.getMatchingIntervals(target,support,strict=False,just_intersection=True)
    marks = [intv.mark() for intv in candidateIntvs]
    marksCount = dict( (mark,marks.count(mark)) for mark in set(marks))
    #counting the speakers
    if len(marksCount)>1:
        optMark = max(marksCount,key=marksCount.get)
        print('     Keeping %s'%optMark, marksCount)
    else:
        #only one speaker for all target intervals
        optMark = marks[0]
    optIntv = [intv for intv in candidateIntvs if intv.mark() == optMark][0]
    return optMark, optIntv, candidateIntvs

def stylizeObject(target,swipeFile, speakerTier=None,registers=None,stylizeFunction=SLAM1,estimate_mode=1):

    targetIntv = target

    #get stylization for an object that implements the xmin() and xmax() methods.
    [times_C,pitchs_C] = intv2pitch(target,swipeFile)

    #skipping interval (unvoiced)
    if len(pitchs_C)<2: return ('_',[],[],[],[],[],[])

    #get corresponding interval in the speaker (i.e. support) tier
    [optSpeaker,optIntv, candiateIntvs] = getMaxMatchIntv([targetIntv],speakerTier)

    speaker = optSpeaker
    speakers_intervals=candiateIntvs

    #if estimate_mode == 2:
    if True:
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
        if not reference: return ('',[],[],[],[],[],[]) #bugfix
    else: #speaker == None
        if not is_numeric_paranoid(registers):
            print('WARNING : no speaker tier provided and reference is not numeric ! not stylizing.')
            return ('',[],[],[],[],[],[])
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
    delta_pitchs_C = [(hz2semitone(pitch) - hz2semitone(reference)) for pitch in pitchs_C]
    (style,smoothed) = stylizeFunction(delta_pitchs_C,tier=target,register=reference)

    smoothed_out = [cent2hz((100*delta + hz2cent(reference))) for delta in smoothed]
    #print(reference)
    supportIntv = intv2pitch(optIntv,swipeFile)
    supportIntv.append(optIntv.mark())
    return (style,delta_pitchs_C,smoothed,times_C, smoothed_out, reference,supportIntv)

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
