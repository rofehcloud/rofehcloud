import shutil
import os
import subprocess
from colorama import init, Style
import yaml
from cerberus import Validator
import questionary

from rofehcloud.config import Config as config
from rofehcloud.chat import load_data
from rofehcloud.logger import log_message
from rofehcloud.llm import call_llm

init(autoreset=True)


def get_profiles():
    profiles = load_data(config.PROFILES_FILE)
    if profiles is None:
        profiles = []

    return profiles


def check_available_tools(profile):
    if config.SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS:
        log_message(
            "INFO",
            "Skipping the check for available tools (SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS is set to true)",
        )
        return True
    copy_of_all_tools = config.ALL_TOOLS.copy()
    for tool in copy_of_all_tools:
        # check that the tool is available in the path and executable
        log_message("DEBUG", f"Checking if tool {tool} is available in the PATH")
        if not shutil.which(tool):
            log_message("DEBUG", f"Tool {tool} not found in the PATH")
            print(
                Style.BRIGHT + f'Warning: tool "{tool}" not found in the PATH. '
                "We highly recommend to install the tool and restart the app."
            )
            config.ALL_TOOLS.remove(tool)

    return True


def read_profile(profile: str) -> dict:
    profile_file = f"{config.PROFILES_DIR}/{profile}.yaml"
    log_message("INFO", f"Reading profile from file {profile_file}")
    if not os.path.exists(profile_file):
        log_message("ERROR", f"Profile file {profile_file} not found")
        return None

    profile_data = load_data(profile_file)
    if profile_data is None:
        log_message("ERROR", f"Error while reading profile {profile}")
        return None

    if validate_profile(profile_data):
        return profile_data
    else:
        return None


def save_profile(profile: str, profile_data: dict) -> bool:
    profile_file = f"{config.PROFILES_DIR}/{profile}.yaml"
    log_message("INFO", f"Saving profile to {profile_file}")
    if not os.path.exists(config.PROFILES_DIR):
        log_message("INFO", f"Creating directory {config.PROFILES_DIR}")
        os.makedirs(config.PROFILES_DIR)

    if not validate_profile(profile_data):
        return False

    if not os.path.exists(profile_file):
        log_message("INFO", f"Creating profile file {profile_file}")
    else:
        log_message("INFO", f"Overwriting profile file {profile_file}")

    with open(profile_file, "w") as f:
        yaml.dump(profile_data, f)

    return True


def validate_profile(profile_data: str) -> bool:
    schema = {
        "name": {"type": "string", "required": True},
        "description": {"type": "string", "required": True},
        "aws_regions_with_resources": {
            "type": "list",
            "required": False,
            "schema": {"type": "string"},
        },
        "troubleshooting_instructions": {
            "type": "string",
            "required": False,
        },
        "action_instructions": {
            "type": "string",
            "required": False,
        },
        "additional_tools": {
            "type": "list",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "cli_command": {"type": "string", "required": True},
                    "tool_usage_instructions": {"type": "string", "required": True},
                    "additional_arguments": {"type": "string", "required": False},
                },
            },
        },
        "source_code_repositories": {
            "type": "list",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "string",
                        "required": True,
                        "allowed": ["github", "gitlab", "bitbucket"],
                    },
                    "local_directory": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                },
            },
        },
    }

    # Initialize the validator with the schema
    validator = Validator(schema)

    try:
        # Validate data against the schema
        if validator.validate(profile_data):
            log_message("DEBUG", "Profile's YAML content is valid.")
            return True
        else:
            print("YAML content is invalid.")
            print("Errors:", validator.errors)
            return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return False


def scan_repository_structure(repo_path: str) -> str:
    """Scan repository structure and return key information for description generation."""
    if not os.path.exists(repo_path):
        log_message("ERROR", f"Repository path {repo_path} does not exist")
        return ""
    
    repo_info = []
    
    try:
        # Get basic file structure
        result = subprocess.run(
            ["find", repo_path, "-maxdepth", "2", "-type", "f", "-name", "*"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')[:20]  # Limit to first 20 files
            repo_info.append("Key files and directories:")
            for file in files:
                if file:
                    rel_path = os.path.relpath(file, repo_path)
                    repo_info.append(f"  {rel_path}")
        
        # Check for common files that indicate project type
        common_files = [
            "package.json", "requirements.txt", "Cargo.toml", "pom.xml", 
            "go.mod", "Dockerfile", "docker-compose.yml", "Makefile",
            "README.md", "README.rst", ".gitignore", "setup.py",
            "pyproject.toml", "composer.json", "Gemfile"
        ]
        
        found_files = []
        for file in common_files:
            if os.path.exists(os.path.join(repo_path, file)):
                found_files.append(file)
        
        if found_files:
            repo_info.append(f"\nImportant files found: {', '.join(found_files)}")
        
        # Try to read README if it exists
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        for readme in readme_files:
            readme_path = os.path.join(repo_path, readme)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]  # First 1000 chars
                        repo_info.append(f"\nREADME content (first 1000 chars):\n{content}")
                    break
                except Exception as e:
                    log_message("DEBUG", f"Could not read README: {e}")
        
        # Check for source code directories
        src_dirs = []
        for item in os.listdir(repo_path):
            item_path = os.path.join(repo_path, item)
            if os.path.isdir(item_path) and item in ["src", "lib", "app", "api", "frontend", "backend", "server", "client"]:
                src_dirs.append(item)
        
        if src_dirs:
            repo_info.append(f"\nSource code directories: {', '.join(src_dirs)}")
            
    except Exception as e:
        log_message("ERROR", f"Error scanning repository {repo_path}: {e}")
        return f"Error scanning repository: {e}"
    
    return "\n".join(repo_info)


def generate_repository_description(repo_name: str, repo_path: str, repo_type: str) -> str:
    """Generate a description for a repository using LLM based on its contents."""
    log_message("INFO", f"Generating description for repository {repo_name}")
    
    repo_structure = scan_repository_structure(repo_path)
    if not repo_structure:
        return ""
    
    prompt = f"""
Based on the repository structure and files listed below, generate a concise and informative description for this {repo_type} repository named "{repo_name}".

The description should:
1. Identify the main technology stack/language
2. Describe the purpose and functionality of the project
3. Mention key components or features
4. Be 1-2 sentences, suitable for a configuration file

Repository information:
{repo_structure}

Generate only the description text, no additional commentary:
"""
    
    try:
        description = call_llm(prompt, config.LLM_TO_USE)
        if description:
            # Clean up the description
            description = description.strip().replace('\n', ' ')
            # Remove quotes if LLM added them
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1]
            if description.startswith("'") and description.endswith("'"):
                description = description[1:-1]
            return description
        else:
            log_message("ERROR", "Failed to generate repository description")
            return ""
    except Exception as e:
        log_message("ERROR", f"Error generating repository description: {e}")
        return ""


def check_and_generate_missing_repo_descriptions(profile: str, profile_data: dict) -> bool:
    """Check for repositories without descriptions and generate them if needed."""
    if "source_code_repositories" not in profile_data:
        return False
    
    repos_updated = False
    
    for repo in profile_data["source_code_repositories"]:
        repo_name = repo.get("name", "")
        repo_path = repo.get("local_directory", "")
        repo_type = repo.get("type", "")
        repo_description = repo.get("description", "")
        
        # Check if description is missing or empty
        if not repo_description or repo_description.strip() == "":
            print(f"\n{Style.BRIGHT}Repository '{repo_name}' has no description.{Style.RESET_ALL}")
            
            # Check if the repository path exists
            if not os.path.exists(repo_path):
                print(f"Warning: Repository path {repo_path} does not exist. Skipping description generation.")
                continue
            
            print("Analyzing repository structure to generate a description...")
            
            generated_description = generate_repository_description(repo_name, repo_path, repo_type)
            
            if generated_description:
                print(f"\n{Style.BRIGHT}Generated description:{Style.RESET_ALL}")
                print(f'"{generated_description}"')
                
                # Ask user for confirmation
                response = questionary.confirm(
                    f"Would you like to add this description to the '{repo_name}' repository configuration?"
                ).ask()
                
                if response:
                    repo["description"] = generated_description
                    repos_updated = True
                    print(f"Description added for repository '{repo_name}'.")
                else:
                    print(f"Skipped adding description for repository '{repo_name}'.")
            else:
                print(f"Failed to generate description for repository '{repo_name}'. Please add one manually.")
    
    # Save the updated profile if any descriptions were added
    if repos_updated:
        print(f"\n{Style.BRIGHT}Updating profile configuration...{Style.RESET_ALL}")
        if save_profile(profile, profile_data):
            print("Profile updated successfully with new repository descriptions.")
            return True
        else:
            print("Error: Failed to save updated profile.")
            return False
    
    return False
