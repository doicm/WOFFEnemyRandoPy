# TODO
# Randomize murkrifts (if I randomize murkrifts, I need to see if I can set labels on overworld. I would avoid changing the first murkrift)

import csv
import random
import os
from pathlib import Path
import sys
import shutil
import subprocess
import time
import copy

# Global variables
# list of monsters to ignore, including Bahamutian Soldiers, so that they don't appear in the mirage list on the map
monsToIgnoreOnMap = ['7193','7194','7195']
# list of monsters to re-include into certain areas that were excluded from randomization
monsToReinclude = [["0100", "7068"], ["0500", "7054"], ["2100", "7044"]]
# Make an option to shuffle bosses. If yes, then shuffle. If no, then don't shuffle. Make the variable global.
shuffleBossBool = False

# Function for each set of lines for the bestiary
def bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, start, end):
    exceptionLineList = [123,144,169,188,189,210,231,262,281,282,334,342,343,345,374,376,377,387] # (need to minus 1 from enemies on this list)
    ceslLine = start - 1
    while ceslLine <= end - 1:
        # if line is exception, ignore it and move to the next
        if ceslLine in exceptionLineList:
            ceslLine += 1
            continue
        # add all of the row data minus the variantID
        ceslRowData.append([CESLoutput[ceslLine][1:]])
        # make separate data for levels, gil and exp (including NG+ data)
        levelsGEXP.append([CESLoutput[ceslLine][3], CESLoutput[ceslLine][79], CESLoutput[ceslLine][80], CESLoutput[ceslLine][81], CESLoutput[ceslLine][82]])
        enemiesDict.update({CESLoutput[ceslLine][0]: [CESLoutput[ceslLine][2]]})
        # search EGL for first instance of value in key value, then add to value array
        for row in EGLoutput:
            if CESLoutput[ceslLine][2] in row:
                idx = row.index(CESLoutput[ceslLine][2])
                enemiesDict[CESLoutput[ceslLine][0]].append(row[idx-1])
                break
        ceslLine += 1
    
    return [enemiesDict, ceslRowData, levelsGEXP]

# Function to modify CESLoutput
def ceslOutputModify(CESLoutput, eDictShuffled, levelsGEXP):
    eDictKeys = list(eDictShuffled.keys())
    eDictKeys.sort()
    sortedDict = {i: eDictShuffled[i] for i in eDictKeys}
    levelIter = 0
    for key, value in sortedDict.items():
        # first iteration combines the data
        for row in CESLoutput:
            if key == row[0]:
                value[2][0].insert(0,key)
                colIter = 0
                lenRow = len(row)
                while (colIter < lenRow):
                    row[colIter] = value[2][0][colIter]
                    colIter += 1
                # reassign the base values of levels, exp, and gil
                row[3] = levelsGEXP[levelIter][0]
                row[79] = levelsGEXP[levelIter][1]
                row[80] = levelsGEXP[levelIter][2]
                row[81] = levelsGEXP[levelIter][3]
                row[82] = levelsGEXP[levelIter][4]
                levelIter += 1
                break
    return CESLoutput

# Function to modify EGLoutput
def eglOutputModify(EGLoutput, eDictShuffled):
    # I want to keep a txt log of enemies for each area to reference later for monster_place
    # I'll store it in a list first. i'll use sets to remove duplicates in each area
    miragesByArea = {}
    for key, value in eDictShuffled.items():
        for row in EGLoutput:
            j = 1
            while j <= 6:
                if row[(4*j)+2] == key:
                    row[(4*j)+1] = value[0]
                    row[(4*j)] = value[1]
                    area = row[1][:8]
                    if area[:2] == "RE": # I only want random encounter sets
                        if area not in miragesByArea:
                            miragesByArea[area] = []
                        if value[1] not in miragesByArea[area]:
                            miragesByArea[area].append(value[1])
                j += 1
    sortedMiragesByArea = dict(sorted(miragesByArea.items(), key=lambda item: item[0]))
    toWrite = ""
    # write to text log the very basic information to write to monster_place.csv later
    with open("./logs/monster_log.txt", "w") as f:
        for key, value in sortedMiragesByArea.items():
            for v in value:
                toWrite += key + ": " + v + "\n"
        f.write(toWrite)
    return EGLoutput

# Function to collect random encounters for shuffling
def collectRandomEncounters(EGLoutput,CESLoutput,enemiesDict,ceslRowData,levelsGEXP):
    # Wellspring Woods 
    # variants are 117, 118
    # lines in CESL are 117-118, but it starts at 116. always minus 1 from the line, since they're 1 based and not 0 based. I'll account for that in the function
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 117, 118)

    # Nether Nebula
    # variants are 123-133. I need to make an exception for copper gnome 1 to allow for the scale to be weighed down. copper gnome is 124
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 123, 133)

    # Watchplains
    # variants are 137-144, 146-149. exception for 145
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 137, 149)

    # Pyreglow Forest
    # variants are 153-161
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 153, 161)

    # Icicle Ridge
    # 166-169,171-181. exception for 170
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 166, 181)

    # Saronia Docks
    # 188-194. 190 is Mimic, which will be excluded. 189 is Sharqual, which I will also exclude in case Murkrift is unavailable/gets defeated.
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 188, 194)

    # Dragon's Scars
    # 206-212, exception for 211 (mega red dragon)
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 206, 212)

    # Valley Seven
    # 216-223
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 216, 223)

    # Windswept Mire
    # 227-233, exception for 232
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 227, 233)

    # Phantom Sands
    # 238-246
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 238, 246)

    # Underground Prison
    # 251-252. Excluding both actually because all mirages are lost at this point anyway and it could be troublesome
    # [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 251, 252)

    # Mako Reactor 0
    # 260-267, exception for 263. 268 is Mimic Jackpot, which will be excluded as well
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 260, 267)

    # Big Bridge
    # 274-284, Excepting 282, 283 (events). I wonder how quest enemies are affected (281 is Minotaur).
    # 277 (Mythril Giant) static included. Imp (292) will be included with the next set.
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 274, 284)

    # Train Graveyard
    # 285-292
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 285, 292)

    # Sunken Temple
    # 303-312
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 303, 312)

    # Crystal Tower
    # 330-348, including 330 for Kuza Beast static, 345 for Kuza Kit; 
    # excluding 335 for Elasmos (no encounter set has that), 343 344 and 346 for Bahamutians (same) 
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 330, 348)

    # Chainroad
    # 361-370
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 361, 370)

    # Castle Exnine
    # 373-392
    # exclude 375 for Behemonster. Don't want to try XLs in rotation yet. 377-378,388 (no entry) 
    [enemiesDict, ceslRowData, levelsGEXP] = bestiaryTraversal(EGLoutput, CESLoutput, enemiesDict, ceslRowData, levelsGEXP, 373, 392)

    # Only going up to Castle Exnine for random encounters because post-game stuff is fine on its own (and may not be included in non-Maxima?)

    return [enemiesDict, ceslRowData, levelsGEXP]

# Function to shuffle rare monsters
def shuffleRareMonsters(EGLoutput, CESLoutput):
    rareMonsterList = ['570','572','576','582','595','599','606','613','617','620','624','636','642','645'] 
    # malboro menace + princess flan kinda throw off the level balance, but oh well. same with the gigan cacti
    rareMonsterData = []
    # iterate through EGLoutput first, grabbing the rare monster data
    for row in EGLoutput:
        if row[0] in rareMonsterList:
            rareMonsterData.append(row)
    # Get each monster in the rare encounter, if applicable
    eachRareMonster = []
    for row in rareMonsterData:
        j = 6
        i = 0
        while i <= 5:
            if (row[j+(i*4)] != '-1'):
                rareMonID = row[j+(i*4)]
                if len(eachRareMonster) < 1:
                    eachRareMonster.append(rareMonID)
                else:
                    if rareMonID not in eachRareMonster:
                        eachRareMonster.append(rareMonID)
            i += 1
    # iterate through CESLoutput to grab level and gil/exp. this stays in the same order. also putting current cesl id
    levelsGEXP = []
    for row in CESLoutput:
        for monster in eachRareMonster:
            if monster == row[0]:
                levelsGEXP.append([monster, row[3], row[79], row[80], row[81], row[82]])
                continue
    # iterate through EGLoutput again, this time shuffling the rare monster data. put the data in a dictionary to shuffle
    rareDict = {}
    i = 0
    while i < len(rareMonsterList):
        rareDict[rareMonsterList[i]] = rareMonsterData[i]
        i += 1
    l = list(rareDict.keys())
    v = list(rareDict.values())
    random.shuffle(l)
    rareDictShuffled = dict(zip(l, v))
    rareDictKeys = list(rareDictShuffled.keys())
    rareDictKeys.sort()
    # Get each rare monster listed after shuffling and remove duplicates
    shuffled_EachRareMonster = []
    sortedDict = {i: rareDictShuffled[i] for i in rareDictKeys}
    for key, value in sortedDict.items():
        j = 6
        i = 0
        while i <= 5:
            if (value[j+(i*4)] != '-1'):
                rareMonID = value[j+(i*4)]
                if len(shuffled_EachRareMonster) < 1:
                    shuffled_EachRareMonster.append(rareMonID)
                else:
                    if rareMonID not in shuffled_EachRareMonster:
                        shuffled_EachRareMonster.append(rareMonID)
            i += 1
    # i need to put the previous cesl ids onto the levelsGEXP list
    # so that I can reference the levels/GEXP
    i = 0
    while i < len(levelsGEXP):
        levelsGEXP[i].append(shuffled_EachRareMonster[i])
        i += 1
    i = 0
    broken = False
    eglList = []
    for key, value in sortedDict.items():
        eglList.append([key, value])
    # iterate through CESL output again. the lGEXP needs to be assigned to it's proper monster
    # use levelsGEXP for reference with previous and current values
        for row in CESLoutput:
            if broken:
                break
            if levelsGEXP[i][6] == row[0]:
                row[3] = levelsGEXP[i][1]
                row[79] = levelsGEXP[i][2]
                row[80] = levelsGEXP[i][3]
                row[81] = levelsGEXP[i][4]
                row[82] = levelsGEXP[i][5]
                i += 1
                if (i == (len(levelsGEXP) - 1)):
                    broken = True
                    break
                continue
    # build the EGLoutput. i only want to go through the data once though
    i = 0
    broken = False
    eglList = sorted(eglList, key=lambda x: x[0])
    # make a deep copy, since eglList made a shallow copy that changed as the list iterated.
    deepEglList = copy.deepcopy(eglList)
    # while going through the eglList, put these values in monster_log.txt
    with open('./logs/monster_log.txt', 'a') as mLog:
        toWrite = ""
        for row in EGLoutput:
            if broken:
                break
            if deepEglList[i][0] == row[0]:
                row[3:] = deepEglList[i][1][3:]
                # Write values for each rare monster in line
                j = 4
                k = 0
                while k <= 6:
                    # account for duplicates
                    if (row[j+(k*4)] != '-1') and row[j+(k*4)] != row[k*4]:
                        toWrite += row[1][:8] + ": " + row[j+(k*4)] + "\n"
                    k += 1
                i += 1
                if i == len(deepEglList):
                    broken = True
        mLog.write(toWrite)
    # I need to make a special exception for Dragon Scars rare encounter, which I want to set to level 20.
    # Some people may not know the trick to running away and getting the required item
    # EGL ID for dragon scar encounter is 595. Be cautious if it's more than 1 enemy type
    dragonScarsLevelToSet = '20'
    ceslIDs = []
    value = EGLoutput[595]
    j = 6
    i = 0
    # get ceslIDs for each monster in group
    while i <= 5:
        if (value[j+(i*4)] != '-1'):
            rareMonID = value[j+(i*4)]
            if len(ceslIDs) < 1:
                ceslIDs.append(rareMonID)
            else:
                if rareMonID not in ceslIDs:
                    ceslIDs.append(rareMonID)
        i += 1
    # change levels to dragonScarsLevelToSet for each monster in group
    for id in ceslIDs:
        for row in CESLoutput:
            if row[0] == id:
                row[3] = dragonScarsLevelToSet
                break
    return [EGLoutput, CESLoutput]

def shuffleBosses(EGLoutput, CESLoutput):
    # list of bosses based on EGL value
    # excluding elemental trio, due to missables
    # excluding chapter 14, since that's a mess
    # excluding order of the circle fights. they're special :)
    bossesList = ['569','571','573','577','578','592','598','601','607','615','618','623','626','627','629','634','635','644'] 
    bossData = []
    # iterate through EGLoutput first, grabbing the boss data
    for row in EGLoutput:
        if row[0] in bossesList:
            bossData.append(row)
    # Get each monster in the boss fight, if applicable
    eachBoss = []
    for row in bossData:
        j = 6
        i = 0
        while i <= 5:
            if (row[j+(i*4)] != '-1'):
                bossID = row[j+(i*4)]
                if len(eachBoss) < 1:
                    eachBoss.append(bossID)
                else:
                    if bossID not in eachBoss:
                        eachBoss.append(bossID)
            i += 1
    # iterate through CESLoutput to grab level and gil/exp. this stays in the same order. also putting current cesl id
    levelsGEXP = []
    for row in CESLoutput:
        for monster in eachBoss:
            if monster == row[0]:
                levelsGEXP.append([monster, row[3], row[79], row[80], row[81], row[82]])
                continue
    # iterate through EGLoutput again, this time shuffling the boss data. put the data in a dictionary to shuffle
    bossDict = {}
    i = 0
    while i < len(bossesList):
        bossDict[bossesList[i]] = bossData[i]
        i += 1
    l = list(bossDict.keys())
    v = list(bossDict.values())
    random.shuffle(l)
    bossDictShuffled = dict(zip(l, v))
    bossDictKeys = list(bossDictShuffled.keys())
    bossDictKeys.sort()
    # Get each boss listed after shuffling and remove duplicates
    shuffled_eachBoss = []
    sortedDict = {i: bossDictShuffled[i] for i in bossDictKeys}
    for key, value in sortedDict.items():
        j = 6
        i = 0
        while i <= 5:
            if (value[j+(i*4)] != '-1'):
                bossID = value[j+(i*4)]
                if len(shuffled_eachBoss) < 1:
                    shuffled_eachBoss.append(bossID)
                else:
                    if bossID not in shuffled_eachBoss:
                        shuffled_eachBoss.append(bossID)
            i += 1
    # i need to put the previous cesl ids onto the levelsGEXP list
    # so that I can reference the levels/GEXP
    i = 0
    while i < len(levelsGEXP):
        levelsGEXP[i].append(shuffled_eachBoss[i])
        i += 1
    i = 0
    broken = False
    eglList = []
    for key, value in sortedDict.items():
        eglList.append([key, value])
    # iterate through CESL output again. the lGEXP needs to be assigned to it's proper monster
    # use levelsGEXP for reference with previous and current values
        for row in CESLoutput:
            if broken:
                break
            if levelsGEXP[i][6] == row[0]:
                row[3] = levelsGEXP[i][1]
                row[79] = levelsGEXP[i][2]
                row[80] = levelsGEXP[i][3]
                row[81] = levelsGEXP[i][4]
                row[82] = levelsGEXP[i][5]
                i += 1
                if (i == (len(levelsGEXP) - 1)):
                    broken = True
                    break
                continue
    # build the EGLoutput. i only want to go through the data once though
    i = 0
    broken = False
    eglList = sorted(eglList, key=lambda x: x[0])
    # make a deep copy, since eglList made a shallow copy that changed as the list iterated.
    deepEglList = copy.deepcopy(eglList)
    # while going through the eglList, put these values in monster_log.txt
    with open('./logs/monster_log.txt', 'a') as mLog:
        toWrite = ""
        for row in EGLoutput:
            if broken:
                break
            if deepEglList[i][0] == row[0]:
                row[3:] = deepEglList[i][1][3:]
                # Write values for each rare monster in line
                j = 4
                k = 0
                while k <= 6:
                    # account for duplicates
                    if (row[j+(k*4)] != '-1') and row[j+(k*4)] != row[k*4]:
                        if int(row[j+(k*4)]) > 1:
                            toWrite += row[1][:8] + ": " + row[j+(k*4)] + "\n"
                    k += 1
                i += 1
                if i == len(deepEglList):
                    broken = True
        mLog.write(toWrite)
    # # I need to make a special exception for Dragon Scars rare encounter, which I want to set to level 20.
    # # Some people may not know the trick to running away and getting the required item
    # # EGL ID for dragon scar encounter is 595. Be cautious if it's more than 1 enemy type
    # dragonScarsLevelToSet = '20'
    # ceslIDs = []
    # value = EGLoutput[595]
    # j = 6
    # i = 0
    # # get ceslIDs for each monster in group
    # while i <= 5:
    #     if (value[j+(i*4)] != '-1'):
    #         rareMonID = value[j+(i*4)]
    #         if len(ceslIDs) < 1:
    #             ceslIDs.append(rareMonID)
    #         else:
    #             if rareMonID not in ceslIDs:
    #                 ceslIDs.append(rareMonID)
    #     i += 1
    # # change levels to dragonScarsLevelToSet for each monster in group
    # for id in ceslIDs:
    #     for row in CESLoutput:
    #         if row[0] == id:
    #             row[3] = dragonScarsLevelToSet
    #             break


    return [EGLoutput, CESLoutput]

def modifyEnemies(EGLoutput,CESLoutput,seedValue):
    # enemies dictionary to hold the final set of enemies
    enemiesDict = {}
    # ceslRowData list to hold the ceslRowData in order and to apply to the enemies dictionary after randomization
    ceslRowData = []
    # need to keep levels, gil, and exp separate. also consider NG+ amounts
    levelsGEXP = []
    # the goal is to not randomize every single slot in the game, but randomize every unique slot up to final boss. 
    # avoid duplicates
    # for example, all Mu 1's <-> all Copper Gnome 2's with ceslRowData remaining
    # This is for random encounters
    collectRandomEncounters(EGLoutput,CESLoutput,enemiesDict,ceslRowData,levelsGEXP)

    # Shuffle the keys (for random encounters) separate from the values and create a new dictionary from it
    l = list(enemiesDict.keys())
    v = list(enemiesDict.values())
    random.seed(seedValue)
    random.shuffle(l)
    eDictShuffled = dict(zip(l, v))
    items = eDictShuffled.items()
    i = 0
    # put the ceslRowData back into the dictionary
    for item in items:
        eDictShuffled[item[0]].append(ceslRowData[i])
        i += 1
    # write to CESLoutput first, changing the ceslRowData
    CESLoutput = ceslOutputModify(CESLoutput, eDictShuffled, levelsGEXP)

    # write to EGLoutput second, changing the other values
    EGLoutput = eglOutputModify(EGLoutput, eDictShuffled)

    # Next, I need to randomize the rare monster encounters. I don't know if I can do this yet, but let's try it. 
    # For now, let's just swap two encounters and see what stats I need to shuffle
    # Rare monsters are labeled with _ex### in enemy_group_list.csv
    # Let's swap EV_c04_ex001 (Black Chocochick) and EV_c10_ex001 (Cerberus)
    [EGLoutput, CESLoutput] = shuffleRareMonsters(EGLoutput, CESLoutput)

    # Make an option to shuffle bosses. If yes, then shuffle. If no, then don't shuffle. Make the variable global.
    global shuffleBossBool
    if shuffleBossBool:
        [EGLoutput, CESLoutput] = shuffleBosses(EGLoutput, CESLoutput)

    # At some point, I'll need to adjust each map's information for what mirages you can encounter in each area. I'm not sure what file has that data yet.
    # There might be a problem for before/after "Cleared". I might be able to make it dynamic, but I'm not sure. I'm now realizing that mirages may be locked out
    # from obtaining permanently as a result of the way I have things set up, but I don't mind.

    return [EGLoutput, CESLoutput]

def modifyMonsterPlace(MPoutput):
    # have data on hand for each area from monster_place.csv
    monster_place_csv_data = [
        ['ParallelWorldGrove', '異世界の林', '1', '1'],
        ['NebraCave', 'ネブラの洞窟', '5', '5'],
        ['MarchPlain', '進撃の平原', '6', '6'],
        ['LightForest', '灯の森', '7', '7'],
        ['IcicleValley', '氷柱の谷フロア', '12', '11'],
        ['SaloniaHarbor', 'サロニアの港', '14', '13'],
        # ['SewerArea', '下海・入口', '16', '15'], #sewer area will be ignored, since I don't randomize this set yet
        ['DragonValley', '竜の渓谷', '19', '18'],
        ['BombVolcano', 'セブンスバリー', '23', '21'],
        ['WindWetlandsBands', '風吹く湿地帯', '24', '22'],
        ['PhantomDesert', '幻の砂漠', '27', '25'],
        # ['DeepGround', 'ディープグラウンド', '29', '28'], # this area doesn't get randomized either
        ['MakoFireplaceInside', '零番魔晄炉', '30', '29'],
        ['big_bridge_', 'ビックブリッジ', '32', '31'],
        ['resshahakaba_', '列車墓場', '35', '34'],
        ['SeabedTemple_', '海底神殿', '41', '40'],
        ['CrystalTower_', 'クリスタルタワー', '43', '42'],
        ['ChainLoad_', '鎖の道', '47', '45'],
        ['ExNineCastle_', 'エクスナイン城', '49', '47']
    ]

    # get the areas that aren't being randomized
    nonRandomizedAreas = []
    # get SewerArea first
    i = 42
    while i < 50:
        nonRandomizedAreas.append(MPoutput[i])
        i += 1
    i = 84
    while i < 87:
        nonRandomizedAreas.append(MPoutput[i])
        i += 1
    # write for each area
    
    MPoutput = []
    # list of monsters to re-include into certain areas that were excluded from randomization
    global monsToReinclude
    monsToReincludeCopy = copy.deepcopy(monsToReinclude)
    with open("./logs/monster_log.txt", "r") as f:
        id = 0
        mpcdIter = 0
        currLine = "0000"
        prevLine = "0000"
        areaIter = 1
        for line in f:
            currLine = line[4:8]
            # if the next line is a new area, then go to the next area in monster_place_csv_data
            if currLine != prevLine:
                # if currLine = particular line that were excepted, then put in unrandomized data
                if currLine == '0600': # put in sewer data
                    j = 0
                    while j < len(nonRandomizedAreas):
                        if nonRandomizedAreas[j][1][0:5] != "Sewer":
                            break
                        MPoutput.append([str(id), nonRandomizedAreas[j][1], nonRandomizedAreas[j][2],nonRandomizedAreas[j][3], nonRandomizedAreas[j][4], nonRandomizedAreas[j][5], nonRandomizedAreas[j][6]])
                        j += 1
                        id += 1
                if currLine == '1500': # put in DeepGround data
                    j = 8
                    while j < len(nonRandomizedAreas):
                        if nonRandomizedAreas[j][1][0:5] != "DeepG":
                            break
                        MPoutput.append([str(id), nonRandomizedAreas[j][1], nonRandomizedAreas[j][2],nonRandomizedAreas[j][3], nonRandomizedAreas[j][4], nonRandomizedAreas[j][5], nonRandomizedAreas[j][6]])
                        j += 1
                        id += 1
                prevLine = currLine
                mpcdIter += 1
                areaIter = 1
                if (mpcdIter == len(monster_place_csv_data)):
                    break
                # check for monsToReincludeCopy
                if len(monsToReincludeCopy) != 0:
                    if currLine == monsToReincludeCopy[0][0]:
                        MPoutput.append([str(id), monster_place_csv_data[mpcdIter][0] + str(areaIter),monster_place_csv_data[mpcdIter][1],monster_place_csv_data[mpcdIter][2],monsToReincludeCopy[0][1],monster_place_csv_data[mpcdIter][3],'0'])
                        id += 1
                        areaIter += 1
                        monsToReincludeCopy.pop(0)
            # if the current line has a monster to ignore, move on
            if line[-5:-1] in monsToIgnoreOnMap:
                continue
            if (mpcdIter == len(monster_place_csv_data)):
                break
            MPoutput.append([str(id), monster_place_csv_data[mpcdIter][0] + str(areaIter),monster_place_csv_data[mpcdIter][1],monster_place_csv_data[mpcdIter][2],line[-5:-1],monster_place_csv_data[mpcdIter][3],'0'])
            if areaIter > 12: # need to have every area list less than 12 in-game, unfortunately. otherwise, it bugs out. will have the log for reference, at least
                MPoutput.pop(len(MPoutput) - 1)
            areaIter += 1
            id += 1
            
    return MPoutput

# Function for modifying txt monster log for users to reference
def modifyMonsterLog():
    MPoutput = []
    # list of monsters to re-include into certain areas that were excluded from randomization
    global monsToReinclude
    monsToReincludeCopy = copy.deepcopy(monsToReinclude)
    with open('./logs/monster_log.txt', 'r') as f:
        for line in f:
            # first entry is areaID. second entry is mirageID
            if line[-5:-1] in monsToIgnoreOnMap:
                continue
            # if current area is same as monsToReinclude area, sneak it in
            if (len(monsToReincludeCopy) > 0):
                if line[4:8] == monsToReincludeCopy[0][0]:
                    MPoutput.append([monsToReincludeCopy[0][0],monsToReincludeCopy[0][1]])
                    monsToReincludeCopy.pop(0)
            MPoutput.append([line[4:8],line[-5:-1]])
    linesArea = open('./database/areas.txt').read().splitlines()
    linesEnemy = open('./database/enemy_names.txt', 'r').read().splitlines()

    # rewrite monster log
    with open('./logs/monster_log.txt', 'w') as f:
        toWrite = "Random encounters: \n"
        raresStarted = False
        bossesStarted = False
        for row in MPoutput:
            # find area first
            for areaString in linesArea:
                if areaString[:4] == row[0]:
                    toWrite += areaString[8:] + ": "
                    # then find the enemy
                    for enemyString in linesEnemy:
                        if enemyString[:4] == row[1]:
                            toWrite += enemyString[5:] + "\n"
                            break
                    break
            # then find rare monsters to append if chapter enemy
            if "_e" in row[0]:
                if raresStarted == False:
                    raresStarted = True
                    toWrite += "---\nRare monsters: \n"
                for enemyString in linesEnemy:
                    if enemyString[:4] == row[1]:
                        toWrite += "Chapter " + row[0][:2] + ": " + enemyString[5:] + "\n"
                        break
            # then find bosses to append
            elif "0406" in row[0] or "_0" in row[0]:
                if bossesStarted == False:
                    bossesStarted = True
                    toWrite += "---\nBoss fights:\n"
                for enemyString in linesEnemy:
                    if enemyString[:4] == row[1]:
                        toWrite += "Chapter " + row[0][:2] + ": " + enemyString[5:] + "\n"
                        break
        f.write(toWrite)
        
# Function to handle repeat functionality of reading the csv and turning it into a list
def readCsv(csvfilename):
    output = []
    # Open the file
    with open(csvfilename, 'r', encoding="utf-8") as csvfile:
        # Read the file
        csvreader = csv.reader(csvfile)
        # Read each row
        for row in csvreader:
            output.append(row)
    return output

# Function to handle repeat functionality of writing the csv with the modified list
def writeCsv(csvoutfile, output):
    with open(csvoutfile, 'w+', newline='', encoding="utf-8") as csvfile:
        # Write the file
        csvwriter = csv.writer(csvfile, delimiter=",")
        # Write each row
        for row in output:
            csvwriter.writerow(row)

def mirageEncsWriteCsv(seedValue):
    # Get csvs converted to list outputs
    EGLoutput = readCsv('enemy_group_list.csv')
    CESLoutput = readCsv('character_enemy_status_list.csv')
    MPoutput = readCsv('monster_place.csv')

    [EGLoutput, CESLoutput] = modifyEnemies(EGLoutput, CESLoutput, seedValue)

    MPoutput = modifyMonsterPlace(MPoutput)

    # I want to modify monster_log.txt again to make it more user-friendly to read. I need to draw from a database for this, however, and it needs
    # to be in English, so I'll have to make custom database files and reference those
    modifyMonsterLog()

    # Write to new files
    writeCsv('enemy_group_list.csv', EGLoutput)
    writeCsv('character_enemy_status_list.csv', CESLoutput)
    writeCsv('monster_place.csv', MPoutput)

def mirageboard_dataWriteCsv():
    # Get filename
    csvfilename = 'mirageboard_data.csv'

    # Get the relevant row and data for what special abilities to write to what rows for Tama, Chocochick, and Sylph
    # 63 and 68 are Tama. 997 is Chocochick. 4749 and 4751 are Sylph
    # Smash softlocks when taught to another
    relevantRowAndData = [[68,2000],[997,2002],[4749,2001],[4751, 2006]]

    output = []

    # Open the file
    with open(csvfilename, 'r', encoding="utf-8") as csvfile:
        # Read the file
        csvreader = csv.reader(csvfile)
        
        # Read each row
        for row in csvreader:
            output.append(row)
    rRADIter = 0
    for row in output:
        i = output.index(row)
        if (i in [item[0] for item in relevantRowAndData]):
            output[i][7] = '8'
            output[i][8] = relevantRowAndData[rRADIter][1]
            output[i][11] = '1'
            rRADIter += 1

    # Write to a new file
    csvoutfile = 'mirageboard_data.csv'

    with open(csvoutfile, 'w+', newline='', encoding="utf-8") as csvfile:
        # Write the file
        csvwriter = csv.writer(csvfile, delimiter=",")
        # Write each row
        for row in output:
            csvwriter.writerow(row)

def putEldboxInShops():
    # Get filename
    csvfilename = 'shop_list.csv'
    output = []

    # Open the file
    with open(csvfilename, 'r', encoding="utf-8") as csvfile:
        # Read the file
        csvreader = csv.reader(csvfile)
        
        # Read each row
        for row in csvreader:
            output.append(row)

    for row in output:
        # Eldbox is item ID 520. Put that into shops that don't have it
        if '520' in row:
            continue
        i = 0
        for element in row:
            if element == "-1":
                row[i] = '520'
                break
            i += 1
    
    # Write to new file
    SLcsvoutfile = 'shop_list.csv'

    with open(SLcsvoutfile, 'w+', newline='', encoding="utf-8") as csvfile:
        # Write the file
        csvwriter = csv.writer(csvfile, delimiter=",")
        # Write each row
        for row in output:
            csvwriter.writerow(row)

# Start CLI
os.system('cls' if os.name == 'nt' else 'clear')

# Function for verifying CSH files, opening them and copying them to backup location for working on
def verifyOpenAndCopy(cshName):
    # Make backup of file. Verify the file is there first.
    sourceCSH = Path("../resource/finalizedCommon/mithril/system/csv/" + cshName + ".csh")
    if (cshName == "mirageboard_data"):
        backupCSH = Path("../resource/finalizedCommon/mithril/system/csv/mirageboard_data_ERoriginal.csh")
    else:
        backupCSH = Path("../resource/finalizedCommon/mithril/system/csv/" + cshName + "_original.csh")

    if (bool(sourceCSH.exists()) == False):
        print("Cannot locate file /resource/finalizedCommon/mithril/system/csv/" + cshName + ".csh.")
        input("Press enter to exit installer.")
        sys.exit()
    
    # If original data exists already as a backup (if running the randomizer twice or more in a row), get the original data
    if (bool(Path(backupCSH).exists()) == True):
        # Create a copy locally for easy management
        shutil.copyfile(backupCSH, "./" + cshName + ".csh")
    else:
        shutil.copyfile(sourceCSH, backupCSH)
        # Create a copy locally for easy management
        shutil.copyfile(sourceCSH, "./" + cshName + ".csh")

    return sourceCSH


# Verify previous directory has WOFF executable to make sure files will write properly
if (bool(Path("../WOFF.exe").exists()) == False):
    print("Wrong folder placement. Place the \"enemyRando\" folder in the WOFF directory in steamapps/common.")
    input("Press enter to exit installer.")
    sys.exit()

# Make backup of enemy_group_list.csh. Verify the file is there first. 
sourceCSH = verifyOpenAndCopy("enemy_group_list")

# Make backup of mirageboard_data.csh to modify Tama, Chocochick, and Sylph. Verify the file is there first. 
sourceMBDCSH = verifyOpenAndCopy("mirageboard_data")

# Make backup of character_enemy_status_list.csh to get the ceslRowData and maintain them per area. Verify the file is there first.
sourceCESLCSH = verifyOpenAndCopy("character_enemy_status_list")

# Make backup of shop_list.csh to get the eldbox in each shop. Verify the file is there first.
sourceSLCSH = verifyOpenAndCopy("shop_list")

# Make backup of monster_place.csh to get the enemy data in each map ('cleared' has priority). Verify the file is there first.
sourceMPCSH = verifyOpenAndCopy("monster_place")

# Prompt the user for a seed name
print("#################################################################")
print("##                      Enemy Randomizer                       ##")
print("#################################################################\n")
print("Welcome to the Enemy randomizer. This randomizer shuffles most \n"
"every regular enemy encounter in the game. It is highly recommended that you\n"
"make a backup of your save before continuing.\n---")
sV = input("Please type the value you wish to use for the seed (you can leave it blank),\nand press enter:\n\n")

# if input is blank, get current time in unix
if len(sV) == 0:
    sV = time.time()

shuffleBossesInput = input("\n\nAre you interested in shuffling most bosses? Type Y to confirm, or leave blank to decline:\n\n")
shuffleBossesInput = shuffleBossesInput.lower()
if (shuffleBossesInput == 'y'):
    shuffleBossBool = True
    print("Shuffle bosses command confirmed...")
else:
    print("Understood. Will not shuffle bosses.")
time.sleep(1)


os.system('cls' if os.name == 'nt' else 'clear')

print("\nGenerating...\n")

# Run the WoFFCshTool by Surihia twice, one to decompress csh and convert to csv, and one to do the reverse after writing the values
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csv", "./enemy_group_list.csh"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csv", "./mirageboard_data.csh"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csv", "./character_enemy_status_list.csh"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csv", "./shop_list.csh"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csv", "./monster_place.csh"])

# Write the values
mirageEncsWriteCsv(sV)
mirageboard_dataWriteCsv()
putEldboxInShops()

subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csh", "./enemy_group_list.csv"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csh", "./mirageboard_data.csv"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csh", "./character_enemy_status_list.csv"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csh", "./shop_list.csv"])
subprocess.run(["./WoFFCshTool_v1.1/WoFFCshTool", "-csh", "./monster_place.csv"])

# Create txt file with seed name in it for reference
with open('./logs/seed.txt', 'w') as f:
    f.write(str(sV))

# Copy the new csh back over to resources
shutil.copyfile("./enemy_group_list.csh", sourceCSH)
shutil.copyfile("./mirageboard_data.csh", sourceMBDCSH)
shutil.copyfile("./character_enemy_status_list.csh", sourceCESLCSH)
shutil.copyfile("./shop_list.csh", sourceSLCSH)
shutil.copyfile("./monster_place.csh", sourceMPCSH)

# Delete the temporary files in this folder.
os.remove("./enemy_group_list.csh")
os.remove("./enemy_group_list.csv")
os.remove("./mirageboard_data.csh")
os.remove("./mirageboard_data.csv")
os.remove("./character_enemy_status_list.csh")
os.remove("./character_enemy_status_list.csv")
os.remove("./shop_list.csh")
os.remove("./shop_list.csv")
os.remove("./monster_place.csh")
os.remove("./monster_place.csv")

input("\nFinished generating! Press enter to exit.\n")