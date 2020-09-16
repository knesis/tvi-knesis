# TissueVision Technical Questions

This document provides answers and justifications for the TissueVision technical questions.

## Technical Comments

### TQ1 - .TIF Metadata

As I interpret it, these data are multi-channel images of the same physical area, but are not incorporated into multi-page .tif files de facto. They instead have been saved separately by channel. 
Cursory online research indicates that only the first page of a multi-page .tif contains relevant metadata tags, and so, only the first channel of the provided data will be examined accordingly. Of course, the file striping offsets, etc. will be different but it is the same process nonetheless.
* One thing I noticed was that in addition to the .tif tags, additional metadata for the images were stored in the 'ImageDescription' field in the form of a Python dictionary string. Unknown if this is the standard for all relevant metadata, but these were added to the total tags.

### TQ2 - Binary Segmentation

The final processing steps for segmentation are as follows:
0. Averaging all Three Channels
	* There is likely a more rigorous process that filters all three channels separately, then combines them to create a threshold, but in the interest of time and simplicity, this method was not pursued.
1. Adaptive Histogram Equalization 
	* Correct for low contrast, as well as variable illumination patterns (e.g. imaging artifact in lower-right)
2. Thresholding using Triangle method
	* Reference:  G.W. Zack, W.E. Rogers, and S.A. Latt. Automatic measurement of sister chromatid exchange frequency. Journal of Histochemistry & Cytochemistry, 25(7):741, 1977. 1, 2.11
	* I know that the standard for segmentation is Otsu's method. However, the unimodality of the histogram, even after augmentation, resulted in too much background tissue being segmented in addition to the fluorescent cells. The triangle threshold, which was more conservative, produced visually and quantitatively higher results.
3. Removal of Miniscule Artifacts with Top-Hat Filter
	* The white top-hat filter takes the morphological opening of an image to remove small pixels in the segmentation mask. The structural element for this filtering was only 2 pixels, but produced substantially higher accuracy.
	* Top-hat filtering was attempted prior to the thresholding step to remove background or the bright outlier artifact, but no performance improvement could be obtained.
4. Evaluation of Segmentation using Jaccard Index (Intersection over Union)
	* Segmentation mask accuracy compared to ground truth (using Jaccard index) = 0.752.
	* Note: Large component of visible error is believed to result from the high intensity artifact in original images, which could not be satisfactorily removed in a robust fashion.


### TQ3 - Feature Extraction

`scikit-image` has functionality for extracting various features from segmentation. 
The selected properties which were considered to be of interest are as follows:
* Area
* Coordinates for Bounding Box
* Mask Values in Bounding Box
* Image Values in Bounding Box
* Centroid
* Major Axis Length
* Minor Axis Length
* Orientation
* Perimeter
* Eccentricity
* Max Intensity of ROI
* Min Intensity of ROI
* Mean Intensity of ROI

* Additional note: I considered adding an extra custom property for circularity, but the calculation may be uninformative for ROIs with such small areas. Moreover, the essence of the measurement is captured somewhat by the "eccentricity" property.


*Strategies for optimizing I/O of mask and feature tables*
1. For single machine and large data, functionalities of pandas can be leveraged to read feature data in chunks to preserve machine memory. In this case, feature tables may be small enough to store hierarchically by dataset/slice/tile (probably not the best, but saved as .csv here due to small data). 
2. For distributed applications seeking to process objects in parallel, the mask and properties can be stored using a relational database such as PostgreSQL, or a distributed file system like HDFS, for which computations can be assembled as a graph and simplified.    
	* Notes: Not too knowledgeable about the specifics, but I believe that PostgreSQL tables can be paritioned for large data to facilitate more operations.
    * More notes: pandas has `.to_sql()` and `.to_hdf()` methods for writes to DBMS.
3. The binary mask image (or reference to that image) should probably be stored as its own field in a table that stores metadata about the image dataset, and so would contain the identifier (41077_120219), number of slices, etc. The dataset identifier is what I believe could be used as the key for selecting relevant records in a separate, larger feature table.
	   
### TQ4 - Signal Difference Metric

I utilized the Signal Difference to Noise Ratio (SDNR) as my signal difference metric, which measures the difference between mean foreground (signal) and mean background (noise), divided by the background standard deviation. It is closely related to the Contrast to Noise Ratio (CNR).

I refrained from using the more common Signal to Noise Ratio (SNR) as, over the entire image, it would be sensitive to changes in mean illumination, which is not preferable. 

The foreground and background regions were segmented using the Yen threshold without any preprocessing, which worked well enough to demonstrate the proof-of-concept. It is perhaps important to note that applying the procedure in TQ2 produced unusable segmentation. This may be the result of using single channel images, rather than averaging the three-channel data, but likely reveals underlying instability in the segmentation process. Testing on additional three-channel image sets may verify its suitability/unsuitability.

The effectiveness of this metric can be validated by introducing believable augmentation and distortion into existing data and observing how the results of the metric respond.
* Properties to vary likely include mean brightness, global contrast, and possibly local contrast. 
* SDNR should be invariant to mean brightness changes, and also increase with increasing global contrast (which I believe is a desired change). 
* Note that alterations to local contrast may affect segmentation results. 
* Rather than introduce artifical distortions, other image sets (which might have slightly different image response characteristics) can also be used.
	* Perhaps existing data of the same tissue slice, but different channels/biomarkers can be used to measure bias.

### TQ5 - Scalability

* Proper scalability of the segmentation and processing steps depends on an efficient way of splitting the large .TIF files into manageable (storable-in-memory) subtiles and accessing/operating on those tiles.
* Libraries for accessing the raster data of .TIF files in a block index-able form include OpenSlide-Python (designed for large whole-slide images), and GDAL (designed for geospatial data). Not knowing much about GDAL, I would be inclined to use OpenSlide.
* There is also VIPS, which is an image processing library designed for large images. It has several pre-built filters/operators, but I believe it can also be used to split a large .TIF into multi-threaded stacks of identically-sized tiles for processing.
* Given a specific tile, the segmentation step can proceed identically to the existing method. However, a consistent threshold might need to be applied to all tiles of the original image section for consistency. It is perhaps feasible to perform segmentation on one random tile first as a test, then apply the resultant threshold to all tiles during the complete pass. In general however, you would probably want the segmentation procedure to be robust enough to proceed independently for each tile.
* Similarly, the signal difference metric can also be computed for each tile in the larger image. Although, if it is desired to summarize the metric for an entire image section, the measurements might be averaged over all tiles.
* In order to arrange the distributed access to individual tiles in a large image section, preprocessing would require splitting the .TIF file and storing tile identifiers and offset coordinates in a relational database table. Simultaneous reads of multiple records (tiles) would allow distributed processing on the individual tiles. Intermediate results (segmentation masks) would need to be stored in a scratch directory until all processing has been completed. At this point, the tiles can be reassembled into a large .TIF output mask, or used to sequentially compute the signal difference metric (if using SDNR). Processing may be distributed using Spark/Hadoop.