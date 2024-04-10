# bids-fmriprep
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) which runs [fMRIPrep](http://fmriprep.readthedocs.io) Long-Term Support version 23.0.1 (Mar 24, 2023) on BIDS-curated data. fMRIPrep is a functional magnetic resonance imaging (fMRI) data preprocessing pipeline that is designed to provide an easily accessible, state-of-the-art interface that is robust to variations in scan acquisition protocols and that requires minimal user input, while providing easily interpretable and comprehensive error and output reporting. It performs basic processing steps (coregistration, normalization, unwarping, noise component extraction, segmentation, skull stripping, etc.) providing outputs that can be easily submitted to a variety of group level analyses, including task-based or resting-state fMRI, graph theory measures, surface or volume-based statistics, etc.

The version number is (Flywheel gear) MAJOR . MINOR . PATCH _ (algorithm) YY . MINOR . PATCH

The "main" branch of this repository is for the Long Term Support version of fMRIPrep. Other branches support
more recent versions of fMRIPrep such as 21.x.x-23.x.x.

## Overview
This gear can only be run on datasets that have been BIDS curated and can pass the tests of the [BIDS Validator](https://github.com/bids-standard/bids-validator).  fMRIPrep requires that your dataset include at least one T1w structural image.  It can include multiple T1 images, a T2 image and some number of BOLD series. This data must have its DICOMS classified with our classifier gear, and converted to nifti files with our dcm2niix gear, in that order.  There are additional requirements as described under "Troubleshooting" below.

This Gear requires a (free) Freesurfer license. The license can be provided to the Gear in 3 ways. See [How to include a Freesurfer license file](https://docs.flywheel.io/User_Guides/user_freesurfer_license_file_to_run_a_freesurfer_or_fmriprep_gear/).

The bids-fmriprep Gear can run at the project, subject or session level.  Because files are in the BIDS format, all the proper files will be used for the given session, subject, or separately, by subject, for the whole project.

## Setup:
Before running BIDS curation on your data, you must first prepare your data with the following steps:
1. Run the [SciTran: DICOM MR Classifier](https://github.com/scitran-apps/dicom-mr-classifier) gear on all the acquisitions in your dataset
    * This step extracts the DICOM header info, and store it as Flywheel Metadata.
1. Run the [DCM2NIIX: dcm2nii DICOM to NIfTI converter](https://github.com/flywheel-apps/dcm2niix) gear on all the acquisitions in your dataset
    * This step generates the Nifti files that fMRIPrep needs from the DICOMS.  It also copies all flywheel metadata from the DICOM to the Nifti file (In this case, all the DICOM header information we extracted in step 1)
1. Run the [curate-bids gear](https://github.com/flywheel-apps/curate-bids) on the project.  More information about BIDS Curation on Flywheel can be found [here](https://docs.flywheel.io/hc/en-us/articles/360008162154-BIDS-Overview) and running the BIDS curation gear is described [here](https://docs.flywheel.io/hc/en-us/articles/360009218434-BIDS-Curation-Gear).  If you need to rename sessions or subjects before curation, you may find the gear helpful: [bids-pre-curate](https://github.com/flywheel-apps/bids-pre-curate).

1. Run fMRIPrep on a session, subject, or project.

Steps 1 and 2 can be automatically carried out as [gear rules](https://docs.flywheel.io/hc/en-us/articles/360008553133-Project-Gear-Rules).

These steps MUST be done in this order.  Nifti file headers have significantly fewer fields than the DICOM headers.  File metadata will be written to .json sidecars when the files are exported in the BIDS format as expected by the fMRIPrep BIDS App which is run by this gear.

## Running:
To run the gear, select a [project](https://docs.flywheel.io/hc/en-us/articles/360017808354-EM-6-1-x-Release-Notes),  [subject](https://docs.flywheel.io/hc/en-us/articles/360038261213-Run-an-analysis-gear-on-a-subject) or [session](https://docs.flywheel.io/hc/en-us/articles/360015505453-Analysis-Gears).

Instead of running at the project level which will sequentially step through each subject, you can launch multiple bids-fmriprep jobs on subjects or sessions in parallel.  An example of running bids-fmriprep on a subject using the Flywheel SDK is in this [notebook](notebooks/run-bids-fmriprep.ipynb).  More details about running gears using the SDK can be found in this [tutorial](https://gitlab.com/flywheel-io/public/flywheel-tutorials/-/blob/ad392d26131ef22408423b5a5c14104253d53cd6/python/batch-run-gears.ipynb).

Note that bids-fmriprep can take a *long* time to run because it runs Freesurfer.  Depending on the number of structural and functional files, it can run for 12 to 48 or more hours.

## Inputs

Because the project has been BIDS curated, all the proper T1, T2, and fMRI files will be automatically found.

### bidsignore (optional)
A list of patterns (like .gitignore syntax) defining files that should be ignored by the
bids validator.

### bids-filter-file (optional)

A JSON file describing custom BIDS input filters using PyBIDS.  [See here](https://fmriprep.org/en/20.2.6/faq.html#how-do-i-select-only-certain-files-to-be-input-to-fmriprep) for details.  Recommendation: start with the default and edit it to be like the example shown there.  This does the opposite of what providing a bidsignore file does: it only keeps what matches the filters.

### freesurfer_license (optional)
Your FreeSurfer license file. [Obtaining a license is free](https://surfer.nmr.mgh.harvard.edu/registration.html).
This file will be copied into the $FSHOME directory.  There are [three ways](https://docs.flywheel.io/hc/en-us/articles/360013235453-How-to-include-a-Freesurfer-license-file-in-order-to-run-the-fMRIPrep-gear-)
to provide the license to this gear.  A license is required for this gear to run.

### fs-subjects-dir (optional)
Zip file of existing FreeSurfer subject's directory to reuse.  If the output of FreeSurfer recon-all is provided to fMRIPrep, that output will be used rather than re-running recon-all.  Unzipping the file should produce a particular subject's directory which will be placed in the $FREESURFER_HOME/subjects directory.  The name of the directory must match the -subjid as passed to recon-all.  This version of fMRIPrep uses Freesurfer v6.0.1.

### previous-results (optional)
Provide previously calculated fMRIPrep output results zip file as in input.  This file will be unzipped into the output directory so that previous results will be used instead of re-calculating them.  This input is provided so that bids-fmriprep can be run incrementally as new data is acquired.

## Config:
Most config options are identical to those used in fmriprep, and so documentation can be found here https://fmriprep.org/en/20.2.6/usage.html.

The following additional arguments control how the gear code behaves.
Note: arguments that start with "gear-" are not passed to fMRIPrep.

### gear-run-bids-validation (optional)
Gear argument: Run bids-validator after downloading BIDS formatted data.  Default is false.

### gear-log-level (optional)
Gear argument: Gear Log verbosity level (ERROR|WARNING|INFO|DEBUG)

### gear-log-to-file (optional)
Gear argument: Instead of logging in real time, save log output of fMRIPrep to the file output/log#.txt (where # is 1 or 2 depending on how many times fMRIPrep was run).

### gear-save-intermediate-output (optional)
Gear argument: The BIDS App is run in a "work/" directory.  Setting this will save ALL
contents of that directory including downloaded BIDS data.  The file will be named
"<BIDS App>_work_<run label>_<analysis id>.zip"

### gear-intermediate-files (optional)
Gear argument: A space separated list of FILES to retain from the intermediate work
directory.  Files are saved into "<BIDS App>_work_selected_<run label>_<analysis id>.zip"

### gear-intermediate-folders (optional)
Gear argument: A space separated list of FOLDERS to retain from the intermediate work
directory.  Files are saved into "<BIDS App>_work_selected_<run label>_<analysis id>.zip"

### gear-save-output-as-subfolders (optional)
Gear argument: Instead of a single zipped file with fMRIPrep and Freesurfer output in it, the gear will save each separately.

### gear-dry-run (optional)
Gear argument: Do everything except actually executing the BIDS App.

### gear-keep-fsaverage (optional)
Keep freesurfer/fsaverage* directories in output.  These are copied from the freesurfer installation.  Default is to delete them.

### gear-FREESURFER_LICENSE (optional)
Gear argument: Text from license file generated during FreeSurfer registration.
Copy the contents of the license file and paste it into this argument.

### gear-writable-dir (optional)
Gear argument: Gears expect to be able to write temporary files in /flywheel/v0/.  If this location is not writable (such as when running in Singularity), this path will be used instead.  fMRIPrep creates a large number of files so this disk space should be fast and local.",

## Troubleshooting

### Resources

fMRIPrep can require a large amount of memory and disk space depending on the number of acquisitions being analyzed.  There is also a trade-off between the cost of analysis and the amount of time necessary.
There is a helpful discussion of this in the [FAQ](https://fmriprep.org/en/20.2.6/faq.html#how-much-cpu-time-and-ram-should-i-allocate-for-a-typical-fmriprep-run) and also on [NeuroStars](https://neurostars.org/t/how-much-ram-cpus-is-reasonable-to-run-pipelines-like-fmriprep/1086).  At the top of your job log, you should see the configuration of the virtual machine you are running on.  When a job finishes, the output of the GNU `time` command is placed into the "Custom Information" (metadata) on the analysis.  To see it, go to the "Analyses" tab for a project, subject, or session, click on an analysis and then on the "Custom Information" tab.

### Metadata

Depending upon your fMRIPrep workflow preferences, a variety of metadata and files may be required for successful execution. And because of this variation, not all cases will be caught during BIDS validation. If you are running into issues executing bids-fmriprep, we recommend reading through the configuration options explained with the [fMRIPrep Usage Notes](https://fmriprep.org/en/stable/usage.html) and double-checking the following:

#### Fieldmaps ([BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#fieldmap-data))

- Phase encoding directions for fieldmaps and bold must be opposite.
    - Look for the `PhaseEncodingDirection` key in the file metadata (or exported JSON sidecar) and note the value (e.g., `j-`). If the fieldmap and the bold series it is `IntendedFor` do not have opposite `PhaseEncodingDirection`, fMRIPrep will error out with "ValueError: None of the discovered fieldmaps has the right phase encoding direction." BIDS specification details can be found [here](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#case-4-multiple-phase-encoded-directions-pepolar). For more information see discussions [here](https://github.com/nipreps/fmriprep/issues/1148#issuecomment-392363308) and [here](https://neurostars.org/t/phase-encoding-error-for-field-maps/2650).
    - To fix this, you can either write in "fieldmaps" into the "ignore" configuration option for the bids-fmriprep Gear, which will ignore using fieldmaps during the fMRIPrep workflow, or if you collected your data with opposite phase encodings, you can update the values for the `PhaseEncodingDirection` key as appropriate.

- `IntendedFor` field needs to point to an existing file.
	- There are two places where the `IntendedFor` file metadata is required for bids-fmriprep.
	- The structure of the metadata in Flywheel should be similar to the following:

```json
{
   "BIDS":{
      "Acq":"",
      "Dir":"",
      "error_message":"",
      "Filename":"sub-123_ses-01_fieldmap.nii.gz",
      "Folder":"fmap",
      "ignore":false,
      "IntendedFor":[
         {
            "Folder":"func"
         }
      ],
      "Modality":"fieldmap",
      "Path":"sub-123/ses-01/fmap",
      "Run":"",
      "template":"fieldmap_file",
      "valid":true
   },
   "IntendedFor":[
      "ses-01/func/sub-123_ses-01_task-stroop_run-02_bold.nii.gz",
      "ses-01/func/sub-123_ses-01_task-stroop_run-01_bold.nii.gz"
   ],
   "PhaseEncodingDirection":"j-",
   "TotalReadoutTime":0.123
}
```

- Note: `PhaseEncodingDirection` and `TotalReadoutTime` are typically required.

#### Functional ([BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data))

- Each functional NIfTI needs the following metadata: `EchoTime`, `EffectiveEchoSpacing`, `PhaseEncodingDirection`,`RepetitionTime`, `SliceTiming`, and `TaskName`.

## Development Notes

### Omitted fMRIPrep Options
The following command line options are deliberately omitted,
as they are either handled internally or cannot be implemented.

--anat-derivatives
--bids-database-dir
--low-mem
--use-plugin
--fs-license-file
--work-dir
--clean-workdir

### Contributing

This repository will eventually be moved to GitLab and will use Flywheel's best practices for gears.  It is currently in an intermediate state between old development practices and the new ones.  The goal is towards this [Best Practice](https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/skeleton/-/blob/main/CONTRIBUTING.md) where poetry and pre-commit are used with GitLab CI.  Previously, this gear was designed from the [bids-app-template](https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/bids-app-template/-/blob/main/README.md).  The old template relied on scripts in `./tests/bin/` to build the gear and do testing inside the running gear. That is the old template and a new one will be developed soon.  No work should be done in this repository towards the new best practices until that new template has been created.

Curently, the following steps should be used when contributing to the development of this repository.

* Clone the repository and install poetry and pre-commit.
* Run `poetry install` to install the dependencies.
* Run `./tests/bin/poetry_export.sh` to create the requirements.txt files.
* Pre-commit hooks will run some linters, etc. when you commit changes to the repository.
* To build the gear and run tests inside the gear use `./tests/bin/run_tests.sh`.  To understand how code can be edited and tested inside the gear without re-building it, see [bids-app-template](https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/bids-app-template/-/blob/main/README.md).
* PyCharm or other debuggers can be set up to debug and run tests in the external poetry environment (not inside the running gear).

The idea is to get all test to pass locally, before committing and pushing the gear to GitHub.  Some of the current tests require you to be logged in to a specific Flywheel instance (ga) and have access to some specific projects.  If you do not, those tests will be skipped.  This dependency on a live instance with specific projects will be removed in the future.

This gear has two miniconda python environments in it.  One is supplied by the base fMRIPrep Docker image and the other is installed in side the Docker files.  The second environment is used to isolate the gear code from the fMRIPrep code.  In order to make that work, the original fMRIPrep environment variables are saved before creating the second python environment and installing its dependencies.  A `run.sh` script is used inside the gear to activate the gear code environment, run the gear code `run.py`, and then fMRIPrep is called as a subprocess where the original environment variables are provided.
