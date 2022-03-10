GitHub: https://github.com/akiyamalab/MEGADOCK

## Images

```sh
docker pull akiyamalab/megadock:cpu
docker pull akiyamalab/megadock:gpu
```

```sh
# Run Interactive Shell
docker run -it akiyamalab/megadock:cpu

# CPU single node (OpenMP parallelization)
docker run akiyamalab/megadock:cpu megadock -R data/1gcq_r.pdb -L data/1gcq_l.pdb -o data/1gcq_r-1gcq_r.out

# GPU single node (GPU parallelization)
docker run --runtime=nvidia akiyamalab/megadock:gpu megadock-gpu -R data/1gcq_r.pdb -L data/1gcq_l.pdb -o data/1gcq_r-1gcq_r.out
```

### Sample
```
megadock -R data/1gcq_r.pdb -L data/1gcq_l.pdb -o data/1gcq_r-1gcq_r.out -t 3 -N 10800

./decoygen data/1gcq_l.1.pdb data/1gcq_l.pdb data/1gcq_r-1gcq_r.out 1
cat data/1gcq_r.pdb data/1gcq_l.1.pdb > data/decoy.1.pdb

#./block data/1gcq_r.pdb B 182-186,189,195-198,204 > data/blocked_1gcq_r.pdb

./ppiscore data/1gcq_r-1gcq_r.out 10800

```


### DV Test
```sh
# Block the HER2 ECD (II) residues (Not 43,44,53,55,56,57,62,63,64,65,74,76,78,92,93,94,95,96,98,100,102,103,104,105,119,120,121,122,123)
# docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu block data/5K33_HER2_Subdomain_II__215-339__Reference_unrelaxed_rank_1_model_1.pdb A 1-42,45-52,54,58-61,66-73,75,77,79-91,97,99,101,106-118,124-125 > data/blocked_5K33_HER2-II.pdb


# Run docking exercise
docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu megadock -R data/5K33_HER2_Subdomain_II__215-339__Reference_unrelaxed_rank_1_model_1.pdb -L data/DV_10933_AlphaFold2_Prediction.pdb -o data/5K33-DV_ref.out -t 3 -N 10800

# Score PPI
docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu ppiscore data/5K33-DV_ref.out 10800
docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu ppiscore data/5K33-DV_ref.out 1

# Rerank using ZRANK
./zrank dock.out 1 10800
./ppiscore dock.out 10800 dock.out.zr.out

# Get best docking run
docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu decoygen data/DV_10933_AlphaFold2_Prediction.1.pdb data/DV_10933_AlphaFold2_Prediction.pdb data/5K33-DV_ref.out 1

docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu decoygen data/DV_10933_AlphaFold2_Prediction.10800.pdb data/DV_10933_AlphaFold2_Prediction.pdb data/5K33-DV_ref.out 10800

# Generate all docking runs interactively
# docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu data/generate_decoys.sh
docker run -v T:\docking_tests:/opt/MEGADOCK/data -it akiyamalab/megadock:cpu

for i in `seq 1 10800`; do ./decoygen DV_10933_AlphaFold2_Prediction.${i}.pdb DV_10933_AlphaFold2_Prediction.pdb 5K33-DV_ref.out $i; done

i=1; cat data/5K33-DV_ref.out | while read LINE; do ./decoygen data/DV_10933_AlphaFold2_Prediction.${i}.pdb data/DV_10933_AlphaFold2_Prediction.pdb data/5K33-DV_ref.out $i; cat data/5K33_HER2_Subdomain_II__215-339__Reference_unrelaxed_rank_1_model_1.pdb data/DV_10933_AlphaFold2_Prediction.${i}.pdb > data/decoy.${i}.pdb; let i=$i+1; done

# Combine PDB files
docker run -v T:\docking_tests:/opt/MEGADOCK/data akiyamalab/megadock:cpu cat data/5K33_HER2_Subdomain_II__215-339__Reference_unrelaxed_rank_1_model_1.pdb data/DV_10933_AlphaFold2_Prediction.1.pdb > data/decoy.1.pdb



```