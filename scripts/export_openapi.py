import json
import os
import yaml
from app.main import app

def export_openapi():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    schema = app.openapi()
    
    json_path = os.path.join(docs_dir, "openapi.json")
    with open(json_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Exported OpenAPI JSON to {json_path}")
    
    yaml_path = os.path.join(docs_dir, "openapi.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(schema, f, sort_keys=False)
    print(f"Exported OpenAPI YAML to {yaml_path}")

if __name__ == "__main__":
    export_openapi()
