#!/usr/bin/env python3
"""
Git Setup Module
Initializes a local Git repository and connects it to GitHub.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_git_installed():
    """Check if Git is installed on the system."""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Git ist installiert: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git ist nicht installiert. Bitte installieren Sie Git zuerst:")
        print("   - Windows: https://git-scm.com/download/win")
        print("   - macOS: brew install git")
        print("   - Linux: sudo apt-get install git (Ubuntu/Debian)")
        return False


def is_git_repository():
    """Check if the current directory is a Git repository."""
    return Path('.git').exists()


def init_git_repository():
    """Initialize a Git repository in the current directory."""
    try:
        subprocess.run(['git', 'init'], capture_output=True, text=True, check=True)
        print("✓ Git Repository initialisiert")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der Initialisierung: {e.stderr}")
        return False


def get_git_config():
    """Get current Git configuration (user.name, user.email)."""
    config = {}
    try:
        for key in ['user.name', 'user.email']:
            result = subprocess.run(['git', 'config', '--global', key], 
                                  capture_output=True, text=True, check=True)
            config[key] = result.stdout.strip()
    except subprocess.CalledProcessError:
        config[key] = "Nicht gesetzt"
    return config


def show_git_config():
    """Display current Git configuration."""
    config = get_git_config()
    print("\nAktuelle Git-Konfiguration:")
    print(f"  user.name: {config.get('user.name', 'Nicht gesetzt')}")
    print(f"  user.email: {config.get('user.email', 'Nicht gesetzt')}")


def get_remote_url():
    """Get the remote URL for origin."""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def show_remote_info():
    """Display remote repository information."""
    remote_url = get_remote_url()
    if remote_url:
        print(f"  Remote URL: {remote_url}")
    else:
        print("  Remote URL: Kein Remote repository konfiguriert")


def add_remote_repo(url):
    """Add a remote repository (HTTPS or SSH)."""
    try:
        # Check if remote 'origin' already exists
        result = subprocess.run(['git', 'remote'], capture_output=True, text=True, check=True)
        if 'origin' in result.stdout.split():
            print("⚠️  Remote 'origin' existiert bereits")
            return False
        
        subprocess.run(['git', 'remote', 'add', 'origin', url], 
                      capture_output=True, text=True, check=True)
        print(f"✓ Remote Repository hinzugefügt: {url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Hinzufügen des Remote Repository: {e.stderr}")
        return False


def setup_git_repo(github_url=None):
    """Main function to set up Git repository and connect to GitHub."""
    print("=== Git Setup ===")
    
    # Check if Git is installed
    if not check_git_installed():
        return False
    
    # Show current configuration
    show_git_config()
    
    # Initialize repository if needed
    if not is_git_repository():
        print("\nKein Git Repository gefunden. Initialisiere...")
        if not init_git_repository():
            return False
    else:
        print("✓ Git Repository existiert bereits")
    
    # Show remote info
    show_remote_info()
    
    # Add remote if URL provided
    if github_url:
        if not get_remote_url():
            print(f"\nFüge GitHub Repository hinzu...")
            add_remote_repo(github_url)
        else:
            print("\n⚠️  Remote Repository bereits konfiguriert")
    
    print("\n=== Setup abgeschlossen ===")
    return True


def interactive_setup():
    """Interactive setup for Git repository."""
    print("=== Interaktives Git Setup ===")
    
    if not check_git_installed():
        return False
    
    # Show current config
    show_git_config()
    
    # Initialize if needed
    if not is_git_repository():
        if input("\nGit Repository initialisieren? (j/N): ").lower() == 'j':
            init_git_repository()
        else:
            print("Setup abgebrochen.")
            return False
    
    # Show remote status
    show_remote_info()
    
    # Add remote if needed
    if not get_remote_url():
        github_url = input("\nGitHub Repository URL (HTTPS oder SSH): ").strip()
        if github_url:
            add_remote_repo(github_url)
    
    print("\n=== Setup abgeschlossen ===")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        github_url = sys.argv[1] if sys.argv[1] else None
        setup_git_repo(github_url)
    else:
        interactive_setup()
