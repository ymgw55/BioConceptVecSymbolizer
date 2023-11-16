import argparse
import json
import requests
import pandas as pd
from time import sleep
from tqdm import tqdm
from biothings_client import get_client


def get_args():
    parser = argparse.ArgumentParser(description='symbolize entity')
    parser.add_argument('entity', type=str,
                        help='choose entity in (gene, chemical)')
                        
    return parser.parse_args()


def gene_symbolizer(model, output_path):

    def get_kegg_symbol(kegg_id):
        url = f"http://rest.kegg.jp/get/{kegg_id}"
        response = requests.get(url)
        sleep(1)
        if response.ok:
            data = response.text
            for line in data.split('\n'):
                if line.startswith("SYMBOL"):
                    return [s.strip() for s in
                            line.split(" ", 1)[1].strip().split(',')][0], True
        return None, False

    data = []
    for concept in tqdm(model.keys()):
        if concept[:len('Gene_')] == 'Gene_':
            kegg_id = concept[len('Gene_'):]
            symbol, is_found = get_kegg_symbol(f'hsa:{kegg_id}')
            if is_found:
                data.append({'concept': concept, 'symbol': symbol})
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def chemical_symbolizer(model, output_path):

    md = get_client("drug")

    data = []
    kegg_drug_df = pd.read_csv('data/kegg_drug.csv')
    drug_names = kegg_drug_df['name'].values.tolist()
    for drug_name in tqdm(drug_names):
        try:
            hits_list = list(md.query(drug_name, fetch_all=True))
            sleep(1)
        except Exception as e:
            continue

        is_found = False
        for hits in hits_list:
            if 'umls' in hits and 'mesh' in hits['umls']:
                mesh_list = hits['umls']['mesh']
                if isinstance(mesh_list, list):
                    mesh_list = list(set(mesh_list))
                else:
                    mesh_list = [mesh_list]
                for mesh in mesh_list:
                    cpt = f'Chemical_MESH_{mesh}'
                    if cpt in model:
                        is_found = True
                        data.append({'concept': cpt, 'symbol': drug_name})
                        break
                    else:
                        is_found = False
            if is_found:
                break

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def main():
    args = get_args()
    entity = args.entity
    assert entity in ['gene', 'chemical'], 'entity must be gene or chemical'

    # load embedding
    embedding_path = 'concept_skip.json'
    with open(embedding_path, 'r') as f:
        model = json.load(f)
    output_path = f'{entity}.csv'

    if entity == 'gene':
        gene_symbolizer(model, output_path)
    elif entity == 'chemical':
        chemical_symbolizer(model, output_path)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    main()
