import tifffile, ast
def extract_tif_meta(fname):
    '''
        Extracts .tif metadata (tags) and additional information embdedded in 'ImageDescription'
        meta = extract_tif_meta(fname)
        INPUTS:
            fname ~ string [path to .tif file]
        OUTPUTS:
            meta ~ dict [contains .tif tags (UPPERCASE keys) and additional information (lowercase keys, if present)
    '''

    with tifffile.TiffFile(fname) as tif:
        meta = {item[0] : item[1].value \
                    for item in tif.pages[0].tags.items()};

    # Expand tags embedded in ImageDescription fields
    # Note: My current solution uses a literal_eval to turn the string into a 
    #   Python dictionary. I know that eval() is not good practice and I would not
    #   normally use it, but ast.literal_eval() is at least rigorously limited to 
    #   parsing Python datatypes exclusively.
    try:
        tags_extra = ast.literal_eval(meta['ImageDescription']);
        meta.update(tags_extra); # Extra metadata appended to original tags
    except:
        pass; # Exception handling in case 'ImageDescription' field is not formatted as dictionary
    try:
        tags_extra2 = ast.literal_eval(meta['ImageDescription1']);
        meta.update(tags_extra2); # Check in case 'ImageDescription1' might have some tags
    except:
         pass; 
               
    return meta;