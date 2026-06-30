import os
from rdkit import DataStructs
from rdkit.DataStructs.cDataStructs import ExplicitBitVect
from openpyxl import Workbook


input_folder = "C:\\Users\\pc\\Desktop\\4_fingerprint"
output_file = "C:\\Users\\pc\\Desktop\\tanimoto.xlsx"


# 获取所有药物文件名
drug_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
drug_data = {}


for drug_file in drug_files:
    drug_id = os.path.splitext(drug_file)[0]  # 使用文件名作药物id

    # 读取分子指纹数据
    with open(os.path.join(input_folder, drug_file), "r") as f:
        lines = f.readlines()

    drug_fps = []
    for line in lines:
        mol_id, fp_str = line.strip().split("\t")
        # 将指纹字符串转换为ExplicitBitVect
        fp = ExplicitBitVect(len(fp_str))
        for i, bit in enumerate(fp_str):
            if bit == "1":
                fp.SetBit(i)
        drug_fps.append((mol_id, fp))
    drug_data[drug_id] = drug_fps # 药物id作键,分子id和分子指纹作值


# 创建工作簿
wb = Workbook()
wb.remove(wb.active)


# 计算每对药物之间的Tanimoto, 同一个文件内的分子之间没有计算tanimoto系数
for i, (drug1, fps1) in enumerate(drug_data.items()):
    for j, (drug2, fps2) in enumerate(drug_data.items()):
        if i < j:  # 只计算上三角矩阵
            sheet_name = f"{drug1}和{drug2}"
            ws = wb.create_sheet(sheet_name)

            # 写入表头
            ws.append([drug1, drug2, "Tanimoto"])

            # Tanimoto
            for mol1_id, fp1 in fps1:
                for mol2_id, fp2 in fps2:
                    similarity = DataStructs.FingerprintSimilarity(fp1, fp2)
                    ws.append([mol1_id, mol2_id, similarity])


# 保存
wb.save(output_file)

print(f"计算完成，结果已保存到 {output_file}")
