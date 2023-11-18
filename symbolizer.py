import argparse
import json
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from biothings_client import get_client
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser(description='symbolize entity')
    parser.add_argument('entity', type=str,
                        help='choose entity in (gene, chemical)')
                        
    return parser.parse_args()


def gene_symbolizer(model, output_path):

    def get_cpt2symbol_list(b_idx, batch_queries, output_dir):

        cache_path = output_dir / f'{b_idx}.txt'
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = f.read()
        else:
            url = f"http://rest.kegg.jp/list/{batch_queries}"
            response = requests.get(url)
            sleep(1)
            if response.ok:
                data = response.text
                with open(cache_path, 'w') as f:
                    f.write(data)

        cpt2symbol_list = []
        for line in data.split('\n'):
            if line == '':
                continue
            hsa, *others = line.split('\t')
            symbols = ' '.join(others).split(';')[0]
            symbol = [s.strip() for s in symbols.split(',')][0]
            gene_id = hsa.split(':')[1]
            cpt = f'Gene_{gene_id}'
            cpt2symbol_list.append({'concept': cpt, 'symbol': symbol})
        return cpt2symbol_list

    queries = []
    for concept in tqdm(model.keys()):
        if concept[:len('Gene_')] == 'Gene_':
            kegg_id = concept[len('Gene_'):]
            try:
                kegg_id = int(kegg_id)
            except:
                continue
            query = f'hsa:{kegg_id}'
            queries.append(query)
    queries.sort(key=lambda x: int(x.split(':')[1]))

    output_dir = Path('output/gene')
    output_dir.mkdir(parents=True, exist_ok=True)

    query_num = len(queries)
    data = []
    batch_size = 100
    for b_idx in tqdm(list(range(query_num//batch_size + 1))):
        start = b_idx * batch_size
        end = min((b_idx + 1) * batch_size, query_num)
        batch_queries = queries[start:end]
        batch_queries = '+'.join(batch_queries)
        cpt2symbol_list = get_cpt2symbol_list(b_idx, batch_queries, output_dir)
        data.extend(cpt2symbol_list)

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
