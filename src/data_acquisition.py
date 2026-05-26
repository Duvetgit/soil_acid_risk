#导入库
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

#封装函数
def crawl_crop_ph_table(url:str) -> pd.DataFrame:
    #伪装head
    headers = {"User-Agent":"Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebkit/537.36"}
    #第一步发送请求，获取网页内容
    try:
        response = requests.get(url,headers,timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
    except Exception as e:
        print(f"请求页面失败：{e}")
        return pd.DataFrame()
    #第二步解析网页
    soup = BeautifulSoup(response.text,"html.parser")

    #第三步找到表格并删除其他数据
    table = soup.find("table")
    if table is None:
        print("页面中没有找到表格")
        return pd.DataFrame()
    # 第四步：用BeautifulSoup直接解析表格，不再使用pd.read_html
    # 提取所有行
    rows = table.find_all("tr")
    if len(rows) < 2:
        print("表格行数不足，无法解析")
        return pd.DataFrame()

    # 第一行是pH范围，作为表头
    header_cells = rows[0].find_all("td")
    ph_ranges = [cell.get_text(strip=True) for cell in header_cells]
    print(f"识别到的pH范围列：{ph_ranges}")

    # 第二行开始是数据行（每种作物对应一个pH范围）
    data_rows = rows[1:]  # 跳过表头行

    # 构建结果列表
    records = []
    for row in data_rows:
        cells = row.find_all("td")
        # 确保列数一致
        if len(cells) != len(ph_ranges):
            continue
        for i, cell in enumerate(cells):
            ph_range = ph_ranges[i]  # 对应的pH范围，如 "pH 6.5~7.5"
            # 一个单元格里可能有多个作物，用<p>标签分隔
            crop_names = [p.get_text(strip=True) for p in cell.find_all("p")]
            if not crop_names:
                continue
            for crop in crop_names:
                records.append({
                    "作物": crop,
                    "pH_range": ph_range
                })

    if not records:
        print("未能从表格中提取到任何数据")
        return pd.DataFrame()

    df_raw = pd.DataFrame(records)
    print(f"原始提取数据共 {len(df_raw)} 条")

    # 第五步：从pH范围字符串中提取pH_low和pH_high
    try:
        # 去掉 "pH " 前缀，按 "~" 拆分
        pH_values = df_raw["pH_range"].str.replace("pH ", "", regex=False).str.split("~", expand=True)
        df_raw["pH_low"] = pd.to_numeric(pH_values[0], errors="coerce")
        df_raw["pH_high"] = pd.to_numeric(pH_values[1], errors="coerce")

        # 只保留需要的三列，并去掉pH值缺失的行
        df = df_raw[["作物", "pH_low", "pH_high"]].dropna(subset=["pH_low", "pH_high"])
        df = df.reset_index(drop=True)

        print("\n清洗后数据预览：\n", df.head(10))
        print(f"共获取 {len(df)} 条作物-pH 记录")
    except Exception as e:
        print(f"数据清洗有错：{e}")
        return pd.DataFrame()

    return df




#主函数
if __name__ == "__main__":
    target_url = "https://nyncw.cq.gov.cn/zwxx_161/rdtt/202212/t20221205_11353980_wap.html"
    crop_ph_df = crawl_crop_ph_table(target_url)

    if not crop_ph_df.empty:
        crop_ph_df.to_csv("../data/crop_ph.csv",index=False,encoding='utf-8-sig')
        print("成功保存到data/crop_ph.csv")
    else:
        print("未获取到数据，检查代码或者网页")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    time.sleep(2)
