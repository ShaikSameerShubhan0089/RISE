import os
import re
from pathlib import Path

def extract_routes(router_dir):
    router_files = Path(router_dir).glob("*.py")
    all_routes = {}

    for file in router_files:
        if file.name == "__init__.py":
            continue
            
        with open(file, "r") as f:
            content = f.read()
            
        # Regex to find @router.METHOD("path"...)
        pattern = r'@router\.(get|post|put|delete|patch)\("([^"]*)"(?:,.*?)?\)\s+async def (\w+)\((.*?)\):'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        routes = []
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            func_name = match.group(3)
            args = match.group(4).replace("\n", " ").strip()
            
            # Extract response_model if present
            resp_pattern = r'response_model=(schemas\.\w+|List\[schemas\.\w+\])'
            resp_match = re.search(resp_pattern, match.group(0))
            response_model = resp_match.group(1) if resp_match else "None"
            
            # Extract dependencies (RBAC)
            rbac_pattern = r'RoleChecker\(\[(.*?)\]\)'
            rbac_match = re.search(rbac_pattern, args)
            roles = rbac_match.group(1).replace("'", "") if rbac_match else "None"
            
            routes.append({
                "method": method,
                "path": path,
                "function": func_name,
                "response_model": response_model,
                "roles": roles
            })
            
        all_routes[file.name] = routes
        
    return all_routes

if __name__ == "__main__":
    router_dir = "backend/routers"
    routes = extract_routes(router_dir)
    
    with open("api_endpoints_extraction.md", "w") as f:
        for file, endpoints in routes.items():
            f.write(f"## Router: {file}\n\n")
            f.write("| Method | Path | Function | Response Model | RBAC Roles |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            for ep in endpoints:
                f.write(f"| {ep['method']} | {ep['path']} | {ep['function']} | {ep['response_model']} | {ep['roles']} |\n")
            f.write("\n")
            
    print("API extraction complete. Saved to api_endpoints_extraction.md")
