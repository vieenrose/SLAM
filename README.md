SLAM+
====

## Authors ##
- [*Luigi (Yu-Cheng) Liu*](mailto:luigi.plurital@gmail.com), Modyco, Université Paris Ouest Nanterre & CNRS
- [*Anne Lacheret-Dujour*](mailto:anne@lacheret.com), Modyco, Université Paris Ouest Nanterre & CNRS
- [*Nicolas Obin*](mailto:nicolas.obin@ircam.fr), IRCAM, UMR STMS IRCAM-CNRS-UPMC, Paris

## What's **SLAM+** ?

### Overview ###


**SLAM+** : **SLAM+** or **SLAMplus** is derived from **SLAM** [4], a data-driven language independent software for pitch (contour) annotation of speech corpora. It integrates an algorithm for the automatic stylization and labelling of melodic contours, developed to process intonation. This algorithm is characterized with three basic peculiarities: 

the method is based on the bottom-up genneration of the contours : 
1) Stylized melodic contours are directly derived from a manually (denoised) cleaned speech signal.
2) Melodic contours, simple or complex, are described through a simple time-frequency representation. 
3) Melodic contours are used to describe various linguistic units as specified by users. 
4) the variation concerns 
	i) the nature (pragmatics, syntactic, phonologic) of the unit and
	ii) the size of the unit (from the syllable to larger prosodic and syntactic units)
5) the melodic contours are automatically represented with a vocabulary of tonal labels (L,l,m,h,H)  

with 2 features newly added in **SLAM+** 

6) Use **Praat PitchTier** file along with **TextGrid** file as data input.
7) Two (instead of one in **SLAM**) stylizations are produced: there are respectively based on a long and a short-term account of intonational register: *global* and *parametrizable local registers*.

Note: 
- **SLAM+** is compatible with **Python 2 and 3** but optimized only for Linux distributions.
- **SLAM+** supports **PitchTier** files in binary or short text format as audio input.
- **SLAM+** integrates a [Python implementaiton](https://gist.github.com/agramfort/850437) of *LOWESS* algorithm [4] for pitch smoothing.  

### Illustration ###

We show, in the figure below, a visualization of pitch contours and their analysis by **SLAM+**. These contours realize the following utterance *'euh on est partis au Portugal complètement'* (Uh, we went to Portugal entirely.) (Rhap-D1003). Analysis is conducted with configuration of *support* and *target* detailed in the following: *support* is the temporal interval uxed to compute the global register of the targets. *target* is the temporal interval to which a melodic contour is computed. As indicated by *target*'s labels, *'euh'* and *'on est partis au Portugal complètement'* are signaled respectively as *N[Assos_N_U]* (discourse marker) and *N* (the nucluer) of a speech act. 

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
Fig 1. Example of analysis carried out by **SLAM+** on a sample of the [Rhapsodie Spoken French corpus](https://www.projet-rhapsodie.fr/) [3]. 

## Installation ##

### Under Debian / Ubuntu Linux ###

0) Download or clone [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Install the following libraries required by **SLAM+**:

            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose

### Under Microsoft Windows ###

0) Download [**SLAMplus**](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Choose a full version of [WinPython](https://winpython.github.io/) and download it.

2) Then put the decompressed content of **SLAMplus** in the sub-directory of WinPython where *python.exe* is 

## How to Launch it ##
1) Drop your **PitchTier** files and **TextGrid** files in the sub-directory *data* of the corresponding **SLAM+** directory. **PitchTier** files must come in pair of *the same name* with **TextGrid** files. As an example: 

     "myfile1.PitchTier" "myfile1.TextGrid" "myfile2.wav" "myfile2.TextGrid"

2) Open a terminal and go to the **SLAM+** directory
3) Execute

for Linux

        python SLAMplus.py
for Windows

        python.exe SLAMplus.py
4) Follow the instructions.

## How to Configure it ##
Configuration of SLAM+ to suit your work:

1) Open the SLAMplus.py in the SLAM+ working folder with text editor (recommaded 'notepad++')

2) Edit the values of SpeakerTier, TargetTier and TagTier. 

Note: These values as stated here are different tiers specified in the concerned TextGrid files. SupportTier (as valued in this work) is defined as the tier name where the largest units of register estimation are delimited. TargetTier is defined as the tier name where units of stylization are bounded. TagTier provides additional descriptive information of the contents. It is used to compare and ascertain the details of SpeakerTier and TargetTier.

### Examples of Configuration ###

For the examples (NaijaSynCor project: JOS_01_V___MDT) in the following, we use the same TextGrid file which provides 4 annotation tiers. These tiers are 
- Syllabes (Syl)
- Prosodic Word (PrWd) 
- Prosodic Phrase (PP) 
- Large Prosodic Unit (LPU). 

Note that only the targetTier varies in these exemples while SupportTier and TagTier are fixed as LPU and PrWd, respectively. 

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Example_TextGrid.png)
Fig 2. Input TextGrid file used in examples

#### 1. Syllabes as target ####

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Config_I.png)
Fig 3. Configuration for Syllabes (Syl) as target 


![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Output_I.png)
Fig 4. Analysis Result

#### 2. Prosodic Phrase as target ####

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Config_II.png)
Fig 5. Configuration for Prosodic Phrase (PP) as target


![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Output_II.png)
Fig 6. Analysis Result

## How to cite us ##

L. Liu, A. Lacheret-Dujour, N. Obin (2019), AUTOMATIC MODELLING AND LABELLING OF SPEECH PROSODY: WHAT’S NEW WITH SLAM+ ?. In *ICPhS* (to appear).

## Bibliography ##

[1] Camacho, A. (2007). [SWIPE: A sawtooth waveform inspired pitch estimator for speech and music](https://www.cise.ufl.edu/~acamacho/publications/dissertation.pdf). Gainesville: University of Florida.

[2] Cleveland, W. S. (1981). LOWESS: A program for smoothing scatterplots by robust locally weighted regression. American Statistician, 35(1), 54.

[3] Lacheret, A., Kahane, S., Beliao, J., Dister, A., Gerdes, K., Goldman, J. P., ... & Tchobanov, A. (2014, May). [Rhapsodie: a prosodic-syntactic treebank for spoken french](https://hal.sorbonne-universite.fr/file/index/docid/968959/filename/LREC2014_AL.pdf). In Language Resources and Evaluation Conference.

[4] N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). [SLAM: Automatic Stylization and Labelling of Speech Melody](https://halshs.archives-ouvertes.fr/hal-00968950). Speech Prosody, 246-250.

[5] Deulofeu, J., Duffort, L., Gerdes, K., Kahane, S., & Pietrandrea, P. (2010, July). [Depends on what the French say spoken corpus annotation with and beyond syntactic functions](https://hal.archives-ouvertes.fr/docs/00/66/51/89/PDF/uppsala.pdf). In Proceedings of the Fourth Linguistic Annotation Workshop (pp. 274-281). Association for Computational Linguistics.

[6] Oyelere S. Abiola, Candide Simard and Anne Lacheret (2018). Prominence in the Identification of Focussed Elements in Naija. In Workshop on the Processing of Prosody across Languages and Varieties (Proslang). 

## Todo ##
- Add support .or file generated by Analor
