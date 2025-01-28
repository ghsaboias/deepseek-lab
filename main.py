import os
import xml.etree.ElementTree as ET
from typing import List
from dataclasses import dataclass
from github import Github
from dotenv import load_dotenv
from groq import Groq
import re

# Load environment variables
load_dotenv('.env')

# GitHub setup
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not all([GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, GROQ_API_KEY]):
    raise ValueError("Required environment variables must be set")

# Initialize clients
gh = Github(GITHUB_TOKEN)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@dataclass
class FileContent:
    path: str
    content: str

@dataclass
class PRMetadata:
    title: str
    body: str

@dataclass
class GeneratedContent:
    files: List[FileContent]
    pr: PRMetadata

@dataclass
class FileStructure:
    path: str
    type: str  # 'file' or 'dir'

@dataclass
class FileSummary:
    path: str
    summary: str

def get_repo_structure(repo, path: str = "") -> List[FileStructure]:
    """Recursively get repository file structure without fetching contents."""
    # First check if repo_structure.txt exists
    if os.path.exists("repo_structure.txt"):
        print("Found existing repo_structure.txt")
        with open("repo_structure.txt", "r") as f:
            return [FileStructure(
                path=line.split(' ')[-1].strip(),
                type='dir' if line.strip().endswith('/') else 'file'
            ) for line in f.readlines() if '──' in line]
    
    print("Fetching repository structure from GitHub...")
    structure = []
    try:
        contents = repo.get_contents(path)
        for item in contents:
            if item.type == "file":
                structure.append(FileStructure(path=item.path, type='file'))
            elif item.type == "dir":
                dir_struct = FileStructure(path=item.path, type='dir')
                structure.append(dir_struct)
                try:
                    structure.extend(get_repo_structure(repo, item.path))
                except Exception as e:
                    print(f"Warning: Could not read contents of {item.path} - {e}")
    except Exception as e:
        print(f"Error reading {path}: {e}")
    
    # Write structure to file after fetching
    if structure:
        write_structure_file(structure)
    
    return structure

def generate_structure_tree(structure: List[FileStructure]) -> str:
    """Generate a visual tree structure from file list."""
    if not structure:
        return "📁 Repository Structure\n└── (empty repository)"
    
    # Build directory tree with type information
    root = {"name": "", "children": {}, "is_dir": True}
    for item in structure:
        parts = item.path.split('/')
        current = root
        for part in parts:
            if part not in current["children"]:
                current["children"][part] = {
                    "name": part,
                    "children": {},
                    "is_dir": item.type == 'dir' if part == parts[-1] else True
                }
            current = current["children"][part]

    def build_tree(node, prefix="", is_last=False):
        lines = []
        children = sorted(node["children"].values(), 
                         key=lambda x: (not x["is_dir"], x["name"]))
        
        for i, child in enumerate(children):
            last_child = i == len(children) - 1
            pointer = "└── " if last_child else "├── "
            connector = "    " if last_child else "│   "
            
            # Current node line
            name = child["name"]
            if child["is_dir"] and name:  # Skip root empty name
                name += "/"
            lines.append(f"{prefix}{pointer}{name}")
            
            # Recursively build child lines
            if child["children"]:
                extension = build_tree(child, 
                                     prefix + connector,
                                     last_child)
                lines.extend(extension)
        
        return lines

    return "📁 Repository Structure\n" + '\n'.join(build_tree(root))

def write_structure_file(structure: List[FileStructure], filename: str = "repo_structure.txt"):
    """Write repository structure to a text file."""
    with open(filename, 'w') as f:
        f.write(generate_structure_tree(structure))
    print(f"Structure saved to {filename}")

def generate_summary(structure: List[FileStructure]):
    """Generate a summary of the repository structure"""
    structure_tree = generate_structure_tree(structure)  # Get the actual structure
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""Analyze this repository structure and generate creative ideas and insights about the project:
1. What kind of application is this?
2. What are the key technical components?
3. What interesting features or patterns do you notice?
4. What suggestions would you make for potential improvements or additions?

Repository structure:
{structure_tree}""",
            },
        ],
        model="deepseek-r1-distill-llama-70b",
    )
    return chat_completion.choices[0].message.content

def parse_summary(summary: str) -> str:
    """Parse the summary into a structured format."""
    # remove content between <think> and </think> and any leading newlines
    # summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
    # summary = summary.lstrip()
    return summary

def get_file_content(repo, file_struct: FileStructure) -> FileContent:
    """Get content for a single file from GitHub."""
    try:
        content = repo.get_contents(file_struct.path)
        return FileContent(path=file_struct.path, 
                          content=content.decoded_content.decode())
    except Exception as e:
        print(f"Error fetching {file_struct.path}: {e}")
        return None

def write_summaries_file(summaries: List[FileSummary], filename: str = "summaries.txt"):
    """Write summaries to a text file."""
    with open(filename, 'w') as f:
        f.write("\n".join(f"{s.path}: {s.summary}" for s in summaries))
    print(f"Summaries saved to {filename}")

if __name__ == "__main__":
    print("Starting repository analysis...")
    repo = gh.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPO}")
    
    # Get repository structure (from file or GitHub)
    structure = get_repo_structure(repo)
    if not structure:
        print("Error: Could not fetch repository structure")
        exit(1)
    
    # Generate summary using Groq
    print("Generating repository summary...")
    summary = generate_summary(structure)
    
    # Write summary to file
    with open("summary.txt", "w") as f:
        f.write(parse_summary(summary))
    print("Summary saved to summary.txt")