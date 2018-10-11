import os
files = ['matrix_seeds_to_all_targets','matrix_seeds_to_all_targets_lengths']
subjects = [xx.strip() for xx in '''
192237R 227533R 368753L 453542L 468050L'''.split()]
ROI_L = ['L'+str(i) for i in range(1,181)]
ROI_R = ['R'+str(i) for i in range(1,181)]

for sub in subjects:
    ROIs = []
    if sub.endswith('L'):
        sub = sub[:-1]
        ROIs = ROI_L
    elif sub.endswith('R'):
        sub = sub[:-1]
        ROIs = ROI_R
    else:
        ROIs = ROI_L + ROI_R

    for roi in ROIs:
        print(sub+' ' + roi)
        for file in files:
            out_dir = '/net/ht140/kamal/HCP/DATA/SUB2/ROI2/'
            cmd = '''
            cp /net/ht140/kamal/HCP/hcp/SUB1/out/ROI1/FILE '''
            cmd = cmd.replace('SUB1',sub)
            out_dir = out_dir.replace('SUB2',sub)
            cmd = cmd.replace('ROI1',roi)
            out_dir = out_dir.replace('ROI2',roi)
            cmd = cmd.replace('FILE',file)
            cmd = cmd.strip()
            if (not os.path.isdir(out_dir)):
                os.makedirs(out_dir)
            cmd = cmd + ' ' +out_dir
            os.system(cmd)
