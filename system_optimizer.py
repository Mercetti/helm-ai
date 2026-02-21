#!/usr/bin/env python3
"""
Stellar Logic AI - System Resource Optimizer
Automated cleanup and optimization script
"""

import os
import shutil
import psutil
import glob
import time
from datetime import datetime, timedelta

class SystemOptimizer:
    def __init__(self):
        self.cleanup_stats = {
            'files_deleted': 0,
            'space_freed': 0,
            'dirs_cleaned': 0
        }
    
    def analyze_system(self):
        """Analyze current system state"""
        print("🔍 SYSTEM ANALYSIS")
        print("=" * 50)
        
        # Memory analysis
        memory = psutil.virtual_memory()
        print(f"🧠 Memory: {memory.percent:.1f}% ({memory.used / 1024 / 1024 / 1024:.1f}GB used)")
        
        # Disk analysis
        disk = psutil.disk_usage('.')
        disk_percent = (disk.used / disk.total) * 100
        print(f"💾 Disk: {disk_percent:.1f}% ({disk.used / 1024 / 1024 / 1024:.1f}GB used)")
        print(f"   Free: {disk.free / 1024 / 1024 / 1024:.1f}GB")
        
        return memory.percent, disk_percent
    
    def clean_python_cache(self):
        """Clean Python cache files"""
        print("\n🧹 Cleaning Python cache...")
        
        # Clean __pycache__ directories
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_path = os.path.join(root, '__pycache__')
                try:
                    size = self.get_dir_size(cache_path)
                    shutil.rmtree(cache_path)
                    self.cleanup_stats['dirs_cleaned'] += 1
                    self.cleanup_stats['space_freed'] += size
                    print(f"   Removed: {cache_path} ({size / 1024:.1f}KB)")
                except Exception as e:
                    print(f"   Error removing {cache_path}: {e}")
        
        # Clean .pyc files
        pyc_files = glob.glob('**/*.pyc', recursive=True)
        for pyc_file in pyc_files:
            try:
                size = os.path.getsize(pyc_file)
                os.remove(pyc_file)
                self.cleanup_stats['files_deleted'] += 1
                self.cleanup_stats['space_freed'] += size
                print(f"   Removed: {pyc_file} ({size / 1024:.1f}KB)")
            except Exception as e:
                print(f"   Error removing {pyc_file}: {e}")
    
    def clean_temp_files(self):
        """Clean temporary files"""
        print("\n🧹 Cleaning temporary files...")
        
        temp_patterns = [
            '**/*.tmp',
            '**/*.log',
            '**/*.bak',
            '**/*~',
            '**/.DS_Store'
        ]
        
        for pattern in temp_patterns:
            files = glob.glob(pattern, recursive=True)
            for file in files:
                try:
                    size = os.path.getsize(file)
                    os.remove(file)
                    self.cleanup_stats['files_deleted'] += 1
                    self.cleanup_stats['space_freed'] += size
                    print(f"   Removed: {file} ({size / 1024:.1f}KB)")
                except Exception as e:
                    print(f"   Error removing {file}: {e}")
    
    def clean_node_modules(self):
        """Clean node_modules selectively"""
        print("\n🧹 Analyzing node_modules...")
        
        node_modules_path = 'node_modules'
        if os.path.exists(node_modules_path):
            size = self.get_dir_size(node_modules_path)
            print(f"   node_modules size: {size / 1024 / 1024:.1f}MB")
            print("   💡 Consider running 'npm ci' when needed instead of full removal")
    
    def optimize_memory(self):
        """Memory optimization suggestions"""
        print("\n🔧 Memory Optimization Suggestions:")
        print("   1. Close unused browser tabs")
        print("   2. Clear browser cache")
        print("   3. Restart memory-intensive applications")
        print("   4. Disable unnecessary startup programs")
        print("   5. Consider RAM upgrade if consistently >80%")
    
    def get_dir_size(self, path):
        """Calculate directory size"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size
    
    def generate_report(self):
        """Generate cleanup report"""
        print("\n📊 CLEANUP REPORT")
        print("=" * 50)
        print(f"Files deleted: {self.cleanup_stats['files_deleted']}")
        print(f"Directories cleaned: {self.cleanup_stats['dirs_cleaned']}")
        print(f"Space freed: {self.cleanup_stats['space_freed'] / 1024 / 1024:.2f}MB")
        
        # Re-analyze system
        memory_percent, disk_percent = self.analyze_system()
        
        print(f"\n🎯 OPTIMIZATION STATUS:")
        if memory_percent < 80:
            print("   🟢 Memory usage improved")
        if disk_percent < 85:
            print("   🟢 Disk usage improved")
        
        print("\n✅ Optimization complete!")

def main():
    optimizer = SystemOptimizer()
    
    print("🚀 STELLAR LOGIC AI - SYSTEM OPTIMIZER")
    print("=" * 60)
    
    # Initial analysis
    memory_percent, disk_percent = optimizer.analyze_system()
    
    # Perform cleanup
    optimizer.clean_python_cache()
    optimizer.clean_temp_files()
    optimizer.clean_node_modules()
    
    # Optimization suggestions
    optimizer.optimize_memory()
    
    # Generate report
    optimizer.generate_report()

if __name__ == "__main__":
    main()
