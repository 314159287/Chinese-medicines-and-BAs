from rdkit import Chem
from rdkit.Chem import AllChem
import argparse
from multiprocessing import Pool


def smiles_to_fingerprint(smiles, fp_type='morgan'):

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    if fp_type == 'morgan':
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
    elif fp_type == 'maccs':
        fp = AllChem.GetMACCSKeysFingerprint(mol)
    elif fp_type == 'topological':
        fp = Chem.RDKFingerprint(mol)
    else:
        raise ValueError("Unsupported fingerprint type")

    return fp.ToBitString() #得到分子指纹的比特字符串


def process_smiles(args):

    smiles, name, fp_type = args
    fp = smiles_to_fingerprint(smiles, fp_type)
    return (name, fp) #返回分子指纹

# 多进程处理
def process_smi_file(input_file, output_file, fp_type='morgan', n_processes=4):

    with open(input_file, 'r') as infile:
        smiles_list = [line.strip().split() for line in infile]

    # 准备并行处理的参数
    args_list = [(parts[0], parts[1] if len(parts) > 1 else "", fp_type) for parts in smiles_list]

    # 多进程并行处理
    with Pool(n_processes) as p:
        results = p.map(process_smiles, args_list)

    # 写入
    with open(output_file, 'w') as outfile:
        for name, fp in results:
            if fp is not None:
                outfile.write(f"{name}\t{fp}\n")
            else:
                print(f"Warning: Could not generate fingerprint for {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate molecular fingerprints from SMILES")
    parser.add_argument("input", help="Input .smi file")
    parser.add_argument("output", help="Output .fpt file")
    parser.add_argument("--fp_type", choices=['morgan', 'maccs', 'topological'], default='morgan',
                        help="Fingerprint type")
    parser.add_argument("--n_processes", type=int, default=4, help="Number of parallel processes")

    args = parser.parse_args()

    process_smi_file(args.input, args.output, args.fp_type, args.n_processes)
    print(f"Fingerprints have been written to {args.output}")


# python smiles_to_fpt.py .smi .fpt
