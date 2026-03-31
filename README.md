# colabfold-apptainer-DRAC

ColabFold (v1.5.5) workflow for running inside an Apptainer container on the Digital Research Alliance of Canada (DRAC) clusters. This pipeline is specifically designed to enable execution on HPC compute nodes—bypassing public server quota limits and eliminating long queue times,  also resolving the "no-internet-access" restriction on HPC compute nodes.

This repository documents how to:
- Pull and flatten a ColabFold Docker image into a `.sif` Apptainer image in your `$SCRATCH`.
- Download the necessary model weights (approx. 5.2GB).
- **Phase 1**: Generate MSAs on a login node (internet access required).
- **Phase 2**: Submit ColabFold GPU folding jobs via SLURM on compute nodes (offline).
- Format multimeric FASTA files and clean up resulting PDB files.

---

## 1. Repository structure

```text
colabfold-apptainer-DRAC/
├─ scripts/
│  ├─ get_msa.sh          # Run on Node has Internet access: Downloads MSA (.a3m) via internet
│  ├─ run_colab.sh        # SLURM script: Runs folding on Compute Node (offline)
│  ├─ format_fasta.py     # Python script: Format multi-chain FASTA files for ColabFold
│  └─ rename_results.sh   # Bash script: Format PDB filenames for the downstream process
└─ README.md              
```

## 2. Requirements
On DRAC (e.g., Narval/Beluga/Cedar):

- Valid Alliance account & allocation

- `apptainer/1.3.5` and `StdEnv/2023` modules

- Sufficient `$SCRATCH` space (avoid `$HOME` due to strict quota limits during container building).

## 3. Build the Apptainer image (`colabfold_1.5.5.sif`)

Since pulling the container and downloading weights can take some time, it is strongly recommended to do this inside a `tmux` session on a fixed login node to avoid interruptions.

1. SSH to a specific Narval login node and confirm the hostname, for example:
```bash
ssh <username>@narval3.alliancecan.ca
hostname
```
Make a note of the hostname (e.g. narval3.alliancecan.ca). You must reconnect to the same node later when re-attaching to `tmux`.

2. Start a `tmux` session:

```bash
tmux new -s build_colabfold
```
3. Inside the `tmux` session, set the Apptainer cache path to `$SCRATCH` prevent the image from being downloaded to the `$HOME` directory, which could lead to insufficient quota and failure.

```bash
cd $SCRATCH
mkdir -p ColabFold && cd ColabFold

export APPTAINER_CACHEDIR=$SCRATCH/.apptainer_cache
export APPTAINER_TMPDIR=$SCRATCH/.apptainer_tmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR

module load StdEnv/2023 apptainer/1.3.5
```
4. Pull the Docker image into a single `.sif` file (takes 5-15 mins):

```bash
apptainer pull colabfold_1.5.5.sif docker://ghcr.io/sokrypton/colabfold:1.5.5-cuda12.2.2
```
5. Download the ColabFold weights:

```bash
apptainer exec --nv \
    -B $PWD/colabfold_weights:/cache \
    -B /etc/pki:/etc/pki \
    colabfold_1.5.5.sif \
    python3 -m colabfold.download
```
(Press `Ctrl+B` then `D` to safely detach from tmux if needed.)

## 4. Run ColabFold Pipeline (Two-Step Offline Mode)
### Step 4.1: Data Preparation
Ensure your complex FASTA files are correctly formatted. ColabFold requires multiple chains to be joined by a colon (e.g., >ComplexName \n SeqA:SeqB). You can use the provided Python script to fix standard multi-chain FASTAs:

```bash
python scripts/format_fasta.py  # Make sure to set your input folder inside the script
```
### Step 4.2: Generate MSA on Login Node (Internet Required)
Since compute nodes lack internet access, they **cannot connect to the MMseqs2 server** to generate MSAs. Therefore, we first execute the MSA search on an internet-connected login node to retrieve the  `.a3m` files. <br>
It is highly recommended to use `tmux` for this step.

```bash
# Start or attach to a tmux session
cd $SCRATCH/ColabFold
chmod +x scripts/get_msa.sh

# Run the MSA generation (The script uses the --msa-only flag to exit after generating and saving the .a3m files, without attempting GPU folding)
./scripts/get_msa.sh
```
Wait until you see "Done" and verify `.a3m` files exist in the `msas/` folder.

### Step 4.3: GPU Folding on Compute Node (Offline)
Submit the job to the SLURM queue. The script will use the pre-generated `.a3m` files and offline weights.

```bash
sbatch scripts/run_colab.sh
```
## 5. Notes & Troubleshooting
- File Renaming : The output structures will have verbose tags (e.g., `_unrelaxed_rank_001_alphafold2_multimer_v3_model_1_seed_000`). Run the provided `scripts/rename_results.sh` to automatically extract the optimal `rank_001` files and clean up their names for seamless downstream analysis (e.g., PRODIGY, PPB-Affinity).
  * *Before:* `PDL1-data-9_unrelaxed_rank_001_alphafold2_multimer_v3_model_5_seed_000.pdb`
  * *After:* `PDL1-data-9.pdb`


- Silent Kills on Login Node: If Apptainer freezes or dies silently while pulling the image, ensure your `APPTAINER_CACHEDIR` is pointed to `$SCRATCH` and not `$HOME`.

- Database Paths: If a job fails, please always inspect the corresponding `.out`/`.err` logs to ensure your `-B` bind paths inside `run_colab.sh` correctly map your `$SCRATCH/colabfold_weights` to `/cache`.



## 6. Related Projects

* **[alphafold2-apptainer-DRAC](https://github.com/DongdongHou006/alphafold2-apptainer-DRAC)**: Our standard AlphaFold2 deployment workflow for DRAC clusters, utilizing local CVMFS databases.

---
For internal use by DRAC users who need a reproducible, offline-capable ColabFold Apptainer workflow.

