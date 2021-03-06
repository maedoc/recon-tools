#!/bin/bash

pushd $DMR

#Tractography
#some more/alternative options?: -backtrack -crop_at_gmwmi -seed_dynamic wm_fod.mif -cutoff 0.06
opt="-seed_gmwmi ./gmwmi.mif -act ./5tt.mif -unidirectional -maxlength $STRMLNS_MAX_LEN -step $STRMLNS_STEP -nthreads $MRTRIX_THRDS"
tckgen ./wm_fod.mif ./$STRMLNS_NO.tck -number $STRMLNS_NO $opt -force

#SIFT filter
opt="-act ./5tt.mif -nthreads $MRTRIX_THRDS"
tcksift ./$STRMLNS_NO.tck ./wm_fod.mif ./$STRMLNS_SIFT_NO.tck -term_number $STRMLNS_SIFT_NO $opt -force

#Visual check (track density image -tdi)
#vox: size of bin
tckmap ./$STRMLNS_SIFT_NO.tck ./tdi_ends-v1.mif -vox 1 -template ./b0.nii.gz -force
#Interactive:
#mrview ./t1-in-d.nii.gz -overlay.load ./tdi-v1.mif -overlay.opacity 0.5
#Snapshot
mrconvert ./tdi_ends-v1.mif ./tdi_ends-v1.nii.gz -force
python -m $SNAPSHOT --ras_transform --snapshot_name t1_tdi_in_d 2vols ./t1-in-d.nii.gz ./tdi_ends-v1.nii.gz

popd
