#!/usr/bin/env python3
"""
Architecture Audit Script for Multi-Repository Systems
Generates Safe Milestone mapping for 78 subdirectories.
"""

import os
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class RepositoryAnalyzer:
    """Analyzes individual repositories for architecture mapping."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo_name = repo_path.name
        self.metadata = {
            "name": self.repo_name,
            "path": str(repo_path),
            "summary": "",
            "dependencies": set(),
            "core_logic": [],
            "environment": [],
            "expected_outputs": [],
            "file_count": 0,
            "language_distribution": {}
        }

    def extract_readme_summary(self) -> str:
        """Extract brief summary from README.md."""
        readme_path = self.repo_path / "README.md"
        if not readme_path.exists():
            return "No README found"
        
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)  # First 500 chars
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                return ' '.join(lines[:3]) or "README exists but is empty"
        except Exception as e:
            return f"Error reading README: {type(e).__name__}"

    def analyze_python_file(self, file_path: Path) -> Tuple[Set[str], List[str], List[str]]:
        """Parse Python file for imports, functions, and output patterns."""
        dependencies = set()
        core_logic = []
        outputs = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract imports via regex (faster than AST for large files)
                import_patterns = [
                    r'^\s*import\s+(\w+)',
                    r'^\s*from\s+(\w+)',
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    dependencies.update(matches)
                
                # Parse with AST for function/class names
                try:
                    tree = ast.parse(content, timeout=2)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            core_logic.append(f"func:{node.name}")
                        elif isinstance(node, ast.ClassDef):
                            core_logic.append(f"class:{node.name}")
                except (SyntaxError, ValueError, TimeoutError):
                    pass
                
                # Detect output patterns
                output_patterns = [
                    (r'\.to_csv\(', 'CSV export'),
                    (r'json\.dump\(', 'JSON output'),
                    (r'\.write\(', 'File write'),
                    (r'\.dump\(', 'Serialization'),
                    (r'return\s+\{', 'Dict return'),
                    (r'print\(', 'Console output'),
                ]
                for pattern, label in output_patterns:
                    if re.search(pattern, content):
                        outputs.append(label)
        
        except Exception:
            pass
        
        return dependencies, list(set(core_logic))[:5], list(set(outputs))

    def analyze_cpp_file(self, file_path: Path) -> Tuple[Set[str], List[str], List[str]]:
        """Parse C++ file for includes, functions, and output patterns."""
        dependencies = set()
        core_logic = []
        outputs = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract includes
                includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
                dependencies.update(includes)
                
                # Extract function definitions
                func_patterns = re.findall(r'(?:void|int|bool|double|auto)\s+(\w+)\s*\(', content)
                core_logic = [f"func:{f}" for f in func_patterns[:5]]
                
                # Detect output patterns
                if re.search(r'std::cout|printf|cout\s*<<', content):
                    outputs.append('Console output')
                if re.search(r'std::ofstream|fopen|fwrite', content):
                    outputs.append('File output')
                if re.search(r'json|JSON', content, re.IGNORECASE):
                    outputs.append('JSON output')
        
        except Exception:
            pass
        
        return dependencies, core_logic, outputs

    def detect_environment(self, dependencies: Set[str]) -> List[str]:
        """Infer runtime environment from dependencies."""
        environment = []
        
        web_libs = {'flask', 'django', 'fastapi', 'bottle', 'tornado', 'aiohttp'}
        api_libs = {'requests', 'httpx', 'urllib', 'aiohttp'}
        cli_libs = {'argparse', 'click', 'typer', 'docopt'}
        data_libs = {'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'torch'}
        db_libs = {'sqlalchemy', 'psycopg2', 'pymongo', 'sqlite3', 'mysql'}
        async_libs = {'asyncio', 'aiohttp', 'trio', 'gevent', 'threading', 'multiprocessing'}
        
        if web_libs & dependencies:
            environment.append('Web Server')
        if api_libs & dependencies:
            environment.append('API Client')
        if cli_libs & dependencies:
            environment.append('CLI Tool')
        if data_libs & dependencies:
            environment.append('Data Processing')
        if db_libs & dependencies:
            environment.append('Database')
        if async_libs & dependencies:
            environment.append('Async/Background')
        
        return environment or ['Standard Library']

    def scan_repository(self) -> Dict:
        """Main scan routine for the repository."""
        # Extract README summary
        self.metadata["summary"] = self.extract_readme_summary()
        
        all_dependencies = set()
        all_core_logic = []
        all_outputs = []
        lang_dist = defaultdict(int)
        
        # Scan all Python and C++ files
        for ext, func in [('.py', self.analyze_python_file), ('.cpp', self.analyze_cpp_file)]:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                if '.git' in file_path.parts or '__pycache__' in file_path.parts:
                    continue
                
                lang_dist[ext] += 1
                deps, logic, outputs = func(file_path)
                all_dependencies.update(deps)
                all_core_logic.extend(logic)
                all_outputs.extend(outputs)
        
        # Compile metadata
        self.metadata["dependencies"] = sorted(list(all_dependencies))
        self.metadata["core_logic"] = list(set(all_core_logic))[:10]
        self.metadata["expected_outputs"] = list(set(all_outputs))
        self.metadata["environment"] = self.detect_environment(all_dependencies)
        self.metadata["file_count"] = sum(lang_dist.values())
        self.metadata["language_distribution"] = dict(lang_dist)
        
        return self.metadata


class ArchitectureMapper:
    """Orchestrates the full architecture audit."""

    def __init__(self, root_path: Path = Path.cwd()):
        self.root_path = root_path
        self.repositories = []
        self.convergence_matrix = []

    def scan_all_repositories(self) -> List[Dict]:
        """Scan all subdirectories as repositories."""
        subdirs = sorted([
            d for d in self.root_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ])
        
        print(f"🔍 Scanning {len(subdirs)} repositories...")
        
        for idx, repo_dir in enumerate(subdirs, 1):
            print(f"  [{idx}/{len(subdirs)}] {repo_dir.name}...", end=' ', flush=True)
            
            analyzer = RepositoryAnalyzer(repo_dir)
            metadata = analyzer.scan_repository()
            self.repositories.append(metadata)
            
            print("✓")
        
        return self.repositories

    def generate_architecture_map(self) -> Dict:
        """Generate comprehensive architecture map JSON."""
        arch_map = {
            "metadata": {
                "total_repositories": len(self.repositories),
                "scan_root": str(self.root_path),
                "version": "1.0"
            },
            "repositories": self.repositories,
            "dependency_graph": self._build_dependency_graph(),
            "environment_distribution": self._analyze_environment_distribution(),
            "redundancy_analysis": self._identify_redundancies()
        }
        return arch_map

    def _build_dependency_graph(self) -> Dict:
        """Build dependency relationships between repositories."""
        graph = defaultdict(list)
        all_deps = defaultdict(set)
        
        for repo in self.repositories:
            for dep in repo['dependencies']:
                all_deps[dep].add(repo['name'])
        
        # Find repos sharing dependencies
        for dep, repos in all_deps.items():
            if len(repos) > 1:
                for repo in repos:
                    graph[repo].extend(list(repos - {repo}))
        
        return {repo: list(set(deps)) for repo, deps in graph.items()}

    def _analyze_environment_distribution(self) -> Dict:
        """Analyze distribution of environment types."""
        env_dist = defaultdict(list)
        for repo in self.repositories:
            for env in repo['environment']:
                env_dist[env].append(repo['name'])
        
        return {env: repos for env, repos in env_dist.items()}

    def _identify_redundancies(self) -> Dict:
        """Identify potentially redundant repositories."""
        redundancy_candidates = []
        
        for i, repo1 in enumerate(self.repositories):
            for repo2 in self.repositories[i+1:]:
                # Check for similar core logic and dependencies
                shared_deps = set(repo1['dependencies']) & set(repo2['dependencies'])
                if len(shared_deps) >= 5:
                    redundancy_candidates.append({
                        "repo1": repo1['name'],
                        "repo2": repo2['name'],
                        "shared_dependencies": list(shared_deps),
                        "similarity_score": len(shared_deps) / max(len(repo1['dependencies']), len(repo2['dependencies']))
                    })
        
        return sorted(redundancy_candidates, key=lambda x: x['similarity_score'], reverse=True)[:10]

    def generate_convergence_matrix(self) -> str:
        """Generate Markdown table of convergence matrix."""
        md_lines = [
            "# Architecture Convergence Matrix",
            "",
            "| Repository | Core Logic | Environment/Dependencies | Expected Output |",
            "|---|---|---|---|",
        ]
        
        for repo in self.repositories:
            core = ', '.join(repo['core_logic'][:2]) or 'N/A'
            env = ', '.join(repo['environment']) or 'N/A'
            deps = ', '.join(repo['dependencies'][:3]) if repo['dependencies'] else 'N/A'
            output = ', '.join(repo['expected_outputs']) or 'N/A'
            
            row = f"| `{repo['name']}` | {core} | {env}<br>_Deps: {deps}_ | {output} |"
            md_lines.append(row)
        
        return '\n'.join(md_lines)

    def save_outputs(self):
        """Save architecture map and convergence matrix to disk."""
        # Generate architecture map
        arch_map = self.generate_architecture_map()
        
        map_file = self.root_path / "architecture_map.json"
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(arch_map, f, indent=2, default=str)
        print(f"✓ Architecture map saved: {map_file}")
        
        # Generate convergence matrix
        convergence_md = self.generate_convergence_matrix()
        
        matrix_file = self.root_path / "convergence_matrix.md"
        with open(matrix_file, 'w', encoding='utf-8') as f:
            f.write(convergence_md)
        print(f"✓ Convergence matrix saved: {matrix_file}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("🏗️  Architecture Audit: Safe Milestone Mapper")
    print("=" * 60)
    print()
    
    mapper = ArchitectureMapper()
    
    # Scan all repositories
    mapper.scan_all_repositories()
    print()
    
    # Save outputs
    mapper.save_outputs()
    print()
    print("=" * 60)
    print(f"✅ Audit Complete! {len(mapper.repositories)} repositories analyzed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
