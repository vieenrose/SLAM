SLAM+
====

**SLAM+** : **SLAM+** or **SLAMplus** is derived from **SLAM** [4], a language independent software dedicated to the data-driven melodic annotation of speech corpora. New features we introduce in **SLAM+** are twofold:
1) Use **Praat PitchTier** file as data input.
2) Two (instead of one in **SLAM**) stylizations based on respectively a long and a short-term account of intonational register: *global* and *parametrizable local registers*.

Note: 
1. **SLAM+** is compatible with **Python 2 and 3** but optimized only for Linux distributions.
2. **SLAM+** supports **PitchTier** files in binary or short text format as audio input.
3. **SLAM+** integrates a [Python implementaiton](https://gist.github.com/agramfort/850437) of *LOWESS* algorithm [4] for pitch smoothing.  

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
Example of analysis carried out by **SLAM+** on a sample of the [Rhapsodie Spoken French corpus](https://www.projet-rhapsodie.fr/) [3]. In this example, we show a visualization of a pitch contours and its analysis by **SLAM+**. This contours realize the following utterance *'euh on est partis au Portugal complètement'* (Uh, we went to Portugal entirely.) (Rhap-D1003). Analysis is conducted with configuration of *support* and *target* detailed in the following: *support* is chosen to give segmentation on maximal prosodic unit; and *target* is set such that is provided a further segmentaiton of each maximal prosodic unit in marcosyntax [5]. As indicated by *target*'s labels, 'Uh' and 'on est partis au Portugal complètement' are signaled as *N[Assos_N_U]* (discourse marker) and *N* (the nucluer) of an individual speech act, respectively. This example gives a rough idea about how this tool can help to speed up analysis on the prosodic structure of a utterance due to SLAM's automatic categorization of intonaltional contours on its elements, here, macrosyntactic units.

## How to cite **SLAM+**

L. Liu, A. Lacheret-Dujour, N. Obin (2018), *AUTOMATIC MODELLING AND LABELLING OF SPEECH PROSODY: WHAT’S NEW WITH SLAM+ ?* (Manuscript submitted for publication to ICPHS 2019).


## How to install **SLAM+**

### Under Debian / Ubuntu Linux

0) Download or clone [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Install the following libraries required by **SLAM+**:

            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose

### Under Microsoft Windows

0) Download or clone [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Install [Python interpreter](https://www.python.org/downloads/).

2) Install [WinPython](https://winpython.github.io/) which contains Python libarires that SLAMplus requires.

Note: Pay attention to version consistence, ie. make sure that Python interpreter and WinPython you will install are of the same major version (of version 2 or version 3).

## How to Use **SLAM+**
1) Drop your **PitchTier** files and **TextGrid** files in the sub-directory *data* of the corresponding **SLAM+** directory. **PitchTier** files must come in pair of *the same name* with **TextGrid** files. As an example: 

     "myfile1.PitchTier" "myfile1.TextGrid" "myfile2.wav" "myfile2.TextGrid"

2) Open a terminal and go to the **SLAM+** directory
3) Execute

        python SLAMplus.py

4) Follow the instructions.

## How to Configure **SLAM+**
You can open SLAMplus.py and modify the parameters to suit your needs. 

## Bibliography ##

[1] Camacho, A. (2007). [SWIPE: A sawtooth waveform inspired pitch estimator for speech and music](https://www.cise.ufl.edu/~acamacho/publications/dissertation.pdf). Gainesville: University of Florida.

[2] Cleveland, W. S. (1981). LOWESS: A program for smoothing scatterplots by robust locally weighted regression. American Statistician, 35(1), 54.

[3] Lacheret, A., Kahane, S., Beliao, J., Dister, A., Gerdes, K., Goldman, J. P., ... & Tchobanov, A. (2014, May). [Rhapsodie: a prosodic-syntactic treebank for spoken french](https://hal.sorbonne-universite.fr/file/index/docid/968959/filename/LREC2014_AL.pdf). In Language Resources and Evaluation Conference.

[4] N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). [SLAM: Automatic Stylization and Labelling of Speech Melody](https://halshs.archives-ouvertes.fr/hal-00968950). Speech Prosody, 246-250.

[5] Deulofeu, J., Duffort, L., Gerdes, K., Kahane, S., & Pietrandrea, P. (2010, July). [Depends on what the French say spoken corpus annotation with and beyond syntactic functions](https://hal.archives-ouvertes.fr/docs/00/66/51/89/PDF/uppsala.pdf). In Proceedings of the Fourth Linguistic Annotation Workshop (pp. 274-281). Association for Computational Linguistics.
