import numpy as np
def sdnr(img,mask):
    '''
    Calculate Signal Difference to Noise Ratio
    out = sdnr(img,mask)
    INPUTS:
        img ~ 2D array (N x M) [Input image for calculation]
        mask ~ Boolean array (N x M) [Segmentation mask highlighting bright informative regions]
    OUTPUTS:    
        out ~ np.float16 [SDNR metric]
    '''
    sig = np.average(img,weights=(mask>0)); # Mean level of signal
    bg = np.average(img,weights=(mask<1)); # Mean level of background (noise)
    bgstd = np.std(img[mask<1],ddof=1); # Std. dev. of background
    out = np.abs(sig-bg)/bgstd; # Signal Difference to Noise Ratio
    return out;