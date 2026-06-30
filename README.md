本项目旨在通过 Python 爬虫与 R 语言数据分析，在治疗胆汁酸过多症的中药方剂中，筛选并识别能与胆汁酸家族分子高效结合的潜在中药活性成分。

核心技术：

    1.数据采集：编写 Python 爬虫，从 TCMID、TCMBank 及 TCMSP 数据库批量抓取目标中药分子数据及对应的 mol 结构文件。

    2.结构转化：利用脚本将 mol 文件批量转化为标准 SMILES 字符串，并进一步将其编码为分子指纹。

    3.数据挖掘 (ADMET)：基于 SMILES 号，通过爬虫在 ADMETlab 平台批量获取分子的药代动力学（ADMET）核心属性。

    4.相似性评价：计算分子指纹与胆汁酸分子的 Tanimoto 相似性系数，定量评估其空间结合潜力。

    5.统计与可视化：使用 R 语言对批量 ADMET 数据进行清洗、统计建模与高维数据可视化呈现。

本项目核心代码均由本人独立编写。感谢王超老师在项目进展中提供指导与建议支持。

This project aims to use Python web scraping and R-language data analysis to screen and identify potential active ingredients in traditional Chinese medicine (TCM) formulations for treating hyperbilirubinemia that can bind efficiently to molecules in the bile acid family.

Core Technologies:

    1. Data Collection: Develop a Python web crawler to batch-extract data on target TCM molecules and their corresponding mol structure files from the TCMID, TCMBank, and TCMSP databases.

    2. Structure Conversion: Use scripts to batch-convert mol files into standard SMILES strings and further encode them into molecular fingerprints.

    3. Data Mining (ADMET): Based on SMILES identifiers, use web crawlers to batch-retrieve core pharmacokinetic (ADMET) properties of molecules from the ADMETlab platform.

    4. Similarity Assessment: Calculate the Tanimoto similarity coefficient between molecular fingerprints and bile acid molecules to quantitatively evaluate their spatial binding potential.

    5. Statistics and Visualization: Use the R programming language to clean the batch ADMET data, perform statistical modeling, and visualize high-dimensional data.

All core code for this project was written independently by me. I would like to thank Professor Wang Chao for his guidance, advice, and support throughout the project.
