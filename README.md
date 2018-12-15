SLAMplus
====

SLAMplus : SLAM+ is derived from SLAM, a language independent software dedicated to the data-driven melodic annotation of speech corpora. We discuss two main innovations introduced by SLAM+: (i) the software input has been improved by introducing a step of pitch cleaning; (ii) acoustic processing and annotation have been enriched by taking into account two intonational registers: global and local registers. SLAM+ is optimized only for LINUX distributions, compatible with Python 2/3.

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
*Output of SLAM+ workflow*

How to cite
------------

N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). SLAM: Automatic Stylization and Labelling of Speech Melody. Speech Prosody, 246-250.

How to install
------------

0) Download or clone SLAM and swipe-installer and put them in the same repository.

1) Install SWIPE module (only necessary if you want also to read wav files instead of PitchTier files)

Swipe, by Kyle Gorman (http://ling.upenn.edu/~kgorman/c/swipe/),  is a pitch estimation algorithm which is required for SLAM to work. 
Sources of swipe are provided in the swipe-installer directory. These are slightly modified versions different from the official github release. Modifications are only for the purpose of swipe compiling under C89 instead of C99 standards.
  
2) Install the following libraries required by SLAM:

            
            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
  
How to use
------------

1) Drop your wav files (or PitchTier files) and textgrid files in the corresponding directories. wav and textgrid files must come in pair of the same name 
     example:
     "myfile1.wav" "myfile1.TextGrid" "myfile2.PitchTier" "myfile2.TextGrid"

2) Open a terminal and go to the SLAM directory
3) Execute

        python SLAM.py

4) Follow the instructions.

How to configure
------------

you can open SLAM.py and modify the parameters to suit your needs. 


