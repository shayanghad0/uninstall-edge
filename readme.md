Below is a Python script that attempts to completely remove Microsoft Edge from a Windows system. It uninstalls the browser, deletes its files and data folders, removes registry entries, and disables the updater (to prevent automatic reinstallation).

**⚠️ Important**:  
- This script is **destructive** – it permanently deletes Edge and all its user data.  
- Edge is deeply integrated into Windows 10/11. Removing it may break certain system features (e.g., WebView2, PDF viewer, widgets).  
- Run this script **only if you are certain** and have a system restore point or backup.  
- Administrative privileges are required.

---

## Instructions

1. **Save the script** as `delete_edge_completely.py` on your Windows computer.
2. **Run it as Administrator** – the script will automatically request elevation if needed.
3. When prompted, confirm the removal.
4. Wait for the process to finish (it may take a few minutes).
5. **Restart your computer** to ensure all changes take effect.

---

## What the script does

- Kills all Edge processes.
- Uninstalls Edge using Windows Installer (`msiexec`) and/or the built‑in uninstaller.
- Removes Edge Update (to prevent reinstallation).
- Deletes all Edge folders from Program Files, AppData, ProgramData, and Temp.
- Wipes Edge‑related registry keys (HKLM and HKCU).
- Disables or deletes scheduled tasks that run Edge Update.

---

## Important Notes

- **Edge WebView2** is **not** removed – many applications depend on it.
- Some files may be locked and require a reboot to delete; the script logs any failures.
- After removal, Windows may attempt to reinstall Edge via Windows Update. You can block this by using group policies or registry settings (not included here).
- The script is designed for **Windows 10/11**. It may not work correctly on older versions.

---

## Disclaimer

Use this script at your own risk. The author is not responsible for any damage or loss of functionality caused by removing Microsoft Edge. Always create a system restore point before running destructive scripts.
If you use it mamby have some issuse on system 
becarefull