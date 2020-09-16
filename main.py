"""
Tissue Vision Technical Questions
Anthony Knesis
9/16/2020

"""

import glob, pprint
import numpy as np
from skimage import io,measure,img_as_float,filters
from tvi_knesis import extract_tif_meta,jaccard,sdnr,segment_mask
import pandas as pd
import matplotlib.pyplot as plt

#------------------------------------------------------------------#
# Constants for convenience
# Naming conventions will dictate more rigorous file parsing schemes 
#   (regex,etc.)

OUT_DIR = 'output'
DATA_DIR = 'data'

# Data Locations
IMG_DIR = 'TQ1';
MASK_DIR = 'TQ2';
DIFF_DIR = 'TQ4';

# Dataset Prefix
IMG_DATASET = '41077_120219_S000090';

# Filenames for data in TQ1, TQ2, and TQ4 respectively
IMG_FNAMES = glob.glob(f"./{DATA_DIR}/{IMG_DIR}/{IMG_DATASET}_*.tif");
MASK_FNAME = f"./{DATA_DIR}/{MASK_DIR}/binary_{IMG_DATASET}_L01.tif";
DIFF_FNAMES = glob.glob(f"./{DATA_DIR}/{DIFF_DIR}/*.tif");

# Output paths
SEGM_PATH = f"./{OUT_DIR}/segmask_{IMG_DATASET}.tif"; # Segmentation mask
FEATS_PATH = f"./{OUT_DIR}/regions_{IMG_DATASET}.csv"; # ROI features
SDNR_PATH = f"./{OUT_DIR}/sdnr_{IMG_DATASET[:-8]}.png"; # Signal diff. plot

#------------------------------------------------------------------#
## TQ1 = Reading images and extracting .tif metadata


# Read metadata from first .tif
img_META = extract_tif_meta(IMG_FNAMES[0]);
pprint.PrettyPrinter(indent=4).pprint(img_META);
    

#------------------------------------------------------------------#
## TQ2 = Binary segmentation mask
    
# Load data and convert to grayscale
img_UINT = np.stack([io.imread(img) for img in IMG_FNAMES]);
img_FLOAT = img_as_float(img_UINT);
img_GRAY = np.mean(img_FLOAT,axis=0);

# Generate binary segmentation mask (see segment_mask.py)
mask_pred = segment_mask(img_GRAY);

# Evaluate similarity using Jaccard index (Intersection over Union)
# Load mask into memory
mask_truth = io.imread(MASK_FNAME);
iou = jaccard(mask_pred, mask_truth);
print(f"Segmentation accuracy is {iou}")

# Save output mask
io.imsave(SEGM_PATH,mask_pred.astype('uint16'),plugin='tifffile');

#------------------------------------------------------------------#
## TQ3 = Feature Extraction

# Mark each distinct object in segmentation mask for analysis
lbls = measure.label(mask_pred,connectivity=2);

# Define relevant properties for ROIs
proplist = ['label','area','bbox','image','intensity_image',\
              'centroid','major_axis_length','minor_axis_length',\
              'orientation', 'perimeter','eccentricity',\
              'max_intensity','min_intensity','mean_intensity'];
# Note: I considered adding an extra custom property for circularity, but the
#   calculation may be uninformative for ROIs with such small areas.
    
# Produce pandas-compatible dictionary of object features         
propdict = measure.regionprops_table(lbls,img_GRAY,properties=proplist);

# Convert directly to dataframe for storage as .csv (for demo)
propdf = pd.DataFrame.from_dict(propdict);
propdf.to_csv(FEATS_PATH);


#------------------------------------------------------------------#
## TQ4 - Signal Difference Metric for Images

# Assess contrast using Signal-Difference to Noise Ratio 
#   (very similar to Contrast to Noise Ratio)

# Calculate for each provided image
sdnrs = np.zeros(len(DIFF_FNAMES));
for i in range(0,len(DIFF_FNAMES)):
        img = io.imread(DIFF_FNAMES[i]);
        thresh = filters.threshold_yen(img);
        mask = img > thresh;
        sdnrs[i] = sdnr(img,mask);      
        
# Generate output plot and save
fig = plt.figure();
plt.plot(sdnrs);
plt.grid(which='major')
plt.xlabel('Slice (start=S000071)');
plt.ylabel('SDNR');
plt.title(f"SDNR for data: {IMG_DATASET[:-8]}");
plt.savefig(SDNR_PATH)



