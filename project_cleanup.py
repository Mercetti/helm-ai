#!/usr/bin/env python3
"""
Stellar Logic AI - Project Cleanup & Organization Tool
Identifies orphaned code, unused files, and optimization opportunities
"""

import os
import json
import ast
import re
from pathlib import Path
from collections import defaultdict, Counter
import sqlite3
from datetime import datetime

class ProjectCleanupAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.python_files = []
        self.html_files = []
        self.js_files = []
        self.css_files = []
        self.database_files = []
        self.image_files = []
        self.config_files = []
        self.doc_files = []
        
        # Analysis results
        self.imports = defaultdict(set)
        self.exports = defaultdict(set)
        self.function_definitions = defaultdict(set)
        self.class_definitions = defaultdict(set)
        self.html_references = defaultdict(set)
        self.js_references = defaultdict(set)
        self.orphaned_files = []
        self.unused_imports = defaultdict(list)
        self.duplicate_files = []
        self.large_files = []
        self.old_files = []
        
    def scan_project(self):
        """Scan entire project structure"""
        print("🔍 Scanning project structure...")
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and common ignore patterns
                if self._should_ignore_file(file_path):
                    continue
                    
                self._categorize_file(file_path)
        
        print(f"📁 Found {len(self.python_files)} Python files")
        print(f"🌐 Found {len(self.html_files)} HTML files")
        print(f"📜 Found {len(self.js_files)} JavaScript files")
        print(f"🎨 Found {len(self.css_files)} CSS files")
        print(f"🗄️ Found {len(self.database_files)} Database files")
        print(f"🖼️ Found {len(self.image_files)} Image files")
        print(f"⚙️ Found {len(self.config_files)} Config files")
        print(f"📚 Found {len(self.doc_files)} Documentation files")
    
    def _should_ignore_file(self, file_path):
        """Check if file should be ignored"""
        ignore_patterns = [
            '__pycache__', '.git', 'node_modules', '.vscode', 
            '.pytest_cache', '.coverage', 'dist', 'build',
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store'
        ]
        
        path_str = str(file_path)
        for pattern in ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def _categorize_file(self, file_path):
        """Categorize file by type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.py':
            self.python_files.append(file_path)
        elif suffix == '.html':
            self.html_files.append(file_path)
        elif suffix == '.js':
            self.js_files.append(file_path)
        elif suffix == '.css':
            self.css_files.append(file_path)
        elif suffix in ['.db', '.sqlite', '.sqlite3']:
            self.database_files.append(file_path)
        elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
            self.image_files.append(file_path)
        elif suffix in ['.json', '.yaml', '.yml', '.env', '.ini', '.toml']:
            self.config_files.append(file_path)
        elif suffix in ['.md', '.txt', '.rst']:
            self.doc_files.append(file_path)
    
    def analyze_python_files(self):
        """Analyze Python files for imports, functions, classes"""
        print("🐍 Analyzing Python files...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                    self._extract_python_info(py_file, tree)
                except SyntaxError:
                    print(f"⚠️ Syntax error in {py_file}")
                    continue
                    
            except Exception as e:
                print(f"⚠️ Error reading {py_file}: {e}")
    
    def _extract_python_info(self, file_path, tree):
        """Extract imports, functions, classes from AST"""
        file_key = str(file_path.relative_to(self.project_root))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[file_key].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports[file_key].add(node.module)
            elif isinstance(node, ast.FunctionDef):
                self.function_definitions[file_key].add(node.name)
            elif isinstance(node, ast.ClassDef):
                self.class_definitions[file_key].add(node.name)
    
    def analyze_html_files(self):
        """Analyze HTML files for references"""
        print("🌐 Analyzing HTML files...")
        
        for html_file in self.html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_key = str(html_file.relative_to(self.project_root))
                
                # Extract script references
                scripts = re.findall(r'src=["\']([^"\']+)["\']', content)
                for script in scripts:
                    self.html_references[file_key].add(script)
                
                # Extract link references
                links = re.findall(r'href=["\']([^"\']+)["\']', content)
                for link in links:
                    self.html_references[file_key].add(link)
                    
            except Exception as e:
                print(f"⚠️ Error reading {html_file}: {e}")
    
    def analyze_js_files(self):
        """Analyze JavaScript files for references"""
        print("📜 Analyzing JavaScript files...")
        
        for js_file in self.js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_key = str(js_file.relative_to(self.project_root))
                
                # Extract import/require statements
                imports = re.findall(r'(?:import|require)\s*\(?["\']([^"\']+)["\']', content)
                for imp in imports:
                    self.js_references[file_key].add(imp)
                    
            except Exception as e:
                print(f"⚠️ Error reading {js_file}: {e}")
    
    def find_orphaned_files(self):
        """Find files that are not referenced by any other file"""
        print("🔍 Finding orphaned files...")
        
        all_references = set()
        
        # Collect all references
        for refs in self.html_references.values():
            all_references.update(refs)
        for refs in self.js_references.values():
            all_references.update(refs)
        
        # Check each file type
        for js_file in self.js_files:
            rel_path = str(js_file.relative_to(self.project_root))
            if rel_path not in all_references and not rel_path.startswith('src/'):
                self.orphaned_files.append(('JavaScript', rel_path, js_file.stat().st_size))
        
        for css_file in self.css_files:
            rel_path = str(css_file.relative_to(self.project_root))
            if rel_path not in all_references:
                self.orphaned_files.append(('CSS', rel_path, css_file.stat().st_size))
    
    def find_duplicate_files(self):
        """Find potential duplicate files"""
        print("🔍 Finding duplicate files...")
        
        file_hashes = defaultdict(list)
        
        # Check Python files for duplicates
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple hash based on content length and first/last lines
                content_hash = f"{len(content)}_{content[:100]}_{content[-100:]}"
                file_hashes[content_hash].append(py_file)
            except:
                continue
        
        # Find duplicates
        for hash_val, files in file_hashes.items():
            if len(files) > 1:
                self.duplicate_files.append(files)
    
    def find_large_files(self):
        """Find large files that might need optimization"""
        print("🔍 Finding large files...")
        
        all_files = self.python_files + self.html_files + self.js_files + self.doc_files
        
        for file_path in all_files:
            try:
                size = file_path.stat().st_size
                if size > 1024 * 1024:  # > 1MB
                    self.large_files.append((str(file_path.relative_to(self.project_root)), size))
            except:
                continue
    
    def find_old_files(self):
        """Find files that haven't been modified recently"""
        print("🔍 Finding old files...")
        
        cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days ago
        
        all_files = self.python_files + self.html_files + self.js_files
        
        for file_path in all_files:
            try:
                mtime = file_path.stat().st_mtime
                if mtime < cutoff_date:
                    self.old_files.append((str(file_path.relative_to(self.project_root)), mtime))
            except:
                continue
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        print("\n" + "="*80)
        print("🧹 STELLAR LOGIC AI - PROJECT CLEANUP REPORT")
        print("="*80)
        
        # Project Overview
        print(f"\n📊 PROJECT OVERVIEW:")
        print(f"   Total Files: {len(list(self.project_root.rglob('*')))}")
        print(f"   Python Files: {len(self.python_files)}")
        print(f"   HTML Files: {len(self.html_files)}")
        print(f"   JavaScript Files: {len(self.js_files)}")
        print(f"   CSS Files: {len(self.css_files)}")
        print(f"   Database Files: {len(self.database_files)}")
        print(f"   Image Files: {len(self.image_files)}")
        print(f"   Config Files: {len(self.config_files)}")
        print(f"   Documentation: {len(self.doc_files)}")
        
        # Orphaned Files
        if self.orphaned_files:
            print(f"\n🗑️ ORPHANED FILES ({len(self.orphaned_files)}):")
            total_orphaned_size = 0
            for file_type, file_path, size in self.orphaned_files:
                print(f"   {file_type}: {file_path} ({size:,} bytes)")
                total_orphaned_size += size
            print(f"   Total orphaned size: {total_orphaned_size:,} bytes ({total_orphaned_size/1024/1024:.2f} MB)")
        else:
            print(f"\n✅ No orphaned files found")
        
        # Duplicate Files
        if self.duplicate_files:
            print(f"\n🔄 DUPLICATE FILES ({len(self.duplicate_files)} groups):")
            for i, files in enumerate(self.duplicate_files, 1):
                print(f"   Group {i}:")
                for file_path in files:
                    print(f"     - {file_path.relative_to(self.project_root)}")
        else:
            print(f"\n✅ No duplicate files found")
        
        # Large Files
        if self.large_files:
            print(f"\n📏 LARGE FILES ({len(self.large_files)}):")
            for file_path, size in sorted(self.large_files, key=lambda x: x[1], reverse=True):
                print(f"   {file_path} ({size/1024/1024:.2f} MB)")
        else:
            print(f"\n✅ No large files found")
        
        # Old Files
        if self.old_files:
            print(f"\n📅 OLD FILES ({len(self.old_files)}):")
            for file_path, mtime in sorted(self.old_files, key=lambda x: x[1]):
                mod_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                print(f"   {file_path} (modified: {mod_date})")
        else:
            print(f"\n✅ No old files found")
        
        # Recommendations
        print(f"\n💡 CLEANUP RECOMMENDATIONS:")
        
        if self.orphaned_files:
            print(f"   🗑️ Remove {len(self.orphaned_files)} orphaned files to free up space")
        
        if self.duplicate_files:
            print(f"   🔄 Review {len(self.duplicate_files)} duplicate file groups")
        
        if self.large_files:
            print(f"   📏 Optimize {len(self.large_files)} large files")
        
        if self.old_files:
            print(f"   📅 Review {len(self.old_files)} files not modified in 30+ days")
        
        # Save detailed report
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """Save detailed cleanup report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'project_stats': {
                'total_files': len(list(self.project_root.rglob('*'))),
                'python_files': len(self.python_files),
                'html_files': len(self.html_files),
                'js_files': len(self.js_files),
                'css_files': len(self.css_files),
                'database_files': len(self.database_files),
                'image_files': len(self.image_files),
                'config_files': len(self.config_files),
                'doc_files': len(self.doc_files)
            },
            'orphaned_files': [
                {'type': t, 'path': p, 'size': s} for t, p, s in self.orphaned_files
            ],
            'duplicate_files': [
                [str(f.relative_to(self.project_root)) for f in files] 
                for files in self.duplicate_files
            ],
            'large_files': [
                {'path': p, 'size': s} for p, s in self.large_files
            ],
            'old_files': [
                {'path': p, 'mtime': m} for p, m in self.old_files
            ]
        }
        
        report_file = self.project_root / 'project_cleanup_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main cleanup analysis function"""
    project_root = Path(__file__).parent
    analyzer = ProjectCleanupAnalyzer(project_root)
    
    print("🧹 Starting Stellar Logic AI Project Cleanup Analysis...")
    
    # Run analysis
    analyzer.scan_project()
    analyzer.analyze_python_files()
    analyzer.analyze_html_files()
    analyzer.analyze_js_files()
    analyzer.find_orphaned_files()
    analyzer.find_duplicate_files()
    analyzer.find_large_files()
    analyzer.find_old_files()
    
    # Generate report
    analyzer.generate_cleanup_report()
    
    print(f"\n✅ Project cleanup analysis complete!")

if __name__ == '__main__':
    main()
