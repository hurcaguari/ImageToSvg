import os
import sys


def Initialize():
    bl_path = sys.argv[0]
    blender_python = os.path.split(bl_path)[0] + '\\4.0\\python\\bin\\python.exe'
    pip_list = os.popen(f'"{blender_python}" -m pip list').read()
    pip_list = pip_list.splitlines()
    pak_lists = []
    srt_list = [
        'Active code page: 65001',
        '------------------ ---------',
        'Package            Version'
    ]
    for i in pip_list:
        if i not in srt_list:
            str_tmp = i.split(' ')
            str_tmp = [item for item in str_tmp if item]
            pak_lists.append(str_tmp[0])

    init_pak = [
        'numpy',
        'pillow'
    ]
    for pak in init_pak:
        print(os.popen(f'"{blender_python}" -m pip install {pak}').read()) if pak not in pak_lists else None
