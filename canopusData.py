import os
files = ['matrix_seeds_to_all_targets','matrix_seeds_to_all_targets_lengths']
subjects = [xx.strip() for xx in '''
188145  206929  238033  360030  401422  453542  468050
192237  208630  248238  368753  413934  454140  481042
206323  227533  325129  392447  421226  463040'''.split()]
ROIs = ['L'+str(i) for i in range(1,181)] + ['R'+str(i) for i in range(1,181)]

for sub in subjects:
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
