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
    landuse_array[:] = landuse_array//10
    unique_classes = np.unique(landuse_array[~np.isnan(landuse_array)].astype(int))#便于统计
    labels = [f"{cls}:{landuse_names.get(cls,f'类型{cls}')}" for cls in unique_classes]
    return landuse_names,labels,unique_classes

#封装面积交叉统计函数：
def calc_area_crosstab(landuse_array,ph_class_array,landuse_names,pixel_area):
    valid_mask = ~np.isnan(landuse_array)&~np.isnan(ph_class_array)
    raw_codes = landuse_array[valid_mask].astype(int)
    first_level = raw_codes//10
    first_level[first_level == 9 ] = 6#将可能出现的海洋归类为未利用地
    ph_values = ph_class_array[valid_mask]
    df = pd.DataFrame(
        {
            "LandUse_Code":first_level,
            "pH_Class":ph_values
        }
    )
    cross_counts = df.groupby(["LandUse_Code","pH_Class"]).size().unstack(fill_value=0)
    cross_area = cross_counts*pixel_area/1e6
    ph_labels = {
        1:"pH<5.5",
        2:"5.5~6.5",
        3:"6.5·7.5",
        4:"7.5~8.5",
        5:">=8.5"
    }
    cross_area = cross_area.rename(columns=ph_labels)
    cross_area.index = cross_area.index.map(lambda x:landuse_names.get(x,f"类型{x}"))
    cross_area["Total"] = cross_area.sum(axis=1)
    return cross_area.round(3)

#重采样函数（源数据没有对齐）：
from rasterio.warp import reproject, Resampling

def resample_raster(src_path, ref_path, output_path):
    """
    将源栅格重投影并重采样，使其与参考栅格完全对齐
    """
    with rasterio.open(ref_path) as ref:
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_width = ref.width
        ref_height = ref.height

    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        profile.update({
            'crs': ref_crs,
            'transform': ref_transform,
            'width': ref_width,
            'height': ref_height,
            'driver': 'GTiff',
            'compress': 'lzw'
        })

        with rasterio.open(output_path, 'w', **profile) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=ref_transform,
                    dst_crs=ref_crs,
                    resampling=Resampling.bilinear
                )
        print(f"重投影完成，已保存至: {output_path}")