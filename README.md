# bids-fmriprep
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) which runs [fMRIprep](http://fmriprep.readthedocs.io) on BIDS-curated data. fmriprep is a functional magnetic resonance imaging (fMRI) data preprocessing pipeline that is designed to provide an easily accessible, state-of-the-art interface that is robust to variations in scan acquisition protocols and that requires minimal user input, while providing easily interpretable and comprehensive error and output reporting. It performs basic processing steps (coregistration, normalization, unwarping, noise component extraction, segmentation, skullstripping etc.) providing outputs that can be easily submitted to a variety of group level analyses, including task-based or resting-state fMRI, graph theory measures, surface or volume-based statistics, etc.

This can run at the 
[project](https://docs.flywheel.io/hc/en-us/articles/360017808354-EM-6-1-x-Release-Notes), 
[subject](https://docs.flywheel.io/hc/en-us/articles/360038261213-Run-an-analysis-gear-on-a-subject) or 
[session](https://docs.flywheel.io/hc/en-us/articles/360015505453-Analysis-Gears) level.
