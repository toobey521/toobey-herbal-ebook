#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toobey本草食蔬 - 版本资源文件生成器
生成 PyInstaller --version-file 可用的版本信息文件
"""
import sys, os

# 直接用字符串构建 PyInstaller 能解析的版本文件格式
VERSION_TXT = """# UTF-8
#
# Toobey本草食蔬 - 蔬菜性味寒热属性与药用价值电子书
# Copyright(C)2026-2099 Toobey
#
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'Toobey'),
          StringStruct('FileDescription', 'Toobey本草食蔬 - 蔬菜性味寒热属性与药用价值电子书'),
          StringStruct('FileVersion', '1.0.0.0'),
          StringStruct('InternalName', 'ToobeyVeggieEbook'),
          StringStruct('LegalCopyright', 'Copyright(C)2026-2099 Toobey'),
          StringStruct('OriginalFilename', 'Toobey本草食蔬.exe'),
          StringStruct('ProductName', 'Toobey本草食蔬'),
          StringStruct('ProductVersion', '1.0.0.0')])
      ]),
    VarFileInfo([VarStruct('Translation', (1033, 1200))])
  ]
)
"""

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "version_info.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(VERSION_TXT)
    print(f"Version file written: {out_path}")
