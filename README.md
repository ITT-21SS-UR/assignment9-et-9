% Interaction Technology and Techniques
  Assignment 9: Gesture Recognition
% Summer semester 2019
% **Submission due: Wednesday, 30. June 2021, 23:55**

**Hand in in groups of max. two.**

Your task is to distinguish different symbols/gestures drawn on a canvas

9.1: \$1 Gesture Recognizer
============================

Implement a Python application that allows the user to record a set of different symbols/gesture drawn with the mouse (e.g., numbers, polygons and distinguish between them using \$1 Gesture Recognizer.

Specifically, implement the following:

* a graphical user interface where the user can add new gestures/symbols to be recognized (e.g., via the QDrawWidget)
* individual processing steps as described in the paper on the \$1 Gesture Recognizer[^dollarone].
* a mode where the user can draw one of the gestures/symbols and the system recognizes it.
* optional but nice: associate certain actions with different gestures (e.g., start/stop audio, launch applications (have a look at the `sh` Python module).
* implement this functionality for the mouse first
* optional but helpful: allow the user to remove and retrain gestures.

Experiment with different sets of gestures/symbols and find a few that can be distinguished well.

[^dollarone]: Wobbrock, J.O., Wilson, A.D. and Li, Y. (2007). **[Gestures without libraries, toolkits or training: A $1 recognizer for user interface prototypes.](http://faculty.washington.edu/wobbrock/pubs/uist-07.01.pdf)** Proceedings of the ACM Symposium on User Interface Software and Technology (UIST '07). Newport, Rhode Island (October 7-10, 2007). New York: ACM Press, pp. 159-168., see also <https://depts.washington.edu/aimgroup/proj/dollar/>

Points
------------

* **4** The script correctly implements the features above
* **3** The script accurately detects 3 different gestures.
* **2** The script is well documented and the script is well-structured, follows the Python style guide (PEP 8) and contains workload distribution of the team members.


9.2: Read up on Gesture Recognition
======================================================

Read the paper on the [*\$P Point-Cloud Recognizer*](http://faculty.washington.edu/wobbrock/pubs/icmi-12.pdf).

Concisely answer the following questions:

* What does the recognizer do?
* Name an advantage of the *\$P* recognizer over the *\$1* recognizer.
* What is the *minimum matching distance*?

Hand in the following file:

**gesture-recognizer.txt**: a plain-text file containing your answers


Points
------------

* **2** Good answer to first question 
* **2** Good answer to second question 
* **2** Good answer to third question 



Submission 
=========================================
Submit via GRIPS until the deadline

All files should use UTF-8 encoding and Unix line breaks.
Python files should use spaces instead of tabs.

                                                               Have Fun!
