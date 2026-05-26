import rasterio
import numpy as np
import pandas as pd
#读取文件的函数,返回数据数组、投影变换和像元面积
def load_raster(filepath):
    with rasterio.open(filepath) as src:
        data = src.read(1).astype(float)
        transform = src.transform
        pixel_area = abs(transform.a*transform.e)
        #处理nodata
        if src.nodata is not None:
            data[data == src.nodata] = np.nan
    #去除无效值：
    data[data<=0] = np.nan
    return data,transform,pixel_area

#将ph值进行分类
def classify_ph(ph_array):
    """
        将土壤pH值分级为5类
        1: 强酸性 (pH<5.5)
        2: 酸性 (5.5-6.5)
        3: 中性 (6.5-7.5)
        4: 弱碱性 (7.5-8.5)
        5: 碱性 (pH>=8.5)
    """
    ph_class = np.full(ph_array.shape,np.nan)
    ph_class[ph_array<5.5] = 1
    ph_class[(ph_array>=5.5) & (ph_array<6.5)] = 2
    ph_class[(ph_array>=6.5) & (ph_array<7.5)] = 3
    ph_class[(ph_array>=7.5) & (ph_array<8.5)] = 4
    ph_class[(ph_array>=8.5)]=5
    return ph_class

#封装土地利用函数：
def reclassify_landuse(landuse_array):
    landuse_names = {
        1:"cropland",
        2:"forest",
        3:"grass",
        4:"water",
        5:"urban",
        6:"unused land"
    }
    unique_classes = np.unique(landuse_array[~np.isnan(landuse_array)].astype(int))#便于统计
    labels = [f"{cls}:{landuse_names.get(cls,f'类型{cls}')}" for cls in unique_classes]
    return landuse_names,labels,unique_classes
