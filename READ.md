# 农田土壤酸化风险评估

## 项目简介
本项目基于全国土地利用和土壤 pH 栅格数据，结合爬取的作物最适 pH 表，构建“作物-土壤酸碱错配风险模型”。通过空间叠加分析，评估全国耕地（水田假设种水稻、旱地假设种玉米）的酸化风险，并生成市级风险排名，为农业种植结构调整和土壤改良提供数据支持。

## 技术栈
- **编程语言**：Python 3
- **核心库**：rasterio, numpy, pandas, geopandas, matplotlib, requests, BeautifulSoup
- **空间分析**：栅格重投影、重采样、掩膜提取、分区统计
- **数据获取**：爬虫（作物最适 pH 表）
- **版本控制**：Git & GitHub

## 数据来源
| 数据 | 来源 | 说明 |
|------|------|------|
| 土地利用 | 中科院资源环境科学与数据中心 (RESDC) | 2023 年全国 1km 栅格 |
| 土壤 pH | 国家青藏高原科学数据中心 (CSDL v2) | 表层 0-5cm，重采样至 1km |
| 作物最适 pH | 重庆市农业农村委员会 (nyncw.cq.gov.cn) | 爬虫获取，源自《土壤学》教材 |
| 行政区划 | 中科院 RESDC | 2022 年地级市界 |

## 主要结论
- 全国约 **54%** 的耕地土壤 pH 偏离了假设作物的最适范围。
- 高风险区域集中在北方，宁夏石嘴山、银川等城市风险占比超过 99%。
- 建议高风险区优先进行土壤改良或调整种植结构。

## 如何运行
1. 创建虚拟环境
python -m venv venv

2. 激活虚拟环境 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

3. 升级 pip（Python 3.13+ 必须先做这一步，否则 pip 会报错）
python -m pip install --upgrade pip

如果上一步报错，用下面的命令强制重装 pip：
python -c "import urllib.request; exec(urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py').read())"

4. 安装项目依赖
pip install -r requirements.txt