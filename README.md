SLAM+
====

An enhanced automatic stylizer for pitch (contour) of speech corpora based on [*SLAM*](https://github.com/jbeliao/SLAM).

## Contributors ##
- `Luigi (Yu-Cheng) Liu` - [luigi.plurital@gmail.com](mailto:luigi.plurital@gmail.com)
- `Anne Lacheret-Dujour` - [anne@lacheret.com](mailto:anne@lacheret.com)
	- [UMR 7114 MoDyCo Lab.](https://www.modyco.fr/fr/) [(University Paris Nanterre)](https://university.parisnanterre.fr/)
- `Nicolas Obin` - [nicolas.obin@ircam.fr](mailto:nicolas.obin@ircam.fr)
	- [Ircam](https://www.ircam.fr/)
- `Julie Belião`

## What's *SLAM+*?

### Overview ###


*SLAM+* : *SLAM+* is a software derived from *SLAM* [4].  *SLAM* is a data-driven language independent software for pitch (contour) annotation of speech corpora. It integrates an algorithm for the automatic stylization and labelling of melodic contours, developed to process intonation. *SLAM* method is based on the bottom-up generation of the contours. The underlying algorithm can be highlighted with the following features: 
 
1) Model-agnostic Approach: 
	- Stylized melodic contours are directly derived from a manually cleaned (denoised) pitch signal.
2) Time-Frequence Representation: 
	- Melodic contours, simple or complex, are described through a simple time-frequency representation. 
	- The melodic contours are automatically represented with a vocabulary of tonal labels `L`,`l`,`m`,`h`,`H` 
3) User-defined Linguistic Units:
	- Melodic contours are used to describe various linguistic units as specified by users. 
	- The linguistic variation concerns 
		- The nature (pragmatics, syntactic, phonologic) of the unit
		- The size of the unit (from the syllable to larger prosodic and syntactic units)

Two enhanced features are added in *SLAM+*

4) Support source data 
	- a pair of 
		- `Praat PitchTier` (binary or short text) file (`.PitchTier`)
		- Associated `Praat TextGrid` file (`.TextGrid`)
	- `Praat Collection` file in binary format (`.Collection`)
	- `Analor JavaObj` file (`.or`)
5) Generate a double stylization based on: 
	- *Global register* (calculated on classic account of intonational register)
	- *Parametrizable local register* (computed on a short-term account of intonational register)


### Illustration ###

We show, in the figure below, a visualization of pitch contours and their analysis by *SLAM+*. These contours realize the following utterance *'euh on est partis au Portugal complètement'* (Uh, we went to Portugal entirely.) (Rhap-D1003). Analysis is conducted with configuration of `support` and `target` detailed in the following: `support` is the temporal interval uxed to compute the global register of the targets. *target* is the temporal interval to which a melodic contour is computed. As indicated by *target*'s labels, *'euh'* and *'on est partis au Portugal complètement'* are signaled respectively as `N[Assos_N_U]` (discourse marker) and `N` (the nucluer) of a speech act. 

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Rhap-D2001.png)
Fig 1. Example of analysis carried out by *SLAM+* on a sample of the [Rhapsodie Spoken French corpus](https://www.projet-rhapsodie.fr/) [3]. 

## Installation ##

### Under MacOS ###

0) Install Python3 under MacOS. For more information, users are refered to [this installation guide](https://docs.python-guide.org/starting/install3/osx/) which we find very helpful.

1) Download or clone [*SLAMplus*](https://github.com/vieenrose/SLAMplus/tree/dev).

2) Install the following libraries required by *SLAM+* via pip3:

            sudo pip3 install numpy scipy matplotlib pandas sympy nose chardet

### Under Debian / Ubuntu Linux ###

0) Download or clone [*SLAMplus*](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Install the following libraries required by *SLAM+*:

            sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose

### Under Microsoft Windows ###

0) Download [*SLAMplus*](https://github.com/vieenrose/SLAMplus/tree/dev).

1) Choose a full version of [WinPython](https://winpython.github.io/) and download it.

2) Then put the decompressed content of `SLAMplus` in the sub-directory of WinPython where `python.exe` is 

## How to Launch SLAM+ ##
1) Drop your `PitchTier` files and `TextGrid` files in the sub-directory `data` of the corresponding `SLAMplus` directory. `PitchTier` files must come in pair of *the same name* with `TextGrid` files. As an example: 

     `myfile1.PitchTier` `myfile1.TextGrid` `myfile2.wav` `myfile2.TextGrid`

2) Open a terminal and go to the `SLAMplus` directory
3) Execute

for Linux

        python SLAMplus.py
for Windows

        python.exe SLAMplus.py
4) Follow the instructions.

## How to Configure SLAM+ ##
Configuration of SLAM+ to suit your work:

1) Open the `SLAMplus.py` in the `SLAMplus` working folder with text editor (recommaded 'notepad++')

2) Edit the values of `SpeakerTier`, `TargetTier` and `TagTier`. 

Note: These values as stated here are different tiers specified in the concerned `TextGrid` files. `SupportTier` (as valued in this work) is defined as the tier name where the largest units of register estimation are delimited. `TargetTier` is defined as the tier name where units of stylization are bounded. `TagTier` provides additional descriptive information of the contents. It is used to compare and ascertain the details of `SpeakerTier` and `TargetTier`.

### Examples of Configuration ###

For the examples (NaijaSynCor project: JOS_01_V___MDT) in the following, we use the same `TextGrid` file which provides 4 annotation tiers. These tiers are 
- Syllabes (`Syl`)
- Prosodic Word (`PrWd`) 
- Prosodic Phrase (`PP`)
- Large Prosodic Unit (`LPU`) 

Note that only the `targetTie` varies in these exemples while `SupportTier` and `TagTier` are fixed as `LPU` and `PrWd`, respectively. 

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Example_TextGrid.png)
Fig 2. Input TextGrid file used in examples

#### 1. Syllabes as target ####

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Config_I.png)
Fig 3. Configuration for Syllabes (Syl) as target 


![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Output_I.png)
Fig 4. A sample of analysis Result

#### 2. Prosodic Phrase as target ####

![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Config_II.png)
Fig 5. Configuration for Prosodic Phrase (PP) as target


![alt text](https://github.com/vieenrose/SLAMplus/blob/dev/img/Output_II.png)
Fig 6. A sample of Analysis Result

## Citation ##

L. Liu, A. Lacheret-Dujour, N. Obin (2019), [AUTOMATIC MODELLING AND LABELLING OF SPEECH PROSODY: WHAT’S NEW WITH SLAM+ ?](https://www.researchgate.net/publication/332108118_Automatic_Modelling_and_Labelling_of_Speech_Prosody_What's_New_with_SLAM). In *ICPhS* (to appear).

## References ##

[1] Camacho, A. (2007). [SWIPE: A sawtooth waveform inspired pitch estimator for speech and music](https://www.cise.ufl.edu/~acamacho/publications/dissertation.pdf). Gainesville: University of Florida.

[2] Cleveland, W. S. (1981). LOWESS: A program for smoothing scatterplots by robust locally weighted regression. American Statistician, 35(1), 54.

[3] Lacheret, A., Kahane, S., Beliao, J., Dister, A., Gerdes, K., Goldman, J. P., ... & Tchobanov, A. (2014, May). [Rhapsodie: a prosodic-syntactic treebank for spoken french](https://hal.sorbonne-universite.fr/file/index/docid/968959/filename/LREC2014_AL.pdf). In Language Resources and Evaluation Conference.

[4] N. Obin,  J. Beliao, C., Veaux, A. Lacheret (2014). [SLAM: Automatic Stylization and Labelling of Speech Melody](https://halshs.archives-ouvertes.fr/hal-00968950). Speech Prosody, 246-250.

[5] Deulofeu, J., Duffort, L., Gerdes, K., Kahane, S., & Pietrandrea, P. (2010, July). [Depends on what the French say spoken corpus annotation with and beyond syntactic functions](https://hal.archives-ouvertes.fr/docs/00/66/51/89/PDF/uppsala.pdf). In Proceedings of the Fourth Linguistic Annotation Workshop (pp. 274-281). Association for Computational Linguistics.

[6] Oyelere S. Abiola, Candide Simard and Anne Lacheret (2018). Prominence in the Identification of Focussed Elements in Naija. In Workshop on the Processing of Prosody across Languages and Varieties (Proslang). 

