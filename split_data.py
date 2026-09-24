import splitfolders

# Input directory with the 38 disease class folders
input_folder = "raw_dataset"

# Output directory where 'train' and 'validation' folders will be generated
output_folder = "dataset"

# 80% train, 20% validation split
splitfolders.ratio(
    input_folder, 
    output=output_folder, 
    seed=42, 
    ratio=(0.8, 0.2), 
    move=False  # Copies files so original images stay safe in raw_dataset
)

print("Splitting complete! Check the 'dataset/' folder.")