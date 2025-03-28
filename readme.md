Enemy Randomizer - World of Final Fantasy
==================================================================
Mod Created By:	Doicm (decentdoicm)
Special Thanks:	WoFF modding community for tools and information,
and Surihia for csv/csh conversion tool that this tool uses.

Version: 
==================================================================
0.1.0

Notes:
==================================================================

1.) In order to install and uninstall this, the enemyRando 
folder will need to be placed in the WOFF executable folder (may 
only work on Windows Steam, as it's untested in other versions).
To find, go to Steam and right-click the game "World of Final
Fantasy, click Manage -> Browse local files.... It should take
you to the folder. Put the enemyRando folder in the WOFF folder
next to the WOFF executable.

2.) I highly recommend creating a backup of your primary
save file. You can usually find it on Windows in the following:

  %USERPROFILE%\Documents\My Games\WOFF\<user-id>\savedata\

or in Linux on the following:

  <SteamLibrary-folder>/steamapps/compatdata/552700/pfx/

Description:
==================================================================
This mod is designed to work with World of Final Fantasy: Maxima
for Steam. However, it may work without Maxima expansion, but I
have no way of testing it. 

This mod changes several of the files to allow for most random
encounters and rare monsters (separately) to be randomized, as
well as for eldboxes to be purchasable at anytime at shops. This
mod also makes a few other adjustments to prevent softlocks, such
as replacing some nodes in mirageboards for Tama, Sylph, and 
Chocochick (the three automatically obtained mirages) with 
field abilities.

Instructions:
==================================================================
To install properly, you will need Python 3.8+ installed. 

Extract or unzip the compressed folder "enemyRando" next to the 
WOFF executable. Go into the enemyRando folder, right-click an 
empty space and hit "Open Terminal" or "Open Command Prompt" or 
some equivalent. Type "python install.py" to run the installer.
Type in a seed name if you desire. You will also be given the
choice to randomize bosses (it normally randomizes random 
encounters and rare monsters). The randomizer should run if 
it's in the correct folder, and then you should be good to go.

To uninstall, do the same as above, only type 
"python uninstall.py" instead and press enter/return when
prompted. 

Some details:
==================================================================
There is a monster_log.txt file in /logs. It serves as a reference
for where random and rare monsters are located, although some may 
disappear as a result of areas being cleared. Unfortunately, the 
game doesn't support the map having more than 12 mirages, so
I truncate what random mirages are shown. Regardless, there may be 
more than 12 mirages in an area, which is why the txt was made.


Changelog:
==================================================================
2025-28-3 - 0.1.0 completed




