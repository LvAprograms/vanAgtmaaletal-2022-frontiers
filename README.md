## vanAgtmaaletal2022
Compiled source for reference model and post-processing scripts plus force quantification data for van Agtmaal et al., 2022 submitted to Frontiers in Earth Science. 

# scripts
Collection of python scripts used to make figures for the paper.
Also contains ForceAnalysis.m, which is the main Matlab visualisation script for the models. It reads .hdf5 model output files as input.

* ForceCalculator.py - class which is inherited by GPE.py. Is able to plot topography, read marker data, etc.
* GPE.py - class inheriting from ForceCalculator. Calculates gravitational potential energy difference between two columns of rocks. Not used in current manuscript
* oceantemp.py - cooling halfspace model temperature visualisation
* slabdetachment.py - plots a dataset of detachment depths versus durations.
* GradualTransition.py - Calculates necessary node x or y coordinates to implement a gradual transition from one grid spacing to one another. Could use some automation.
* plot_dragdata.py - plots output of viscous drag calculations (from matlab script ForceAnalysis.m, can't publish here unfortunately)
* plot_slabpull.py - plots output of slab pull calcuations (from matlab script ForceAnalysis.m)
* PTt.py - program for parsing PTt.log files generated during or after model runs to compose PTt paths.  
* minor_plots.py - just some convenience plotting script. 

# force data
With the option "Slab_pull" and "Drag" in post_processing/ForceAnalysis.m, we produced the raw force output used to make the force quantification figures.
The names are the systematic old names. The list below shows the names used in our manuscript. The models reflong, thineur, ref5cm, reffree, refcold( -er, -est) are also included. 
* ER(_rerun) -> ref
* FI(_rerun) -> oc510
* FJ(_rerun) -> oc410
* FK(_rerun) -> oc310
* FP(_rerun) -> peierls
* FQ(_rerun) -> LM25
* FR(_rerun) -> LM50
* FS(_rerun) -> LM75
* FT(_rerun) -> LMoc510
* FX(_rerun) -> slowref

# PTt data
The high-resolution PTt data is stored in text files *PTt.log with the same naming as the force data files. 
For models such as peierls and slowref, we had to extract the PTt data after the model run finished.
The PTt data files are too big for this repository. Please email me at luuk.vanagtmaal@erdw.ethz.ch 
