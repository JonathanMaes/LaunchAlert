# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

# changelog = open('./changelog.txt', 'r', encoding='utf-8')
# versionStr = changelog[0]
# versionTuple = (versionStr.split('.')[0], versionStr.split('.')[1], versionStr.split('.')[2], 0)

VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[0]), int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[1]), int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[2]), 0),
    prodvers=(int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[0]), int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[1]), int(open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0].split('.')[2]), 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'Jonathan\'s Launch Notifications'),
        StringStruct(u'FileVersion', open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0]),
        StringStruct(u'InternalName', u'Jonathan\'s Launch Notifications'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2019 Jonathan Maes'),
        StringStruct(u'LegalTrademarks', u'Copyright (C) 2019 Jonathan Maes'),
        StringStruct(u'OriginalFilename', u'main.exe'),
        StringStruct(u'ProductName', u'Jonathan\'s Launch Notifications'),
        StringStruct(u'ProductVersion', open('./changelog.txt', 'r', encoding='utf-8').read().split('\n')[0]),
        StringStruct(u'Debugger', u'0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) # 1033 is US English, 1200 is Unicode
  ]
)
