import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def get_python_packages():
    """Get installed Python packages."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[2:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()][:20]  # Top 20
    except:
        pass
    return []

def categorize_commands():
    """Categorize available commands by type."""
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    
    categories = {
        'Development Tools': set(),
        'Version Control': set(),
        'Package Managers': set(),
        'Network Tools': set(),
        'System Tools': set(),
        'Text/File Tools': set(),
        'Databases': set(),
        'Cloud/DevOps': set(),
        'Multimedia': set(),
        'Other Tools': set()
    }
    
    # Define patterns for categorization
    patterns = {
        'Development Tools': ['python', 'node', 'npm', 'java', 'javac', 'gcc', 'g++', 'make', 'cmake', 'dotnet', 'go', 'rust', 'cargo', 'ruby', 'php', 'perl', 'R', 'scala', 'kotlin'],
        'Version Control': ['git', 'svn', 'hg', 'bzr', 'cvs'],
        'Package Managers': ['pip', 'conda', 'npm', 'yarn', 'brew', 'choco', 'apt', 'yum', 'pacman', 'gem', 'composer'],
        'Network Tools': ['curl', 'wget', 'ssh', 'scp', 'rsync', 'ping', 'traceroute', 'nslookup', 'dig', 'netstat', 'telnet', 'ftp', 'sftp'],
        'System Tools': ['ps', 'top', 'htop', 'kill', 'killall', 'df', 'du', 'mount', 'umount', 'lsof', 'netstat', 'systemctl', 'service'],
        'Text/File Tools': ['grep', 'sed', 'awk', 'sort', 'uniq', 'head', 'tail', 'cat', 'less', 'more', 'vim', 'nano', 'emacs', 'code', 'subl'],
        'Databases': ['mysql', 'psql', 'sqlite3', 'mongo', 'redis-cli', 'influx'],
        'Cloud/DevOps': ['docker', 'kubectl', 'helm', 'terraform', 'ansible', 'vagrant', 'aws', 'gcloud', 'azure', 'heroku'],
        'Multimedia': ['ffmpeg', 'convert', 'gimp', 'inkscape', 'vlc']
    }
    
    # Scan PATH for executables
    found_commands = set()
    for path_dir in path_dirs:
        try:
            path_obj = Path(path_dir)
            if path_obj.exists() and path_obj.is_dir():
                for file in path_obj.iterdir():
                    if file.is_file() and os.access(file, os.X_OK):
                        cmd_name = file.stem.lower()  # Remove extension
                        found_commands.add(cmd_name)
        except (PermissionError, OSError):
            continue
    
    # Categorize found commands
    for category, cmd_list in patterns.items():
        for cmd in cmd_list:
            if cmd.lower() in found_commands or shutil.which(cmd):
                categories[category].add(cmd)
    
    # Find uncategorized commands (limit to avoid spam)
    categorized = set()
    for cmd_set in categories.values():
        categorized.update(cmd_set)
    
    uncategorized = found_commands - {cmd.lower() for cmd in categorized}
    # Filter out common Windows/system executables to reduce noise
    windows_system = {'cmd', 'powershell', 'notepad', 'explorer', 'taskmgr', 'regedit', 'mspaint', 'calc'}
    uncategorized = uncategorized - windows_system
    
    # Add some interesting uncategorized tools
    categories['Other Tools'] = set(list(uncategorized)[:15])  # Limit to 15
    
    return categories

def get_key_paths():
    """Get 5-7 most important system paths."""
    paths = {
        'Current Directory': os.getcwd(),
        'Home Directory': str(Path.home()),
        'Python Executable': sys.executable,
        'Temp Directory': os.path.expandvars('%TEMP%') if os.name == 'nt' else '/tmp',
    }
    
    if os.name == 'nt':
        paths.update({
            'Program Files': os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            'System32': os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'System32'),
            'AppData Roaming': os.environ.get('APPDATA', ''),
        })
    else:
        paths.update({
            'Root': '/',
            'Usr Bin': '/usr/bin',
            'Usr Local Bin': '/usr/local/bin',
        })
    
    return paths

def system_info():
    """Returns comprehensive but focused system information."""
    
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    info = f"""
═══════════════════════════════════════════════════════════════
                        SYSTEM OVERVIEW
═══════════════════════════════════════════════════════════════

🕐 Current Time: {current_time}

🖥️  Operating System:
   Platform: {platform.system()} {platform.release()} ({platform.machine()})
   Version:  {platform.version()}
   Node:     {platform.node()}

🐍 Python Environment:
   Version:     {platform.python_version()}
   Executable:  {sys.executable}
   Implementation: {platform.python_implementation()}
"""
    
    info += "\n\n📁 Key System Paths:"
    paths = get_key_paths()
    for name, path in paths.items():
        info += f"\n   {name:<20}: {path}"
    
    info += "\n\n🛠️  Installed Tools & Commands:"
    categories = categorize_commands()
    
    for category, commands in categories.items():
        if commands:  # Only show categories with found commands
            info += f"\n\n   {category}:"
            sorted_commands = sorted(commands)
            for i, cmd in enumerate(sorted_commands):
                if i % 6 == 0:
                    info += "\n     "
                # Check if command actually exists and add indicator
                status = "✅" if shutil.which(cmd) else "❓"
                info += f"{status}{cmd:<12}"
    
    
    return info.strip()

def quick_command_check(commands):
    """Quick check for specific commands."""
    print("\n🔍 Quick Command Check:")
    for cmd in commands:
        path = shutil.which(cmd)
        status = "✅ Available" if path else "❌ Not Found"
        print(f"   {cmd:<15}: {status}")
        if path and len(path) < 80:  # Don't show very long paths
            print(f"   {'':<15}  → {path}")

# Example usage:
if __name__ == "__main__":
    print(system_info())