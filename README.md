SLAM+
====

**SLAM+** : **SLAM+** or **SLAMplus** is derived from **SLAM**, a language independent software dedicated to the data-driven melodic annotation of speech corpora. There are 2 extensions we introduce in **SLAM+**:
1) Support *Pitch* Input, provied in (Binary and Short Text) *Praat PitchTier*  
2) Account for two intonational registers: *global* and *local registers* in stylization. 

Note: ***SLAM+** is optimized only for Linux distributions, compatible with **Python 2 and 3***.

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
*Figure: Visualization of Pitch Contours and its Analysis in **SLAM+***

## How to cite **SLAM+**
N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). SLAM: Automatic Stylization and Labelling of Speech Melody. Speech Prosody, 246-250.

## How to install **SLAM+**
0) Download or clone [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev) and [**swipe-installer**](https://github.com/vieenrose/swipe-installer) and put them in the same repository.

1) Install *Swipe* module (only necessary if you want also to read *WAVE* files in addition to *Praat PitchTier* files)

Swipe, by Kyle Gorman (http://ling.upenn.edu/~kgorman/c/swipe/),  is a pitch estimation algorithm which is required for **SLAM+** to work. 
Sources of swipe are provided in the swipe-installer directory. These are slightly modified versions different from the official github release. Modifications are only for the purpose of *Swipe* compiling under *C89* instead of *C99* standards.
  
2) Install the following libraries required by **SLAM+**:

            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
  
## How to Use **SLAM+**
1) Drop your wav files (or PitchTier files) and textgrid files in the corresponding directories. wav and textgrid files must come in pair of the same name 
     Example: 
     "myfile1.wav" "myfile1.TextGrid" "myfile2.PitchTier" "myfile2.TextGrid"

2) Open a terminal and go to the SLAM directory
3) Execute

        python SLAM.py

4) Follow the instructions.

## How to Configure **SLAM+**
you can open SLAM.py and modify the parameters to suit your needs. 
