# Copy the result .pdb file to new deirctory: results_rank001

mkdir -p results_rank001 && find results/ -name "*rank_001*.pdb" -type f -exec cp {} results_rank001/ \;

# Rename the .pdb file in the results_rank001 directory

cd result_rank001
            
for file in *unrelaxed_rank_001*; do
    new_name=$(echo "$file" | sed -E 's/_unrelaxed_rank_001_alphafold2_multimer_v3_model_[1-5]_seed_000//')
                
    mv "$file" "$new_name"
                
    echo "Renamed: $file -> $new_name"
done
