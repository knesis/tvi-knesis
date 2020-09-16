from skimage import filters, morphology, exposure
import numpy as np
def segment_mask(img_GRAY):
    '''
        Computation of Segmentation Mask for grayscale images
        mask_pred = segment_mask(img_GRAY)
        INPUTS:
            img_GRAY ~ 2D array, dtype=float (N x M) [Grayscale input for which mask will be generated
        OUTPUTS:    
            mask_pred ~ Boolean array (N x M) [Output segmentation mask in [0,1]]
    '''
    
    # Increase contrast by adapative histogram equalization
    # The low contrast in large parts of the image, coupled with the high
    #   intensity for the bottom-right artifacts, motivated selection of a locally
    #   adaptive form of histogram equalization.
    img_HISTEQ = exposure.equalize_adapthist(img_GRAY);

    # Use triangle threshold for segmenting objects
    # Given the skewed and unimodal distribution of pixel values, 
    #   the triangle threshold was selected as desirable for isolating the
    #   tail of peak pixel intensities without including brighter segments of the 
    #   tissue (as was observed with Otsu)
    thresh = filters.threshold_triangle(img_HISTEQ);
    mask_init = img_HISTEQ > thresh;

    # Use white tophat filtering to remove small artifacts
    # White top-hat filtering inflates objects larger than the structural element,
    #   and then returns the complement. The original mask can be used to crush
    #   small structures in the original image.
    strel =  morphology.disk(2);
    noise = morphology.white_tophat(mask_init,strel);
    mask_pred = np.logical_and(mask_init, np.logical_not(noise));
    return mask_pred;