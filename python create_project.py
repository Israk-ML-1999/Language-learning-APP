import os

# Define the folder structure
project_structure = {
    "gold_tongue_ai": {
        "app": {
            "api": {
                "v1": {
                    "translate.py": ""
                }
            },
            "services": {
                "groq_translate.py": "",
                "tts_gcp.py": ""
            },
            "main.py": ""
        },
        "requirements.txt": "",
        ".env": ""
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

if __name__ == "__main__":
    create_structure(".", project_structure)
    print("✅ Project structure created successfully.")
