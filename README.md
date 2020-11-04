# bids-fmriprep
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) which runs [fMRIPrep](http://fmriprep.readthedocs.io) on BIDS-curated data. fMRIPrep is a functional magnetic resonance imaging (fMRI) data preprocessing pipeline that is designed to provide an easily accessible, state-of-the-art interface that is robust to variations in scan acquisition protocols and that requires minimal user input, while providing easily interpretable and comprehensive error and output reporting. It performs basic processing steps (coregistration, normalization, unwarping, noise component extraction, segmentation, skull stripping, etc.) providing outputs that can be easily submitted to a variety of group level analyses, including task-based or resting-state fMRI, graph theory measures, surface or volume-based statistics, etc.

The bids-fmriprep Gear can run at the [project](https://docs.flywheel.io/hc/en-us/articles/360017808354-EM-6-1-x-Release-Notes),  [subject](https://docs.flywheel.io/hc/en-us/articles/360038261213-Run-an-analysis-gear-on-a-subject) or [session](https://docs.flywheel.io/hc/en-us/articles/360015505453-Analysis-Gears) level.

This Gear requires a Freesurfer license. The license can be provided to the Gear in 3 ways. See [How to include a Freesurfer license file](https://docs.flywheel.io/hc/en-us/articles/360013235453).

## Troubleshooting

Depending upon your fMRIPrep workflow preferences, a variety of metadata and files may be required for successful execution. And because of this variation, not all cases will be caught during BIDS validation. If you are running into issues executing bids-fmriprep, we recommend reading through the configuration options explained with the [fMRIPrep Usage Notes](https://fmriprep.org/en/stable/usage.html) and double-checking the following:

### Fieldmaps ([BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#fieldmap-data))

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

### Functional ([BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data))

- Each functional NIfTI needs the following metadata: `EchoTime`, `EffectiveEchoSpacing`, `PhaseEncodingDirection`,`RepetitionTime`, `SliceTiming`, and `TaskName`.

