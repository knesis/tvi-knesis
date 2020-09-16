import numpy as np
def jaccard(mask1,mask2):
    '''
        Computation of Jaccard index for segmentation evaluation
        iou = jaccard(mask1,mask2)
        INPUTS:
            mask1 ~ boolean array (N x M) [Mask 1 to be evaluated; e.g. ground truth mask]
            mask2 ~ boolean array (N x M) [Mask 2 to be evaluated; e.g. predicted mask]
        OUTPUTS:    
            iou ~ float in [0,1] [Jaccard index]
    '''
    inter = np.sum(np.multiply(mask1 >= 1,mask2 >= 1)); # Intersection
    union = np.sum((mask1+mask2) >= 1); # Union
    iou = inter/max([union,1]); # Intersection/Union
    return iou;