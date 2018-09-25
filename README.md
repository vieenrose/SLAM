SLAM
====

SLAM : a method for the automatic Stylization and LAbelling of speech Melody (optimized only for LINUX distributions)

How to cite:
------------

N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). SLAM: Automatic Stylization and Labelling of Speech Melody. Speech Prosody, 246-250.

How to install
------------

0) Download or clone SLAM and swipe-installer and put them in the same repository.

1) Install SWIPE module

Swipe, by Kyle Gorman (http://ling.upenn.edu/~kgorman/c/swipe/),  is a pitch estimation algorithm which is required for SLAM to work. 
Sources of swipe are provided in the swipe-installer directory. These are slightly modified versions different from the official github release. Modifications are only for the purpose of swipe compiling under C89 instead of C99 standards.
  
2) Install the following libraries required by SLAM:

    make 
    sudo apt-get install liblibblas-dev liblapack-dev libfftw3-dev libsndfile1-dev swig
   sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
  
How to use
------------

1) drop your wav files and textgrid files in the corresponding directories. wav and textgrid files must come in pair of the same name 
     example:
     "myfile1.wav" "myfile1.TextGrid" "myfile2.wav" "myfile2.TextGrid"

2) open a terminal and go to the SLAM directory
3) type "python SLAM.py"
4) follow the instructions.

How to configure
------------

you can open SLAM.py and modify the parameters to suit your needs. 


