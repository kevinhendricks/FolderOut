**FolderOUT** is a python 3.4 output plugin for Sigil 
that will copy the files inside an epub to a a Folder

[Plugin] FolderOut - Folder output plugin for Sigil
Updated: February 2, 2018

License/Copying: GNU LGPL Version 2 or Version 3 your choice. Any other license terms are only available directly from the author in writing.

The purpose of this plugins is to provide the ability for Sigil to save epub files to a folder.
Thereby allowing ebook developers to more easily interface to git or some other version control system.

Note:
This plugin will not work with Python 2.7. They are designed to work with more recent versions of Sigil that have an embedded Python 3.X interpreter .

Note:
Since unzipped files in open folders can be changed by other tools, any embedded fonts are stored unobfuscated and both plugins will refuse to work with folders that have an encryption.xml file present in the META-INF folder to prevent obfuscation/unobfuscation mismatches from destroying the font files. Before producing the final epub using Sigil (or any other software), the proper embedded font subsetting and/or obfuscating should be performed depending on the license of the fonts embedded.

See the Sigil Plugin Index on MobileRead to find out more about this plugin and other plugins available for Sigil:
https://www.mobileread.com/forums/showthread.php?t=247431

