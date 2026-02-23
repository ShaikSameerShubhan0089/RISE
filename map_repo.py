import os
import json

def generate_file_mapping():
    base_dir = r"c:\Users\S Sameer\Desktop\autism - Copy"
    ignore_dirs = ['.git', '__pycache__', 'node_modules', '.venv', '.gemini', 'tmp', 'brain']
    
    mapping = []
    
    for root, dirs, files in os.walk(base_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.json', '.sql', '.md', '.env', '.txt')):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                size = os.path.getsize(os.path.join(root, file))
                mapping.append({
                    "path": rel_path.replace("\\", "/"),
                    "size": size,
                    "type": file.split('.')[-1]
                })
    
    with open("file_mapping.json", "w") as f:
        json.dump(mapping, f, indent=4)
    print(f"Mapped {len(mapping)} files.")

if __name__ == "__main__":
    generate_file_mapping()
