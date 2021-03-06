#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import nibabel as nb
import numpy as np
import subprocess


def load_aa_ras(aa_path):
    with tempfile.NamedTemporaryFile(suffix='.nii.gz') as tf:
        # TODO use cli wrapped commands
        subprocess.check_call([
            'mri_convert', aa_path, tf.name,
            '--out_orientation', 'RAS', '-rt', 'nearest'
        ])
        aa_img = nb.load(tf.name)
    return aa_img


def load_contacts(contact_path):
    contacts = []
    with open(contact_path, 'r') as fd:
        for line in fd.readlines():
            name, x, y, z = line.strip().split()
            contacts.append((name, float(x), float(y), float(z)))
    return contacts


def contact_fs_names(aa_img, contacts, lut):
    inv_aff = np.linalg.inv(aa_img.affine)
    aa_dat = aa_img.get_data()
    for name, x, y, z in contacts:
        i, j, k = ijk = inv_aff.dot(np.r_[x, y, z, 1])[:-1].astype('i')
        aa_val = aa_dat[i, j, k]
        aa_name = lut[aa_val]
        yield name, aa_name
    

def build_fs_label_name_map(lut_path):
    lut = {}
    with open(lut_path, 'r') as fd:
        for line in fd.readlines():
            if not line[0] == '#' and line.strip():
                val, name, _, _, _, _ = line.strip().split()
                lut[int(val)] = name
    return lut


def write_results(results, output_tsv):
    with open(output_tsv, 'w') as fd:
        for name, aa_name in results:
            fd.write('%s\t%s\n' % (name, aa_name))


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("label_volume", help="nibabel-loadable label volume to analyze")
    parser.add_argument("contacts", help="file produced by seeg-ct.sh describing contact positions")
    parser.add_argument("output_tsv", help="tab-separated file to write")
    parser.add_argument("--loglevel", help="set logging level", default="INFO")
    parser.add_argument("--fs-lut", help="path to FreeSurferColorLUT.txt")
    return parser
   
    
def main():
    parser = build_argparser()
    parse = parser.parse_args()
    print(parse)
    logging.basicConfig(level=getattr(logging, parse.loglevel))
    log = logging.getLogger(sys.argv[0])
    
    log.info('reading %r', parse.label_volume)
    vol = nb.load(parse.label_volume)
    
    log.info('loading FS LUT')
    lut_path = parse.fs_lut or (
        os.path.join(os.environ['FREESURFER_HOME'], 'FreeSurferColorLUT.txt'))
    lut_map = build_fs_label_name_map(lut_path)
    
    log.info('reading %r', parse.contacts)
    contacts = load_contacts(parse.contacts)
    
    log.info('computing contact names')
    results = list(contact_fs_names(vol, contacts, lut_map))
    
    log.info('writing results to %r', parse.output_tsv)
    write_results(results, parse.output_tsv)
    

if __name__ == '__main__':
    main()