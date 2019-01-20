# -*- coding: utf-8 -*-

import matplotlib
import matplotlib.pylab as pl
import numpy as np
import SLAM_utils.TextGrid as tg
from SLAM_utils import praatUtil
from SLAM_utils import swipe
import os, math, sys


minDELTA=4
locality = 100

def SLAM1(semitones, time = None, rangeRegisterInSemitones = 20):

    #this takes a sequence of semitones and applies the SLAM1 stylization

    #first, smooth the semitones curves using LOWESS
    # DOWNSAMPLE_ON = False
    """
    if 100<len(semitones) and DOWNSAMPLE_ON: 
        # ? why do a downsampling ?
        # 1.assumed that the signal is of narraowband due to the
        # the filtering processing by SWIPE ?
        # 2.make acceleration ?
        r = int(len(semitones)/100.0)
        semitones = list(np.array(semitones)[::r])
    """

    t = np.array(range(len(semitones)))/float(len(semitones))
    if 10<len(semitones):
        import SLAM_utils.lowess as lowess
        smooth = lowess.lowess(t,semitones)
    else:
        smooth = semitones

    numQuantizationRegions = 5
    DELTA = max(rangeRegisterInSemitones / numQuantizationRegions,minDELTA)
    delta = DELTA / 2

    # identify the three essential points
    if len(smooth) >= 3: ti,fr=identifyThreeEssentialPoints(smooth, time = time, thld=delta)
    else: ti,fr = time, smooth
    
    # transcript the model in SLAM annotation
    style = relst2register(fr[0], DELTA=DELTA)
    style+= relst2register(fr[-1], DELTA=DELTA)
    if len(fr)>=3:
        denum = ti[-1] - ti[0]
        if abs(denum) > 0:
            tNotmalized = (ti[1] - ti[0]) / denum
            style += relst2register(fr[1], DELTA=DELTA)
            positionId = int(math.ceil(3*tNotmalized))
            style+= str(positionId)

    style = ''.join(style)
    
    return (style,smooth)

def show_stylization(time_org,original,smooth,style1,style2,targetIntv,register, register_loc,figIn,support,rangeRegisterInSemitones,alpha, tag,is_new_support=True ):

    # parameters
    num_time_partitions_per_target = 3
    num_freq_boundaries = 5
    freq_min = -10
    freq_max = +10
    linestyle_RelGrid_Major=':'
    linestyle_RelGrid_Minor=''
    linestyle_AbsGrid = ''
    color_LocReg = 'red'
    linestyle_LocReg = ':'
    color_GloReg = 'black'
    linestyle_GloReg ='-'
    linestyle_pitch = ''
    linestyle_style2 = '-'
    markerstyle_pitch = '.'
    color_RelGrid_Minor = 'lightgrey'
    color_RelGrid_Major='k'
    background_color = 'white'
    color_style_styl='seagreen'
    color_style_sty2='red'
    color_smooth = 'orange'
    color_essentials = color_smooth
    linewidth_RelGrid_Major=.5
    linewidth_RelGrid_Minor=.5
    linewidth_AbsGrid = .5
    markersize_pitch = 2*2
    markersize_essentials = 5*1.5
    linewidth_LocReg = .5*2*2
    linewidth_GloReg = .5*2
    
    linewidth_smooth=1
    linewidth_Style1 = 1*2
    linewidth_Style2=1*2
    linewidth_pitch=linewidth_smooth
    # define the softness of boundelines of ranger of register 
    alphaGlo = alpha
    alphaLoc = alpha
    
    fig = figIn
    ax = fig.gca()
    
    # put window title
    if is_new_support:
      ax.set_facecolor(background_color)
      fig_window_title = u'Figure - Melodic Contour of \'{}\''.format(support.label)
      fig.canvas.set_window_title(fig_window_title)
    # make time axis
    xlim = [sec2msec(time_org[0]),sec2msec(time_org[-1])]
    xticks = np.linspace(xlim[0], xlim[1], num_time_partitions_per_target+1)
    xticks_major = xlim
    xticks_minor = sorted(list(set(xticks) - set(xticks_major)))
    
    if not is_new_support:
        xticks_minor+=list(ax.xaxis.get_ticklocs(minor=True))
        #xticks_minor+=list(ax.xaxis.get_ticklocs(minor=False))
        xticks_major2=list(ax.xaxis.get_ticklocs(minor=False))
        xticks_major2+=xticks_major

    if is_new_support:
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks_major))
    else:
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks_major2))

    #ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xticks_major))
    ax.xaxis.set_minor_locator(matplotlib.ticker.FixedLocator(xticks_minor))
    xticks_labels_major = ['{:.0f} ms'.format(x) for x in xticks_major]
    xticks_labels_minor = ['{:.0f}'.format(x) for x in xticks_minor]
    ax.set_xticklabels([],minor=False,fontsize=7)
    #ax.set_xticklabels(xticks_labels_minor,minor=True)
    
    ax.grid(b=True,which='major', axis='x',color=color_RelGrid_Major,linestyle=linestyle_RelGrid_Major,linewidth=linewidth_RelGrid_Major)
    ax.grid(b=True,which='minor', axis='x',color=color_RelGrid_Minor,linestyle=linestyle_RelGrid_Minor,linewidth=linewidth_RelGrid_Minor)
    #minDELTA=4#4.0 #debug
    DELTA = max(rangeRegisterInSemitones / 5,minDELTA)
    #print("show_styl.: DELTA=",DELTA)
    yticks_major=\
    [-3*DELTA,\
    -2.5*DELTA, \
    -1.5*DELTA, \
    -0.5*DELTA, \
    0.5*DELTA, \
    1.5*DELTA, \
    2.5*DELTA,\
    3*DELTA]
    #[-10,-6,-2,2,6,10]
    yticks_minor=[-2*DELTA,-DELTA,0, DELTA,2*DELTA]
    #yticks_minor=[-8,-4,0,4,8]
    #ticks2style={yticks_minor[2]:'m',yticks_minor[1]:'l',yticks_minor[0]:'L',yticks_minor[3]:'h',yticks_minor[4]:'H'}
    #def findlabel(ytick, yticks_minor):
    #      labs = ['L','l','m','h','H']
    #      return labs[np.argmin(abs(np.array(yticks_minor) - ytick))]
          
    #{0:'m',-4:'l',-8:'L',4:'h',8:'H'}
    ytick2labels_major = ['{:.0f} Hz'.format(register*semitone2hz(y)) for y in yticks_major]
    ytick2labels_minor = ['{:.0f}'.format(register*semitone2hz(y)) for y in yticks_minor]
    if is_new_support:
          #print('show_styl. yticks_major=',yticks_major)#debug
          #print('show_styl. yticks_minor=',yticks_minor)#debug
          ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
          ax.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
          ax.set_yticklabels(ytick2labels_major,minor=False)
          ax.set_yticklabels(ytick2labels_minor,minor=True)
          
    tot_yticks = np.concatenate((yticks_major,yticks_minor))
    ylim = [min(tot_yticks),max(tot_yticks)]
    pl.ylim(ylim)
    
    # plot global register on support
    if is_new_support:
          xlim_support = [sec2msec(support.time[i])for i in [0,-1]]
          lnst6=ax.plot(xlim_support,[0,0], linewidth=linewidth_GloReg,zorder=0,linestyle=linestyle_GloReg,color=color_GloReg)
    """
    # make 2nd freauency axis
    if is_new_support:
          ax2 = ax.twinx()
          # move the second axis to background
          yticklabels_major = ['{:.0f} ST'.format(f) for f in yticks_major]
          yticklabels_minor = ['{:.0f}'.format(f) for f in yticks_minor]
          ax2.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
          ax2.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
          ax2.set_yticklabels(yticklabels_major,minor=False)
          ax2.set_yticklabels(yticklabels_minor,minor=True)
    """
   
    """       
    # grid relative to local regster in bleu lines
    register_local = hz2semitone(np.mean([semitone2hz(f) for f in smooth]))
    for offset in [0,-2,2,-6,6,-10,10]:
        if offset :
            ax.plot(xticks_major,[register_local+offset,register_local+offset], linestyle=linestyle_RelGrid_Minor,color=color_RelGrid_Minor,linewidth=linewidth_RelGrid_Minor,zorder=0)
        else: # i.e. offset = 0
            lnst5=ax.plot(xticks_major,[register_local+offset,register_local+offset], '-',linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    """
    
    pl.ylim(min(tot_yticks),max(tot_yticks))
    # draw support 
    if is_new_support or True:
      supp_intv = sec2msec(support.time)
      supp_org = hz2semitone(support.freq) - hz2semitone(register)
      supp_mark = support.label
    
    # draw target
    target_intv = sec2msec(time_org)
   
    
    # stylization
    # rangeRegisterInHz
    def style2pitch(style,xmin,xmax, yoffset=0, DELTA = 4):
        #print('style2pitch:style=',style) #debug
        alphabet2semitones = {'H': 8, 'h': 4, 'm': 0, 'l' : -4, 'L' : -8} 
        
        def relativePos2time(Pos, interval): 
            return interval[0] + (int(Pos) - .5) / 3 * (interval[-1]-interval[0])
        f_i = register2relst(style[0],DELTA=DELTA)[0] + yoffset #alphabet2semitones[style[0]]+yoffset
        f_f = register2relst(style[1],DELTA=DELTA)[0] + yoffset #alphabet2semitones[style[1]]+yoffset
              
        style_intv = [xmin,xmax]
        style_pitch = [f_i,f_f]
        if len(style) >=4:
            f_p = register2relst(style[2],DELTA=DELTA)[0] + yoffset #alphabet2semitones[style[2]]+yoffset
            t_p = relativePos2time(style[3],[xmin,xmax])
            #print(style_intv)
            style_intv.insert(1,t_p)
            #print(style_intv)
            style_pitch.insert(1,max([f_p,f_i+DELTA/2.0,f_f+DELTA/2.0]))
        return style_intv,style_pitch
    
        
    #register_loc = register*semitone2hz(np.mean(smooth)) #debug
    #print('show_sty.: register_loc=',register_loc)
    #try:
    #print("show_sty:style1=",style1)#debug
    #DELTA = max(rangeRegisterInSemitones / 5,4.0)
    #print("show_sty:DELTA = ", DELTA)#debug
    style1_intv,style1_pitch = style2pitch(style1,xticks_major[0],xticks_major[-1], DELTA=DELTA)
    #print('style1_pitch:',style1_pitch)#debug
    alphabet2semitones = {'H': 8, 'h': 4, 'm': 0, 'l' : -4, 'L' : -8}
    yoffset=hz2semitone(register_loc)-hz2semitone(register)
    #print(style1,style2)
    style2_intv,style2_pitch = style2pitch(style2,xticks_major[0],xticks_major[-1],DELTA=DELTA, yoffset=yoffset)
          
    # 2(+1) essential points
    ti,fr=identifyThreeEssentialPoints(smooth,time=time_org, thld=DELTA / 2)
    essential_intv = sec2msec(np.array(ti))
    essential_pitch = fr
    
    if is_new_support:
        lns0=ax.plot(supp_intv,supp_org, 'b',linestyle=linestyle_pitch,markersize=markersize_pitch,linewidth=linewidth_pitch, marker=markerstyle_pitch)
        # compute range
        # range here is defined as the (100-a)-th percentiele - the a-th percentiele
        # in logarithmic scale
        # we implement, in  the below, for example alpha = 5

        stat_max_freq = np.percentile(supp_org, 100-alphaGlo)
        stat_min_freq = np.percentile(supp_org, alphaGlo)
        range_of_register = \
            register *(semitone2hz(stat_max_freq)) - \
            register *(semitone2hz(stat_min_freq))
            

        # plot the soft / statistical upper and lower bounds of freq.
        #lnsu=ax.plot(supp_intv,stat_min_freq*np.ones(len(supp_intv)),linestyle=linestyle_GloReg,color=color_GloReg,linewidth=linewidth_GloReg)
        #lnsl=ax.plot(supp_intv,stat_max_freq*np.ones(len(supp_intv)),linestyle=linestyle_GloReg,color=color_GloReg,linewidth=linewidth_GloReg)
        
      
    #lns1=ax.plot(target_intv,original,'b',linewidth=2)
    
    lns2=ax.plot(target_intv,smooth,color=color_smooth,linewidth=linewidth_smooth)
    if len(essential_intv)>2:
      # only show the significative main saliancy 
      lns4=ax.plot(essential_intv[1],essential_pitch[1],'ro',markersize=markersize_essentials,color=color_essentials)
    lns3=ax.plot(style1_intv,style1_pitch,color=color_style_styl,linewidth=linewidth_Style1)
    lns3p=ax.plot(style2_intv,style2_pitch,color=color_style_sty2,linewidth=linewidth_Style2,linestyle=linestyle_style2)

    # grid relative to local regster
    """
    register_local = hz2semitone(np.mean([semitone2hz(f) for f in smooth]))
    for offset in [0,-1,1,-3,3,-5,5]:
        if offset :
            ax.plot(xticks_major,[register_local+offset,register_local+offset], linestyle=linestyle_RelGrid_Minor,color=color_RelGrid_Minor,linewidth=linewidth_RelGrid_Minor,zorder=0)
        else: # i.e. offset = 0
            lnst5=ax.plot(xticks_major,[register_local+offset,register_local+offset], '-',linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    """
    offset = 0
    register_local = hz2semitone(register_loc)-hz2semitone(register) #hz2semitone(np.mean([semitone2hz(f) for f in smooth])) #debug
    lnst5=ax.plot(xticks_major,[register_local+offset,register_local+offset], '-',linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    
    ones_vec = np.ones(len(xticks_major))
    soft_min_LocReg = np.percentile(smooth, alphaLoc)
    soft_max_LocReg = np.percentile(smooth, 100-alphaLoc)
    #ax.plot(xticks_major,ones_vec*soft_min_LocReg, linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    #ax.plot(xticks_major,ones_vec*soft_max_LocReg, linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    
    #print(supp_intv)
    if is_new_support:
          tot_intv = np.concatenate((supp_intv,target_intv))
          pl.xlim(min(min(tot_intv),xticks[0]),max(max(tot_intv),xticks[-1]))
          ax.grid(b=True,which='major', axis='y', color='0',linestyle=linestyle_AbsGrid,linewidth=linewidth_AbsGrid)
          
    if is_new_support:
          ax.set_ylabel('Frequencey (Hz)')
    
    fig.subplots_adjust(top=0.95,bottom=0.27,left=0.2, right=0.925)
    xlim=ax.get_xlim()
    diff_xlim = max(xlim)-min(xlim)
    diff_ylim = max(ylim)-min(ylim)
    x1 = (xticks_major[0]-xlim[0])/diff_xlim
    x2 = (xticks_major[1]-xlim[0])/diff_xlim
    
    labelsLeftPos = -0.1
    
    # duration label
    ax.annotate('{:.0f} ms'.format(xticks_major[-1]-xticks_major[0]),xy=(x2/2+x1/2,-0.035),xycoords='axes fraction',fontsize=6,horizontalalignment='center')
    if is_new_support:
       # support label
       ax.annotate(supp_mark,xy=(0.5,-0.13+.04-0.02),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='medium',horizontalalignment='center',fontstyle='italic')
       ax.annotate('Support:',xy=(labelsLeftPos,-0.13+.04-0.02),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='semibold',horizontalalignment='right',fontstyle='normal')
    
    # target label
    ax.annotate(targetIntv.mark(),xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.13+.04-0.08-0.01),xycoords=('data','axes fraction'),fontsize=9,fontweight='medium',horizontalalignment='center',fontstyle='italic')
    ax.annotate('Target:',xy=(-0.1,-0.13+.04-0.08-0.01),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='semibold',horizontalalignment='right',fontstyle='normal')
    
    # its stlization in symbolic form
    ax.annotate('Global Labels:',xy=(labelsLeftPos,-0.19+.04+.02-0.08-0.01-0.02),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='semibold',horizontalalignment='right',color=color_style_styl)
    ax.annotate(style1,xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.19+.04+.02-0.08-0.01-0.02),xycoords=('data','axes fraction'),fontsize=9,fontweight='semibold',horizontalalignment='center',color=color_style_styl)
    txt_style2= style2
    ax.annotate('Local Labels:',xy=(labelsLeftPos,-0.19+.04+.02-0.08-0.01-0.02-0.06),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='semibold',horizontalalignment='right',color=color_style_sty2)
    
    ax.annotate(style2,xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.19+.04+.02-0.08-0.01-0.02-0.06),xycoords=('data','axes fraction'),fontsize=9,fontweight='semibold',horizontalalignment='center',color=color_style_sty2)
    #ax.annotate(style1,xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.19+.04+.02-0.08-0.01-0.02),xycoords=('data','axes fraction'),fontsize=9,fontweight='semibold',horizontalalignment='center',color=color_style_sty2)
    
    #ax.annotate(txt_style2,xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.17),xycoords=('data','axes fraction'),fontsize=9,fontweight='semibold',horizontalalignment='center',color=color_style_sty2)
    if tag:
        ax.annotate('Tag:',xy=(labelsLeftPos,-0.19+.04+.02-0.08-0.01-0.02-0.06-0.06),xycoords=('axes fraction','axes fraction'),fontsize=11,fontweight='semibold',horizontalalignment='right',color='blue')
        ax.annotate(tag,xy=(.5*xticks_major[0]+.5*xticks_major[1],-0.19+.04+.02-0.08-0.01-0.02-0.06-0.06),xycoords=('data','axes fraction'),fontsize=9,fontweight='semibold',horizontalalignment='center',color='blue')

    """
    # grid relative to local regster in bleu lines
    register_local = hz2semitone(np.mean([semitone2hz(f) for f in smooth]))
    for offset in [0,-2,2,-6,6,-10,10]:
        if offset :
            ax.plot(xticks_major,[register_local+offset,register_local+offset], linestyle=linestyle_RelGrid_Minor,color=color_RelGrid_Minor,linewidth=linewidth_RelGrid_Minor,zorder=0)
        else: # i.e. offset = 0
            lnst5=ax.plot(xticks_major,[register_local+offset,register_local+offset], '-',linewidth=linewidth_LocReg,zorder=0,linestyle=linestyle_LocReg,color=color_LocReg)
    """
    
    # make 2nd freauency axis
    # bug (solved by add synchronization): when support = target, this axis sffuers of an offset !!!
    if is_new_support:
          ax2 = ax.twinx()
          ax2.set_ylim(ax.get_ylim()) # synchronize two y-axis
          # move the second axis to background
          yticklabels_major = ['{:.2f}'.format(f) for f in yticks_major]
          yticklabels_minor = ['L','l','m','h','H'] #['{:.2f}'.format(f) for f in yticks_minor]
          ax2.yaxis.set_major_locator(matplotlib.ticker.FixedLocator(yticks_major))
          ax2.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(yticks_minor))
          ax2.set_yticklabels(yticklabels_major,minor=False)
          #print('show_styl. yticks_major=',yticks_major)#debug
          #print('show_styl. yticks_minor=',yticks_minor)#debug
          #ax2.set_yticklabels(yticklabels_minor,minor=True,color=color_style_styl,fontweight='semibold')
          ax2.set_ylabel('Frequencey Relative to Global Register (semitones)')

    # support label
    if is_new_support:
      key_of_register = register  
      #supp_mark += ', key: {:.0f} Hz, range: {:.0f} Hz'.format(key_of_register, range_of_register)
      text_key_range = 'Global Key: {:.0f} Hz, Global Range: {:.0f} Hz, DELTA = {} (semitones), alpha = {:4.2f}'.format(key_of_register, range_of_register, DELTA,alpha)
      ax.annotate(text_key_range,xy=(0.5,1.025),xycoords='axes fraction',fontsize=11,fontweight='medium',  horizontalalignment='center',fontstyle='italic')
      
      #lines = lns3+lns3p+lns2+lns0+lnst6+lnst5
      lines = lns3+lns3p+lns2+lns0+lnst6+lnst5
      ax2.legend(lines,\
      ['Stylized @ GloReg',\
      'Stylized @ LocReg',\
       'Smoothed Cleaned Pitch (LOWESS)',\
       'Cleaned Pitch',\
       'Global Register (Key)',\
       'Dynamic Local Register (Key)'
       #'Significtive Main Saliency on Smoothed Pitch'\
       ],fontsize=11)
       
    # let us make the figure!
    return fig

def stylizeObject(targetIntv,supportIntvs,inputPitch,alpha,stylizeFunction1=SLAM1):

    # skip unlabeled
    if targetIntv.mark()=='_': #or (all ([i for i in supportIntvs]) == '_'):
      return None

    #get stylization for an object that implements the xmin() and xmax() methods.
    [targetTimes,targetPitch] = intv2pitch(targetIntv,inputPitch)
    
    #do not process if no enough of sample
    if len(targetPitch)<2 :
          return None
        
    #get valide reference
    """
    if is_numeric_paranoid(registers): 
          #no speaker/support tier was provided, registers is only the average f0
          reference = registers
    """
    #else:
    try:
        #reference = registers[supportIntvs[0].mark()]
        supportObj = intv2customPitchObj(supportIntvs,inputPitch)
        supportTimes,supportPitch = supportObj.time, supportObj.freq
        if not len(supportPitch): return None
        
        """
        estimation of key of register using 'numpy.convolve' function
        note: not very approritate for non-regular time step sampling pitch
        """
        
        kMaxTarget = (np.abs(supportObj.time - targetTimes[-1])).argmin()
        kMinTarget = (np.abs(supportObj.time - targetTimes[ 0])).argmin()
        kMinSupport = 0
        KMaxSupport = len(supportObj.time) - 1
        
        spanOfKInWindow = range(kMinSupport - kMaxTarget, KMaxSupport - kMinTarget + 1)
        lenSpanOfWindow = len(spanOfKInWindow)
        minSpanOfKInWindow = min(spanOfKInWindow)
        maxSpanOfKInWindow = max(spanOfKInWindow)
        width = 2 * max(abs(maxSpanOfKInWindow), abs(maxSpanOfKInWindow))
        if lenSpanOfWindow:
            windowVect = np.array([])
            for k in reversed(spanOfKInWindow):
                  scaled_k = locality * k
                  if scaled_k > maxSpanOfKInWindow or scaled_k < minSpanOfKInWindow: weight = 0.0
                  else: weight = 0.5 + 0.5 * np.cos(np.pi * (scaled_k / float(width)))
                  windowVect = np.append(windowVect, [weight])
            unitPitch = np.ones(len(supportPitch))
            estDynLocReg  = np.convolve(windowVect, supportPitch, mode = 'valid')
            unitDynLocReg = np.convolve(windowVect, unitPitch   , mode = 'valid')
            normUnitDynLocReg = sum(unitDynLocReg)
            if normUnitDynLocReg: estDynLocReg = sum(estDynLocReg) / sum(unitDynLocReg)
            else:                 estDynLocReg = 0
        else:
            estDynLocReg = supportPitch[kMinTarget]

        loccalDynamicRegister=estDynLocReg
        register_loc = loccalDynamicRegister
        
    except:
        return None
        
    #delta with reference in semitones and stylize it
    pitchOverSupportInHz = supportPitch
    register_glo = semitone2hz(np.mean(hz2semitone(supportPitch))) # debug
    rangeRegisterInSemitones = \
    rangeRegisterFunc(pitchOverSupportInHz, keyRegiserInHz = register_glo, alpha = alpha)
    deltaTargetPitch = [(hz2semitone(pitch) - hz2semitone(register_glo)) for pitch in targetPitch]
    out = stylizeFunction1(deltaTargetPitch,targetTimes,rangeRegisterInSemitones)
    if out == None:return None
    else:(style_glo,smoothed_glo) = out
    deltaTargetPitch2 = [(hz2semitone(pitch) - hz2semitone(loccalDynamicRegister)) for pitch in targetPitch]
    out = stylizeFunction1(deltaTargetPitch2,targetTimes,rangeRegisterInSemitones)
    if out == None:return None
    else:(style_loc,smoothed_loc) = out
    
    return (style_glo,style_loc,targetTimes,deltaTargetPitch,smoothed_glo,register_glo,register_loc, rangeRegisterInSemitones, loccalDynamicRegister)

"""
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
"""
def getSupportIntvs(targetIntv,supportTier):
      
      """
      this function returns the interval of 'supportTier' which 
      matchs the best with the given 'targetIntv'. 
      
      inputs
            targetIntv
            supportTier
      return
            supportIntv
      """

      trgt,spprt = targetIntv,supportTier #alias
      supportIntvs = tg.getMatchingIntervals([trgt],spprt,strict=False,just_intersection=True)
      if not supportIntvs: return supportIntvs
      labels = [intv.mark() for intv in supportIntvs]
      labelsCount = dict((label,labels.count(label)) for label in set(labels))
      bestLabel = max(labelsCount,key=labelsCount.get)
      
      """
      for intv in supportIntvs:
          if intv.mark() == bestLabel:
              return intv
      """
      # it can occur that 2+ intervals carry the same label, return all
      # these sub-intervals to be complete
      intvs = [intv for intv in supportIntvs if intv.mark() == bestLabel]
      #print('getSupportIntvs:targetIntv:(xmin,xmax)=',targetIntv.xmin(),targetIntv.xmax())#debug
      """
      for intv in intvs:
            print('getSupportIntvs:SupportIntv:(xmin,xmax)=',intv.xmin(),intv.xmax())#debug
      """
      return intvs
      
def getTags(targetIntv,tagTier):
      
      """
      this function returns the interval of 'supportTier' which 
      matchs the best with the given 'targetIntv'. 
      
      inputs
            targetIntv
            supportTier
      return
            supportIntv
      """

      trgt,lb = targetIntv,tagTier #alias
      supportIntvs = tg.getMatchingIntervals([trgt],lb,strict=False,just_intersection=True)
      labels = [intv.mark() for intv in supportIntvs]
      return u' '.join(labels)

                    
def printIntv(intv):
        
      """
      convinient function to shwo the content of an 'interval' 
      objet defined in 'TextGrid' class
      """
      print('{}: [{},{}]'.format(intv.mark().encode('utf-8'),intv.xmin(),intv.xmax()))
            
class intv2customPitchObj():
      
      """
      convinient class which converts an 'interval' objet to
      a class having the 3 follwing attributes: time, freq, label
      which is useful for tracing figure
      """
      def __init__(self,supportIntvs, inputPitch):
            
            # check if all these intervals have the same label
            if ([intv for intv in supportIntvs if intv.mark() == supportIntvs[0].mark()]):
                   label = supportIntvs[0].mark()
            else:
                  print('Error: something may be wrong !')
                  exit()

            self.label=label
            self.time = np.array([])
            self.freq = np.array([])
            for supportIntv in supportIntvs:
                  [time,freq]=intv2pitch(supportIntv,inputPitch)
                  # concatenate all time vectors in one time vector (same for freq.)
                  self.time=np.concatenate((self.time,time))
                  self.freq=np.concatenate((self.freq,freq))
                  
      
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
    return 1000.0 * np.array(sec)

def relst2register(semitones, DELTA = 4):
    #from relative semitones to register
    #DELTA: quantization step size
    if isinstance(semitones,(int,float)):
        semitones = [semitones]
    result = []
    for st in semitones:
        if   st >  1.5 * DELTA  : result.append('H')
        elif st >  0.5 * DELTA  : result.append('h')
        elif st > -0.5 * DELTA  : result.append('m')
        elif st > -1.5 * DELTA  : result.append('l')
        else : #st <= -1.5 * DELTA
              result.append('L')

    #debug
    """
    if not result:
      print('Error of Null Output (relst2register): (semitones, DELTA)=({},{})'.format(semitones, DELTA))
      exit()
    """
      
    return result
    

def register2relst(style, DELTA = 4):
      st = []
      for c in style:
            if   c == 'H'  : st.append( 2.5 * DELTA - 0.5 * DELTA)
            elif c == 'h'  : st.append( 1.5 * DELTA - 0.5 * DELTA)
            elif c == 'm'  : st.append( 0.5 * DELTA - 0.5 * DELTA)
            elif c == 'l'  : st.append(-0.5 * DELTA - 0.5 * DELTA)
            elif c == 'L'  : st.append(-1.5 * DELTA - 0.5 * DELTA)
            else           : st.append(c)
      return st
      

def rangeRegisterFunc(pitchOverSupportInHz, keyRegiserInHz, alpha = 2.0):
      pitchOverSupportInSemitones = hz2semitone(pitchOverSupportInHz) - hz2semitone(keyRegiserInHz)
      minFreqInSemitones = np.percentile(pitchOverSupportInSemitones,       alpha)
      maxFreqInSemitones = np.percentile(pitchOverSupportInSemitones, 100 - alpha)
      
      #print('minFreqInSemitones,maxFreqInSemitones',minFreqInSemitones,maxFreqInSemitones)#debug
      return 2*max(abs(minFreqInSemitones),abs(maxFreqInSemitones))
    
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
    

def identifyThreeEssentialPoints(freq,time=None, thld=2):
    #assume data is of increasing order of time
    try:
        t = [time[0],time[-1]]
    except TypeError:
        time = np.linspace(0, 1, len(freq))
        t = [time[0],time[-1]]
    f = [freq[0],freq[-1]]
    k = (np.array(freq)).argmax()
    maximum = freq[k]
 
    if (maximum >= f[0] + thld) and (maximum >= f[-1] + thld):
          t.insert(1,time[k])
          f.insert(1,maximum)
    return t,f

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

# a simple Python 2/3 compatible input()
def input_SLAM(inp):
    vers = sys.version_info.major
    if vers > 2: return input(inp) # Python 3
    else: return raw_input(inp) # Python 2
    
# code taken from https://github.com/vieenrose/tonalizer/blob/master/differential_tone_coding.py
def get_duration(t1_secs, t2_secs) :
      secs = abs(t1_secs - t2_secs)
      days = secs // 86400
      hours = secs // 3600 - days * 24
      minutes = secs // 60 - hours * 60 - days * 60 * 24
      secondes = int(secs) % 60
      return '{:>02.0f}:{:>02.0f}:{:>02.0f}:{:>02d}'.format(days, hours, minutes, secondes)
