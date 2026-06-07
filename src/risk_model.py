import numpy as np
import pandas as pd
def calc_acid_risk(lu_data,ph_data,crop_ph_df,assumed_crop="水稻"):
    #计算掩膜：
    valid_mask = ~np.isnan(lu_data)
    first_level = np.zeros_like(lu_data,dtype=int)
    first_level[valid_mask] = lu_data[valid_mask].astype(int)//10
    cropland_mask = (first_level == 1)
    #获取ph_low和ph_high
    crop_row = crop_ph_df[crop_ph_df["作物"] == assumed_crop]
    if crop_row.empty:
        raise ValueError(f"作物表中未找到 '{assumed_crop}'，请检查 crop_ph.csv")
    ph_low = crop_row["pH_low"].values[0]
    ph_high = crop_row["pH_high"].values[0]
    print(f"假设作物: {assumed_crop}, 最适pH范围: {ph_low} - {ph_high}")
    #计算风险系数：
    risk_array = np.full(lu_data.shape, np.nan, dtype=float)
    # 只对耕地像元计算
    ph_cropland = ph_data[cropland_mask]

    # 初始风险为0（适宜的情况）
    risk_cropland = np.zeros_like(ph_cropland)

    # 过酸：pH < ph_low，风险 = ph_low - pH
    too_acid = ph_cropland < ph_low
    risk_cropland[too_acid] = ph_low - ph_cropland[too_acid]

    # 过碱：pH > ph_high，风险 = pH - ph_high
    too_alkaline = ph_cropland > ph_high
    risk_cropland[too_alkaline] = ph_cropland[too_alkaline] - ph_high

    # 把算好的耕地风险填回大图里
    risk_array[cropland_mask] = risk_cropland

    # ========== 4. 统计风险概况 ==========
    total_cropland = np.sum(cropland_mask)
    at_risk = np.sum(risk_cropland > 0)

    stats = {
        "assumed_crop": assumed_crop,
        "optimum_range": f"{ph_low} - {ph_high}",
        "total_cropland_pixels": total_cropland,
        "at_risk_pixels": at_risk,
        "risk_rate(%)": round(at_risk / total_cropland * 100, 2),
        "mean_risk": round(np.nanmean(risk_array), 4),
        "max_risk": round(np.nanmax(risk_array), 4)
    }

    return risk_array, stats
    pass
