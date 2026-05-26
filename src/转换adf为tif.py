import rasterio
import math

# ========== 请根据你的实际文件路径修改 ==========
# 输入：你的 ADF 数据文件夹路径
adf_folder = r"C:\Users\xiehe\Desktop\2023年\ld2023_1km"

# 输出：你要保存的 TIF 文件路径
output_tif = r"C:\Users\xiehe\Desktop\2023年\landuse_2023.tif"
# ================================================

try:
    # 1. 用 rasterio 直接打开 ADF 文件夹
    with rasterio.open(adf_folder) as src:
        # 2. 读取所有数据
        data = src.read()

        # 3. 计算合适的 tile 尺寸（16 的倍数）
        # 取行数列数中较小值，且不超过 256
        tile_size = min(256, src.height, src.width)
        # 向下取整到 16 的倍数
        tile_size = (tile_size // 16) * 16
        # 万一结果为 0 就设成 16
        if tile_size < 16:
            tile_size = 16

        # 4. 复制并更新元数据
        profile = src.profile.copy()
        profile.update(
            driver='GTiff',
            compress='lzw',          # 压缩，减小文件体积
            tiled=True,              # 启用分块写入
            blockxsize=tile_size,    # 块的宽度
            blockysize=tile_size     # 块的高度
        )

        # 5. 写入 TIF 文件
        with rasterio.open(output_tif, 'w', **profile) as dst:
            dst.write(data)

        print(f"✅ 转换成功！")
        print(f"   新文件: {output_tif}")
        print(f"   形状: {src.shape}, 波段数: {src.count}")
        print(f"   分辨率: {src.res}, 坐标系: {src.crs}")

except Exception as e:
    print(f"❌ 转换失败: {e}")