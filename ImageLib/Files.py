import os
import uuid

from PIL import Image, ImageOps

import logging

# 配置日志记录器
logger = logging.getLogger("Vector")

TMP_PATH = os.getenv('TEMP', '/tmp')

def convert_rgb(image_path,name):
    """
    将CMYK图片转换为RGB格式
    :param image_path: CMYK图片文件路径
    :return: 输出RGB图片路径
    """
    if not image_path.lower().endswith(('.jpg', '.jpeg','.bmp')):
        return logger.warning(f"[格式错误]: 输入文件不是支持的图片格式 -x {image_path}")

    img = Image.open(image_path)
    if img.mode == 'CMYK':
        img = img.convert('RGB')
    rgb_path = os.path.join(TMP_PATH, name + '_rgb.jpg')
    img.save(rgb_path, 'JPEG')
    return rgb_path


def convert_jpg(image_path,name):
    """
    将PNG图片转换为JPG格式
    :param image_path: PNG图片文件路径
    :return: 输出JPG图片路径
    """
    if not image_path.lower().endswith('.png'):
        return logger.warning(f"[格式错误]: 输入文件不是PNG格式 -x {image_path}")
    img = Image.open(image_path)
    alpha = img.getchannel('A')
    alpha = Image.merge('RGB', (alpha, alpha, alpha))

    alpha = ImageOps.invert(alpha)
    jpg_path = os.path.join(TMP_PATH,name + '.jpg')
    alpha.save(jpg_path, 'JPEG')
    return jpg_path

def convert_bmp(image_path,name):
    """
    将JPG图片转换为BMP格式
    :param image_path: JPG图片文件路径
    :return: 输出BMP图片路径
    """
    if not image_path.lower().endswith(('.jpg', '.jpeg')):
        return logger.warning(f"[格式错误]: 输入文件不是JPG格式 -x {image_path}")

    img = Image.open(image_path)
    bmp_path = os.path.join(TMP_PATH,name + '.bmp')
    img.save(bmp_path, 'BMP')
    return bmp_path

def potrace_cmd(image_path,out_path,type='svg'):
    """
    :param file:输入文件格式[png,jpg,bmp]
    :return:cmd状态信息
    """
    if not image_path.lower().endswith(('.bmp', '.BMP')):
        return logger.warning(f"[格式错误]: BMP格式文件才能转换为SVG格式 -x {image_path}")
    out_path = os.path.abspath(out_path)
    if type == 'svg':
        potrace = os.path.join(os.path.dirname(__file__), 'potraces', 'potrace.exe')
        cmd = f'{potrace} --svg "{image_path}" -o "{out_path}"'
        inx = os.popen(cmd).read()
        return inx.rstrip()
    elif type == 'pdf':
        potrace = os.path.join(os.path.dirname(__file__), 'potraces', 'potrace.exe')
        cmd = f'{potrace} --pdf "{image_path}" -o "{out_path}"'
        inx = os.popen(cmd).read()
        return inx.rstrip()
    elif type == 'eps':
        potrace = os.path.join(os.path.dirname(__file__), 'potraces', 'potrace.exe')
        cmd = f'{potrace} --eps "{image_path}" -o "{out_path}"'
        inx = os.popen(cmd).read()
        return inx.rstrip()

def image_grayscale(image_path):
    """
    将图片转换为灰度图

    :param image_path: 图片文件路径
    :return: 输出灰度图路径
    """
    img = Image.open(image_path).convert('L')
    grayscale_path = os.path.splitext(image_path)[0] + '_grayscale' + os.path.splitext(image_path)[1]
    img.save(grayscale_path)
    return grayscale_path

def image_property(image_path):
    """
    获取图片的宽度和高度

    :param image_path: 图片文件路径
    :return: 图片的宽度和高度
    """
    img = Image.open(image_path)
    id = str(uuid.uuid4()).split('-')[0]
    info = {
        "id":id,
        "path":img.filename,
        "size":img.size,
        "format":img.format,
        "mode":img.mode,
        "temp":{
        }
    }
    return info

def iter_files_in_directory(directory):
    """
    递归遍历目录下的所有文件并返回一个迭代器

    :param directory: 目录路径
    :return: 文件路径迭代器
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def RecycleTempFiles(date):
    for k, v in date['temp'].items():
        if v and os.path.exists(v):
            os.remove(v)

def VectorConversion(*paths,out_type='svg'):
    """
    将图片转换为矢量图

    :param paths: 图片文件路径列表
    :param out_type: 输出文件类型
    :return date: 图片信息
    """
    def vector(path,out_type='svg'):
        if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            return logger.warning(f"[格式错误]: 输入文件不是PNG,JPG,BMP格式 -x {path}")
        logger.info(f'[处理文件]: {path} -> [{out_type}]:{os.path.splitext(path)[0]}.{out_type}')
        path = os.path.abspath(path)
        date = image_property(path)
        if date['format'] == 'JPEG':
            if date['mode'] == 'CMYK':
                date['temp']['rgb'] = convert_rgb(path,date['id'])
                date['temp']['bmp'] = convert_bmp(date['temp']['rgb'],date['id'])
            else:
                date['temp']['bmp'] = convert_bmp(path,date['id'])
        elif date['format'] == 'PNG':
            date['temp']['jpg'] = convert_jpg(path,date['id'])
            date['temp']['bmp'] = convert_bmp(date['temp']['jpg'],date['id'])
        else:
            return logger.warning(f"[格式错误]: 输入文件不是PNG,JPG格式 -x {path}")
        out_path = os.path.splitext(path)[0] + f'.{out_type}'
        potrace_cmd(date['temp']['bmp'],out_path,type=out_type)
        RecycleTempFiles(date)
        return date
    dates = []
    for p in paths:
        if os.path.isdir(p):
            for i in iter_files_in_directory(p):
                dates.append(vector(i,out_type))
        elif os.path.isfile(p):
            dates.append(vector(p,out_type))
        else:
            logger.error(f'[路径错误]: 文件或目录不存在:{p}')
    dates = [i for i in dates if i]
    return dates