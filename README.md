SLAM+
====

**SLAM+** : **SLAM+** or **SLAMplus** is derived from **SLAM** [4], a language independent software dedicated to the data-driven melodic annotation of speech corpora. New features we introduce in **SLAM+** are twofold:
1) New support for **Praat PitchTier** file (in addition to **WAVE** file) as audio input.
2) Two (instead of one in **SLAM**) stylizations based on respectively a long and a short-term account of intonational register: *global* and *parametrizable local registers*.

Note: 
1. **SLAM+** is compatible with **Python 2 and 3** but optimized only for Linux distributions.
2. **SLAM+** supports **mono-channel WAVE** and **PitchTier** files in binary or short text format as audio input.
3. **SLAM+** integrates a [Python implementaiton](https://gist.github.com/agramfort/850437) of *LOWESS* algorithm [4] for pitch smoothing.  

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
Example of visualization of pitch contours analysis on *'euh on est partis au Portugal complètement'* (Uh, we went to Portugal entirely.) (Rhap-D1003) from [Rhapsodie Treebank](https://www.projet-rhapsodie.fr/) [3]

## How to cite **SLAM+**

L. Liu, A. Lacheret, N. Obin (2018), *AUTOMATIC MODELLING AND LABELLING OF SPEECH PROSODY: WHAT’S NEW WITH SLAM+ ?* (Manuscript submitted for publication).



## How to install **SLAM+**
0) Download or clone [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev) and [**swipe-installer**](https://github.com/vieenrose/swipe-installer) and put them in the same repository.

1) Install *Swipe* module (only necessary if you want also to read **WAVE** files in addition to **PitchTier** files)

Implemented by Kyle Gorman, [Swipe](http://ling.upenn.edu/~kgorman/c/swipe/) is a pitch estimation algorithm [1], which is required for **SLAM+** to work with **WAVE** files. Sources of swipe are provided in the swipe-installer directory. These are **slightly modified versions** different from the official *GitHub* release. Modifications are only for the purpose of *Swipe* compiling under *C89* instead of *C99* standards.
  
2) Install the following libraries required by **SLAM+**:

            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
  
## How to Use **SLAM+**
1) Drop your **mono-channel WAVE** (or **PitchTier**) files and **TextGrid** files in the sub-directory *data* of the corresponding **SLAM** directory. **WAVE** (or **PitchTier**) files must come in pair of *the same name* with **TextGrid** files. As an example: 

     "myfile1.PitchTier" "myfile1.TextGrid" "myfile2.wav" "myfile2.TextGrid"

2) Open a terminal and go to the **SLAM** directory
3) Execute

        python SLAM.py

4) Follow the instructions.

## How to Configure **SLAM+**
You can open SLAM.py and modify the parameters to suit your needs. 

## Bibliography ##

[1] Camacho, A. (2007). [SWIPE: A sawtooth waveform inspired pitch estimator for speech and music](https://www.cise.ufl.edu/~acamacho/publications/dissertation.pdf). Gainesville: University of Florida.

[2] Cleveland, W. S. (1981). LOWESS: A program for smoothing scatterplots by robust locally weighted regression. American Statistician, 35(1), 54.

[3] Lacheret, A., Kahane, S., Beliao, J., Dister, A., Gerdes, K., Goldman, J. P., ... & Tchobanov, A. (2014, May). [Rhapsodie: a prosodic-syntactic treebank for spoken french](https://hal.sorbonne-universite.fr/file/index/docid/968959/filename/LREC2014_AL.pdf). In Language Resources and Evaluation Conference.

[4] N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). [*SLAM: Automatic Stylization and Labelling of Speech Melody*](https://halshs.archives-ouvertes.fr/hal-00968950). Speech Prosody, 246-250.
