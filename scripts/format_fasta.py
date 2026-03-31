import os
import glob
# --- setting your input folder path ---
# Make sure this points to your folder where you store fasta files
input_folder = "/content/drive/MyDrive/FASTA Colab/Batch_5"
# ---------------------------
print(f"Checking and fixing FASTA format: {input_folder}")
fasta_files = glob.glob(os.path.join(input_folder, "*.fasta"))
for file_path in fasta_files:
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # Parse existing >A >B format
    seqs = []
    current_seq = []
    name = os.path.basename(file_path).replace(".fasta", "")
    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            if current_seq:
                seqs.append("".join(current_seq))
                current_seq = []
        else:
            current_seq.append(line)
    if current_seq:
        seqs.append("".join(current_seq))
    # If multiple sequences (complex) are detected and not in colon format
    if len(seqs) > 1:
        print(f"  Fixing: {name} (Found {len(seqs)} chains, merging...)")
        # Convert to ColabFold format: >Name \n SeqA:SeqB
        new_header = f">{name}"
        new_seq = ":".join(seqs)  # Join with colon
        # Overwrite original file
        with open(file_path, 'w') as f:
            f.write(f"{new_header}\n")
            f.write(f"{new_seq}\n")
    else:
        # Check if already in colon format
        if ":" in seqs[0]:
            print(f"  Skipping: {name} (Already in correct complex format)")
        else:
            print(f"⚠️ Warning: {name} has only one sequence, cannot form a complex!")
print("\n FASTA format fixing complete!")