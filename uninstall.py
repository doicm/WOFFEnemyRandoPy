import os
import shutil
from pathlib import Path
import sys

def defineAndCheckFile(name):
    sourceCSH = Path("../resource/finalizedCommon/mithril/system/csv/" + name + ".csh")
    if name == "mirageboard_data":
        backupCSH = Path("../resource/finalizedCommon/mithril/system/csv/mirageboard_data_ERoriginal.csh")
    else:
        backupCSH = Path("../resource/finalizedCommon/mithril/system/csv/" + name + "_original.csh")

    if (bool(backupCSH.exists()) == False):
        if name == "mirageboard_data":
            print("Cannot locate file /resource/finalizedCommon/mithril/system/csv/" + name + "_ERoriginal.csh.")    
        else:
            print("Cannot locate file /resource/finalizedCommon/mithril/system/csv/" + name + "_original.csh.")
        print("It appears the randomizer may already be uninstalled. If you are still having issues, \ngo to Steam and verify your files.")
        input("\nPress enter to exit.\n")
        sys.exit()
    return [sourceCSH,backupCSH]

def copyAndRemoveFile(source, backup):
    shutil.copyfile(backup,source)
    os.remove(backup)

def clearLogs():
    with open('./logs/monster_log.txt','w') as f:
        f.write('')
    with open('./logs/seed.txt','w') as f:
        f.write('')

os.system('cls' if os.name == 'nt' else 'clear')

[sourceCSH, backupCSH] = defineAndCheckFile('enemy_group_list')
[sourceMBDCSH, backupMBDCSH] = defineAndCheckFile('mirageboard_data')
[sourceCESLCSH, backupCESLCSH] = defineAndCheckFile('character_enemy_status_list')
[sourceSLCSH, backupSLCSH] = defineAndCheckFile('shop_list')
[sourceMPCSH, backupMPCSH] = defineAndCheckFile('monster_place')

print("#################################################################")
print("##                Enemy Randomizer Uninstaller                 ##")
print("#################################################################\n")
print("This will uninstall the Enemy randomizer.\n---")
input("Press enter to uninstall.\n")

copyAndRemoveFile(sourceCSH,backupCSH)
copyAndRemoveFile(sourceMBDCSH,backupMBDCSH)
copyAndRemoveFile(sourceCESLCSH,backupCESLCSH)
copyAndRemoveFile(sourceSLCSH,backupSLCSH)
copyAndRemoveFile(sourceMPCSH,backupMPCSH)

clearLogs()

input("\nUninstallation complete. Press enter to exit.\n")