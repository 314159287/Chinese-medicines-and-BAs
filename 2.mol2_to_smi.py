import os
import sys
from rdkit import Chem

def convert_mol2_to_smi(input_file, output_file):
    # 读取mol2
    mol = Chem.MolFromMol2File(input_file)
    if mol is not None:
        # 转换成smi
        smi = Chem.MolToSmiles(mol)
        with open(output_file, 'w') as f:
            f.write(smi)
        print(f"Converted {input_file} to {output_file}")
    else:
        print(f"Failed to convert {input_file}")

def batch_convert(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".mol2"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace(".mol2", ".smi"))
            convert_mol2_to_smi(input_path, output_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python mol2_to_smi_converter.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist.")
        sys.exit(1)

    batch_convert(input_directory, output_directory)
    print("Conversion completed.")

#python 2.mol2_to_smi.py /path/to/input/mol2 /path/to/output/smi