"""
将 ADF 栅格数据文件夹转换为 GeoTIFF 格式。

用法:
    python src/convert_adf_to_tif.py <输入ADF文件夹> <输出TIF文件>

示例:
    python src/convert_adf_to_tif.py "C:\path\to\ld2023_1km" "C:\path\to\landuse_2023.tif"
"""
import rasterio
import sys
import os


def convert_adf_to_tif(adf_folder, output_tif):
    """将 ADF 栅格数据文件夹转换为 GeoTIFF 格式。"""
    with rasterio.open(adf_folder) as src:
        data = src.read()

        # 计算合适的 tile 尺寸（16 的倍数）
        tile_size = min(256, src.height, src.width)
        tile_size = (tile_size // 16) * 16
        if tile_size < 16:
            tile_size = 16

        profile = src.profile.copy()
        profile.update(
            driver='GTiff',
            compress='lzw',
            tiled=True,
            blockxsize=tile_size,
            blockysize=tile_size
        )

        with rasterio.open(output_tif, 'w', **profile) as dst:
            dst.write(data)

        print(f"✅ 转换成功！")
        print(f"   新文件: {output_tif}")
        print(f"   形状: {src.shape}, 波段数: {src.count}")
        print(f"   分辨率: {src.res}, 坐标系: {src.crs}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    adf_folder = sys.argv[1]
    output_tif = sys.argv[2]

    if not os.path.exists(adf_folder):
        print(f"❌ 输入路径不存在: {adf_folder}")
        sys.exit(1)

    try:
        convert_adf_to_tif(adf_folder, output_tif)
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        sys.exit(1)
