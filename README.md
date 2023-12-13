# BioConceptVecSymbolizer

Using the following files, you can convert BioConceptVec concepts to symbols.
- gene.csv
- chemical.csv

## Reproduction

### Download BioConceptVec Skip-gram

```bash
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/BioConceptVec/concept_skip.json
```

### Setup
```bash
python -m pip install biothings_client
```

### Symbolize
```bash
$ python symbolizer.py -h
usage: symbolizer.py [-h] entity

symbolize entity

positional arguments:
  entity      choose entity in (gene, chemical)
```

For example, `gene.csv` is generated as follows
```bash
$ python symbolizer.py gene
```

## TODO
We are looking for contributors to write code for converting other entities such as Disease, DNAMutation, and ProteinMutation. Feel free to send a pull request.

## References

1. **BioConceptVec Original Paper**: 
   "BioConceptVec: Creating and Evaluating Literature-Based Biomedical Concept Embeddings on a Large Scale"
   PLOS Computational Biology.
   Available at: [https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007617](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007617)

2. **BioConceptVec Repository**: 
   GitHub repository for BioConceptVec.
   Available at: [https://github.com/ncbi/BioConceptVec](https://github.com/ncbi/BioConceptVec)

3. **biothings_client Repository**: 
   GitHub repository for the biothings_client Python package.
   Available at: [https://github.com/biothings/biothings_client.py](https://github.com/biothings/biothings_client.py)
