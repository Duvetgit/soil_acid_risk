import numpy as np
import pandas as pd
def calc_acid_risk(lu_data,ph_data,crop_ph_df,paddy_crop="水稻",dryland_crop="玉米"):
    #计算掩膜：
    valid = ~np.isnan(lu_data)
    raw_codes = lu_data[valid].astype(int)
    paddy_mask = np.zeros_like(lu_data,dtype=bool)
    paddy_mask[valid] = (raw_codes == 11)
    dryland_mask = np.zeros_like(lu_data,dtype=bool)
    dryland_mask[valid] = (raw_codes == 12)
    cropland_mask = paddy_mask|dryland_mask
    #获取ph_low和ph_high,这里弄玉米和水稻两种，封装函数
    def get_optimum(crop_name):
        crop_row = crop_ph_df[crop_ph_df["作物"] == crop_name]
        if crop_row.empty:
            raise ValueError(f"作物表中未找到 '{crop_name}'，请检查 crop_ph.csv")
        ph_low = crop_row["pH_low"].min()
        ph_high = crop_row["pH_high"].max()
        return ph_low,ph_high
    paddy_low,paddy_high = get_optimum(paddy_crop)
    dry_low,dry_high = get_optimum(dryland_crop)
    print(f"水稻假设作物: {paddy_crop}, 最适pH范围: {paddy_low} - {paddy_high}")
    print(f"水稻假设作物: {dryland_crop}, 最适pH范围: {dry_low} - {dry_high}")
    ph_data = ph_data/100.0
    #计算风险系数：
    risk_array = np.full(lu_data.shape, np.nan, dtype=float)
    for mask,low,high in [(paddy_mask,paddy_low,paddy_high),
                          (dryland_mask,dry_low,dry_high)]:
        if np.sum(mask) == 0:
            continue
        ph_vals = ph_data[mask]
        risks = np.zeros_like(ph_vals)
        too_acid = ph_vals < low
        too_alk = ph_vals > high
        risks[too_acid] = low-ph_vals[too_acid]
        risks[too_alk] = ph_vals[too_alk] - high
        risk_array[mask] = risks
    # ========== 4. 统计风险概况 ==========
    total_cropland = np.sum(cropland_mask)
    at_risk = np.sum(risk_array[cropland_mask] > 0)

    stats = {
        "paddy_crop": paddy_crop,
        "dryland_crop":dryland_crop,
        "total_cropland":total_cropland,
        "paddy_pixels":np.sum(paddy_mask),
        "dryland_pixels":np.sum(dryland_mask),
        "at_risk_pixels": at_risk,
        "risk_rate(%)": round(at_risk / total_cropland * 100, 2),
        "mean_risk": round(np.nanmean(risk_array), 4),
        "max_risk": round(np.nanmax(risk_array), 4)
    }

    return risk_array, stats
    pass
