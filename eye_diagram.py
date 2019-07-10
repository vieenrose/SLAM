import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

fig, ax = plt.subplots()
fig.canvas.set_window_title('Eye diagram for stylized melodic contours by SLAM+')

# definition of an decoder for SLAM+ tonal code
def tonal_dec(code):
	# freq cat. to freq val. mapper
	def cat2freq(y):
		if y == 'L': return -4
		if y == 'l': return -2
		if y == 'm': return  0
		if y == 'h': return  2
		if y == 'H': return  4

	def cat2time(x):
		if x == '1':return 0.1666
		if x == '2':return 0.5
		if x == '3':return 0.8333

	t = []
	f = []

	code = list(code)
	code = code[::-1]

	i    = 0
	while code:
		if i < 2:
			# decode start and final points
			t.append(i)
			y = code.pop()
			f.append(cat2freq(y))
		else:
			# decode frequency and time of peaks / valleys
			y = code.pop()
			t.append(cat2time(code.pop()))
			f.append(cat2freq(y))
			#if f[-1] > f[0] : f[-1] += 2
			#else : f[-1] -= 2
		i+=1

	# sort data according to time axis
	f = [f for _,f in sorted(zip(t,f))]
	t = sorted(t)

	return t,f

# plot global styles on eye diagram
with open('stylesGlo.out') as file:
	for style in file:
		style = style.replace('\n','')
		if style:
			t, s = tonal_dec(style)
			ax.plot(t, s, 'bo-', linewidth=1, alpha=0.01, solid_capstyle="butt")


# time position to normalized time
# '1' -> .167
# '2' -> .500
# '3' -> .833
plt.xlim(0,1)
plt.xlabel('normalized time')
minor_ticks       = [ .167,   .5, .833]
minor_tick_labels = ['1','2','3']
major_ticks = [0,.333,.666,1]
major_tick_labels = ['start','','','end']
ax.xaxis.set_major_locator(ticker.FixedLocator((major_ticks)))
ax.xaxis.set_major_formatter(ticker.FixedFormatter(major_tick_labels))
ax.xaxis.set_minor_locator(ticker.FixedLocator((minor_ticks)))
ax.xaxis.set_minor_formatter(ticker.FixedFormatter(minor_tick_labels))

# frequency code to frequency
# 'H' ->  4
# 'h' ->  2
# 'm' ->  0
# 'l' -> -2
# 'L' -> -4
plt.ylim(-5,5)
plt.ylabel('frequency (log-scale)')
minor_ticks =       [-4,-2,0,2,4]
minor_tick_labels = ['L','l','m','h','H']
major_ticks =       [-5,-3,-1,1,3,5]
major_tick_labels = ['','','','','','']
ax.yaxis.set_major_locator(ticker.FixedLocator((major_ticks)))
ax.yaxis.set_major_formatter(ticker.FixedFormatter(major_tick_labels))
ax.yaxis.set_minor_locator(ticker.FixedLocator((minor_ticks)))
ax.yaxis.set_minor_formatter(ticker.FixedFormatter(minor_tick_labels))

plt.grid(False)
plt.savefig('eye_diagram_glo.png', dpi=1200)
plt.show()
