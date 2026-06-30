#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to completely uninstall and remove Microsoft Edge (and Edge Update) from Windows.
Requires administrator privileges.
"""

import os
import sys
import subprocess
import shutil
import winreg
import ctypes
import time
import logging
from pathlib import Path

# ---------- Logging ----------
LOG_FILE = Path.home() / "Desktop" / "edge_removal.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ---------- Admin Check & Elevation ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    """Restart the script with administrator privileges."""
    script = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, script, None, 1
    )
    sys.exit()

# ---------- Stop Edge Processes ----------
def stop_edge_processes():
    """Terminate all running Edge processes."""
    try:
        subprocess.run(["taskkill", "/f", "/im", "msedge.exe"], capture_output=True)
        subprocess.run(["taskkill", "/f", "/im", "msedgewebview2.exe"], capture_output=True)
        subprocess.run(["taskkill", "/f", "/im", "MicrosoftEdgeUpdate.exe"], capture_output=True)
        logging.info("Edge processes terminated.")
    except Exception as e:
        logging.warning(f"Could not stop some processes: {e}")

# ---------- Uninstall via Windows Installer ----------
def uninstall_edge_via_wmic():
    """
    Use WMIC to find and uninstall Microsoft Edge.
    Returns True if an uninstall was triggered successfully.
    """
    try:
        # Query product name containing "Microsoft Edge"
        cmd = 'wmic product where "name like \'%%Microsoft Edge%%\'" get name, identifyingnumber'
        output = subprocess.check_output(cmd, shell=True, text=True)
        lines = output.strip().splitlines()
        # Find lines that include "Microsoft Edge" (not EdgeUpdate)
        for line in lines:
            if "Microsoft Edge" in line and "EdgeUpdate" not in line:
                parts = line.split()
                # The identifying number is the last token
                if parts:
                    product_code = parts[-1].strip()
                    if product_code:
                        logging.info(f"Found Edge product code: {product_code}")
                        # Uninstall using msiexec
                        uninstall_cmd = f'msiexec /x {product_code} /quiet /norestart'
                        subprocess.run(uninstall_cmd, shell=True, check=False)
                        logging.info("Uninstall command sent.")
                        return True
        logging.warning("No Microsoft Edge product found via WMIC.")
        return False
    except Exception as e:
        logging.error(f"WMIC uninstall failed: {e}")
        return False

def uninstall_edge_via_uninstaller():
    """
    Try to run the built-in uninstaller executable.
    """
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\*\Installer\setup.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\*\Installer\msedge_installer.exe",
    ]
    for pattern in paths:
        for setup in Path("C:/").glob(pattern):
            if setup.exists():
                try:
                    subprocess.run([str(setup), "--uninstall", "--system-level", "--force-uninstall"], check=False)
                    logging.info(f"Ran uninstaller: {setup}")
                    return True
                except Exception as e:
                    logging.error(f"Failed to run uninstaller {setup}: {e}")
    logging.warning("No Edge uninstaller found.")
    return False

def uninstall_edge_update():
    """Uninstall Microsoft Edge Update."""
    try:
        cmd = 'wmic product where "name like \'%%Microsoft Edge Update%%\'" get identifyingnumber'
        output = subprocess.check_output(cmd, shell=True, text=True)
        lines = output.strip().splitlines()
        for line in lines:
            if "Microsoft Edge Update" in line:
                parts = line.split()
                if parts:
                    product_code = parts[-1].strip()
                    if product_code:
                        subprocess.run(f'msiexec /x {product_code} /quiet /norestart', shell=True, check=False)
                        logging.info("Uninstalled Edge Update.")
                        return True
        logging.warning("Edge Update not found via WMIC.")
        return False
    except Exception as e:
        logging.error(f"Failed to uninstall Edge Update: {e}")
        return False

# ---------- Delete Files and Folders ----------
def delete_edge_files():
    """Remove all Edge-related files and folders."""
    folders = [
        # Program Files
        r"C:\Program Files (x86)\Microsoft\Edge",
        r"C:\Program Files (x86)\Microsoft\EdgeUpdate",
        r"C:\Program Files (x86)\Microsoft\EdgeCore",
        r"C:\Program Files\Microsoft\Edge",
        r"C:\Program Files\Microsoft\EdgeUpdate",
        # AppData (per-user and all-users)
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\EdgeUpdate"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Edge"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Edge"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\EdgeUpdate"),
        # Temp folders
        os.path.expandvars(r"%TEMP%\Edge*"),
        # Common user data
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\Edge"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\EdgeUpdate"),
        # All users profile
        r"C:\Users\*\AppData\Local\Microsoft\Edge",
        r"C:\Users\*\AppData\Local\Microsoft\EdgeUpdate",
        r"C:\Users\*\AppData\Roaming\Microsoft\Edge",
    ]
    for path in folders:
        expanded = os.path.expandvars(path)
        # Handle wildcards (for users)
        if "*" in expanded:
            import glob
            for p in glob.glob(expanded, recursive=True):
                try:
                    if os.path.isfile(p):
                        os.remove(p)
                        logging.info(f"Deleted file: {p}")
                    elif os.path.isdir(p):
                        shutil.rmtree(p, ignore_errors=True)
                        logging.info(f"Deleted folder: {p}")
                except Exception as e:
                    logging.warning(f"Could not delete {p}: {e}")
        else:
            try:
                if os.path.isdir(expanded):
                    shutil.rmtree(expanded, ignore_errors=True)
                    logging.info(f"Deleted folder: {expanded}")
                elif os.path.isfile(expanded):
                    os.remove(expanded)
                    logging.info(f"Deleted file: {expanded}")
            except Exception as e:
                logging.warning(f"Could not delete {expanded}: {e}")

# ---------- Remove Registry Keys ----------
def delete_registry_keys():
    """Remove Edge-related registry keys."""
    keys = [
        # Machine-wide
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Edge"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Edge"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate"),
        # User-specific
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Edge"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Edge\BLBeacon"),
        # Uninstall entries
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge"),
    ]
    for hive, key_path in keys:
        try:
            winreg.DeleteKey(hive, key_path)
            logging.info(f"Deleted registry key: {hive} - {key_path}")
        except FileNotFoundError:
            logging.info(f"Registry key not found: {hive} - {key_path}")
        except Exception as e:
            logging.warning(f"Could not delete registry key {hive} - {key_path}: {e}")

    # Also delete Edge Update keys under Uninstall
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_ALL_ACCESS) as uninstall_key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(uninstall_key, i)
                    if "Edge" in subkey_name or "EdgeUpdate" in subkey_name:
                        try:
                            winreg.DeleteKey(uninstall_key, subkey_name)
                            logging.info(f"Deleted uninstall subkey: {subkey_name}")
                        except:
                            pass
                    i += 1
                except WindowsError:
                    break
    except Exception as e:
        logging.warning(f"Could not enumerate uninstall keys: {e}")

# ---------- Disable Edge Update Scheduled Tasks ----------
def disable_edge_update_tasks():
    """Disable or delete scheduled tasks for Edge Update."""
    try:
        tasks = [
            "MicrosoftEdgeUpdateTaskMachineCore",
            "MicrosoftEdgeUpdateTaskMachineUA",
            "MicrosoftEdgeUpdateTaskUser*",
        ]
        for task in tasks:
            subprocess.run(f'schtasks /change /disable /tn "{task}" /f', shell=True, check=False)
            # Also try to delete
            subprocess.run(f'schtasks /delete /tn "{task}" /f', shell=True, check=False)
        logging.info("Disabled/deleted Edge Update scheduled tasks.")
    except Exception as e:
        logging.warning(f"Could not manage scheduled tasks: {e}")

# ---------- Main ----------
def main():
    print("=" * 60)
    print("   Microsoft Edge Complete Removal Script")
    print("   WARNING: This will permanently delete Edge and all its data.")
    print("=" * 60)
    print(f"Log file will be saved to: {LOG_FILE}")
    print()

    if not sys.platform.startswith("win"):
        logging.error("This script is only for Windows.")
        sys.exit(1)

    if not is_admin():
        logging.info("Requesting administrator privileges...")
        elevate()
        # Elevation will restart the script; the following code runs only after elevation.
        # After elevation, we re-run, so we need to re-check.
        # Actually, after elevation, the script restarts, so we need to handle that.
        # We'll just run the main logic after elevation.
        # The script will restart and run again with admin rights.
        # So we need to put the main logic after this check.
        # But we already called elevate() which will exit this instance.
        # So we need to structure: if not admin, elevate and exit. Else proceed.

    # Now we should be admin.
    if not is_admin():
        logging.error("Failed to gain administrator privileges. Exiting.")
        sys.exit(1)

    logging.info("Starting Edge removal process...")

    # Confirm once more
    print("\nThis script will attempt to remove Microsoft Edge completely.")
    print("Are you sure you want to continue? (y/N): ", end="")
    response = input().strip().lower()
    if response != "y":
        print("Aborted.")
        sys.exit(0)

    try:
        # Step 1: Stop processes
        stop_edge_processes()
        time.sleep(2)

        # Step 2: Uninstall via WMIC and/or uninstaller
        uninstalled = uninstall_edge_via_wmic()
        if not uninstalled:
            uninstalled = uninstall_edge_via_uninstaller()

        # Step 3: Uninstall Edge Update
        uninstall_edge_update()

        # Step 4: Delete files and folders
        delete_edge_files()

        # Step 5: Delete registry keys
        delete_registry_keys()

        # Step 6: Disable scheduled tasks
        disable_edge_update_tasks()

        logging.info("Edge removal completed. Please restart your computer to finalize.")
        print("\nRemoval process finished. Check the log file for details.")
        print(f"Log file: {LOG_FILE}")
        print("A system restart is recommended.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
