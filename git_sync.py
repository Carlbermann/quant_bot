#!/usr/bin/env python3
"""
Git Sync Module
Provides functions for pulling and pushing changes to/from GitHub.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def check_git_repository():
    """Check if the current directory is a Git repository."""
    return Path('.git').exists()


def run_git_command(command, capture_output=True):
    """Run a Git command and return the result."""
    try:
        result = subprocess.run(['git'] + command, 
                              capture_output=capture_output, 
                              text=True, 
                              check=True)
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def git_pull():
    """Pull the latest changes from the remote repository (origin)."""
    print("🔄 Hole neueste Änderungen vom Remote Repository...")
    
    if not check_git_repository():
        print("❌ Kein Git Repository gefunden")
        return False
    
    # Check if remote exists
    success, _ = run_git_command(['remote'])
    if not success or 'origin' not in _:
        print("❌ Kein Remote 'origin' konfiguriert")
        return False
    
    # Pull changes
    success, output = run_git_command(['pull', 'origin', 'HEAD'])
    
    if success:
        print("✓ Pull erfolgreich")
        if output.strip():
            print(f"   {output.strip()}")
        return True
    else:
        print("❌ Pull fehlgeschlagen")
        if output.strip():
            print(f"   Fehler: {output.strip()}")
        return False


def git_add_all():
    """Add all changes to the staging area."""
    success, output = run_git_command(['add', '.'])
    return success


def git_has_changes():
    """Check if there are any changes to commit."""
    success, output = run_git_command(['status', '--porcelain'])
    if success:
        return len(output.strip()) > 0
    return False


def git_commit(message):
    """Commit changes with the given message."""
    success, output = run_git_command(['commit', '-m', message])
    return success


def git_push():
    """Push changes to the remote repository."""
    success, output = run_git_command(['push', 'origin', 'HEAD'])
    return success, output


def generate_commit_message():
    """Generate a commit message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Automated commit - {timestamp}"


def git_push_commit(message=None):
    """Add, commit, and push changes to GitHub."""
    print("📤 Sende Änderungen zum Repository...")
    
    if not check_git_repository():
        print("❌ Kein Git Repository gefunden")
        return False
    
    # Check if remote exists
    success, _ = run_git_command(['remote'])
    if not success or 'origin' not in _:
        print("❌ Kein Remote 'origin' konfiguriert")
        return False
    
    # Check if there are changes to commit
    if not git_has_changes():
        print("ℹ️  Keine Änderungen zum Committen gefunden")
        return True
    
    # Add all changes
    print("   Füge alle Änderungen hinzu...")
    if not git_add_all():
        print("❌ Fehler beim Hinzufügen der Änderungen")
        return False
    
    # Generate commit message if not provided
    if message is None:
        message = generate_commit_message()
    
    # Commit changes
    print(f"   Committe Änderungen: {message}")
    if not git_commit(message):
        print("❌ Fehler beim Commit")
        return False
    
    # Push changes
    print("   Pushe Änderungen...")
    success, output = git_push()
    
    if success:
        print("✓ Push erfolgreich")
        if output.strip():
            print(f"   {output.strip()}")
        return True
    else:
        print("❌ Push fehlgeschlagen")
        if output.strip():
            print(f"   Fehler: {output.strip()}")
        
        # Provide helpful error messages
        if "authentication failed" in output.lower():
            print("   💡 Tipp: Überprüfen Sie Ihre Git-Anmeldedaten")
        elif "merge conflict" in output.lower():
            print("   💡 Tipp: Merge-Konflikt detected. Führen Sie zuerst 'git pull' aus")
        elif "no such branch" in output.lower():
            print("   💡 Tipp: Branch existiert nicht auf Remote")
        
        return False


def git_status():
    """Show current Git status."""
    if not check_git_repository():
        print("❌ Kein Git Repository gefunden")
        return
    
    print("📋 Git Status:")
    success, output = run_git_command(['status', '--short'])
    if success:
        if output.strip():
            print(output.strip())
        else:
            print("   Keine Änderungen")


def sync_workflow(message=None):
    """Complete sync workflow: pull -> push commit."""
    print("=== Git Sync Workflow ===")
    
    # Pull latest changes
    if not git_pull():
        print("⚠️  Pull fehlgeschlagen, fahre trotzdem fort...")
    
    # Push changes
    if not git_push_commit(message):
        print("❌ Sync fehlgeschlagen")
        return False
    
    print("=== Sync abgeschlossen ===")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "pull":
            git_pull()
        elif sys.argv[1] == "push":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            git_push_commit(message)
        elif sys.argv[1] == "sync":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            sync_workflow(message)
        elif sys.argv[1] == "status":
            git_status()
        else:
            print("Verwendung:")
            print("  python git_sync.py pull")
            print("  python git_sync.py push [message]")
            print("  python git_sync.py sync [message]")
            print("  python git_sync.py status")
    else:
        print("Verwendung:")
        print("  python git_sync.py pull")
        print("  python git_sync.py push [message]")
        print("  python git_sync.py sync [message]")
        print("  python git_sync.py status")
