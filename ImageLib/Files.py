import os
import platform
import subprocess
import uuid
import warnings
from typing import Dict, List, Optional, Iterator

from PIL import Image, ImageOps

import logging

# 配置日志记录器
logger = logging.getLogger("Vector")

# 或者禁用 DecompressionBombWarning 警告
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# 常量定义
TMP_PATH = os.getenv('TEMP', '/tmp')
SUPPORTED_INPUT_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp')
SUPPORTED_OUTPUT_FORMATS = ('svg', 'eps', 'pdf')

# 获取 potrace 可执行文件路径
def get_potrace_path() -> str:
    """获取适合当前操作系统的 potrace 可执行文件路径"""
    if platform.system() == 'Windows':
        return os.path.join(os.path.dirname(__file__), 'potraces', 'potrace.exe')
    else:
        return 'potrace'  # Unix 系统使用系统路径

def convert_rgb(image_path: str, name: str) -> Optional[str]:
    """
    将CMYK图片转换为RGB格式
    :param image_path: CMYK图片文件路径
    :param name: 输出文件名前缀
    :return: 输出RGB图片路径，失败返回None
    """
    if not image_path.lower().endswith(('.jpg', '.jpeg', '.bmp')):
        logger.warning(f"[格式错误]: 输入文件不是支持的图片格式 -x {image_path}")
        return None

    try:
        with Image.open(image_path) as img:
            if img.mode == 'CMYK':
                img = img.convert('RGB')
            rgb_path = os.path.join(TMP_PATH, name + '_rgb.jpg')
            img.save(rgb_path, 'JPEG')
            return rgb_path
    except Exception as e:
        logger.error(f"[转换错误]: RGB转换失败 {image_path} - {e}")
        return None


def convert_jpg(image_path: str, name: str) -> Optional[str]:
    """
    将PNG图片转换为JPG格式
    :param image_path: PNG图片文件路径
    :param name: 输出文件名前缀
    :return: 输出JPG图片路径，失败返回None
    """
    if not image_path.lower().endswith('.png'):
        logger.warning(f"[格式错误]: 输入文件不是PNG格式 -x {image_path}")
        return None
    
    try:
        with Image.open(image_path) as img:
            jpg_path = os.path.join(TMP_PATH, name + '.jpg')
            if img.mode == 'RGBA':
                alpha = img.getchannel('A')
                alpha = Image.merge('RGB', (alpha, alpha, alpha))
                alpha = ImageOps.invert(alpha)
                alpha.save(jpg_path, 'JPEG')
            else:
                img.convert('RGB').save(jpg_path, 'JPEG')
            return jpg_path
    except Exception as e:
        logger.error(f"[转换错误]: JPG转换失败 {image_path} - {e}")
        return None

def convert_bmp(image_path: str, name: str) -> Optional[str]:
    """
    将JPG图片转换为BMP格式
    :param image_path: JPG图片文件路径
    :param name: 输出文件名前缀
    :return: 输出BMP图片路径，失败返回None
    """
    if not image_path.lower().endswith(('.jpg', '.jpeg')):
        logger.warning(f"[格式错误]: 输入文件不是JPG格式 -x {image_path}")
        return None

    try:
        with Image.open(image_path) as img:
            bmp_path = os.path.join(TMP_PATH, name + '.bmp')
            img.save(bmp_path, 'BMP')
            return bmp_path
    except Exception as e:
        logger.error(f"[转换错误]: BMP转换失败 {image_path} - {e}")
        return None

def potrace_cmd(image_path: str, out_path: str, type: str = 'svg') -> Optional[str]:
    """
    使用potrace将BMP图片转换为矢量格式
    :param image_path: 输入文件格式[bmp]
    :param out_path: 输出文件路径
    :param type: 输出格式类型 [svg, eps, pdf]
    :return: 命令执行状态信息，失败返回None
    """
    if not image_path.lower().endswith(('.bmp', '.BMP')):
        logger.warning(f"[格式错误]: BMP格式文件才能转换为矢量格式 -x {image_path}")
        return None
    
    if type not in SUPPORTED_OUTPUT_FORMATS:
        logger.warning(f"[格式错误]: 不支持的输出格式 {type}")
        return None
    
    out_path = os.path.abspath(out_path)
    potrace = get_potrace_path()
    
    try:
        cmd = [potrace, f'--{type}', image_path, '-o', out_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            return result.stdout.strip() if result.stdout else "转换成功"
        else:
            logger.error(f"[转换错误]: Potrace执行失败 - {result.stderr}")
            return None
    except FileNotFoundError:
        logger.error(f"[系统错误]: 找不到potrace可执行文件: {potrace}")
        return None
    except Exception as e:
        logger.error(f"[转换错误]: Potrace执行异常 - {e}")
        return None

def image_grayscale(image_path: str) -> Optional[str]:
    """
    将图片转换为灰度图

    :param image_path: 图片文件路径
    :return: 输出灰度图路径，失败返回None
    """
    try:
        with Image.open(image_path) as img:
            grayscale_img = img.convert('L')
            grayscale_path = os.path.splitext(image_path)[0] + '_grayscale' + os.path.splitext(image_path)[1]
            grayscale_img.save(grayscale_path)
            return grayscale_path
    except Exception as e:
        logger.error(f"[转换错误]: 灰度图转换失败 {image_path} - {e}")
        return None

def image_property(image_path: str) -> Optional[Dict]:
    """
    获取图片的属性信息

    :param image_path: 图片文件路径
    :return: 图片信息字典，失败返回None
    """
    try:
        with Image.open(image_path) as img:
            id = str(uuid.uuid4()).split('-')[0]
            info = {
                "id": id,
                "path": img.filename,
                "size": img.size,
                "format": img.format,
                "mode": img.mode,
                "temp": {}
            }
            return info
    except Exception as e:
        logger.error(f"[读取错误]: 无法读取图片属性 {image_path} - {e}")
        return None

def iter_files_in_directory(directory: str) -> Iterator[str]:
    """
    递归遍历目录下的所有文件并返回一个迭代器

    :param directory: 目录路径
    :return: 文件路径迭代器
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def RecycleTempFiles(date: Dict) -> None:
    """
    清理临时文件
    
    :param date: 包含临时文件路径的字典
    """
    for k, v in date.get('temp', {}).items():
        if v and os.path.exists(v):
            try:
                os.remove(v)
            except Exception as e:
                logger.warning(f"[清理警告]: 无法删除临时文件 {v} - {e}")

def VectorConversion(*paths, out_type: str = 'svg') -> List[Optional[Dict]]:
    """
    将图片转换为矢量图

    :param paths: 图片文件路径列表
    :param out_type: 输出文件类型
    :return: 图片信息列表
    """
    def vector(path: str, out_type: str = 'svg') -> Optional[Dict]:
        """
        处理单个图片文件
        
        :param path: 图片文件路径
        :param out_type: 输出格式
        :return: 图片信息字典，失败返回None
        """
        try:
            if not path.lower().endswith(SUPPORTED_INPUT_FORMATS):
                logger.warning(f"[格式错误]: 输入文件不是支持的格式 -x {path}")
                return None
            
            if not os.path.isfile(path):
                logger.warning(f"[路径错误]: 文件不存在 {path}")
                return None
                
            logger.info(f'[处理文件]: {path} -> [{out_type}]:{os.path.splitext(path)[0]}.{out_type}')
            path = os.path.abspath(path)
            date = image_property(path)
            
            if date is None:
                return None
            
            # 根据图片格式进行处理
            if date['format'] == 'JPEG':
                if date['mode'] == 'CMYK':
                    rgb_path = convert_rgb(path, date['id'])
                    if rgb_path is None:
                        return None
                    date['temp']['rgb'] = rgb_path
                    bmp_path = convert_bmp(rgb_path, date['id'])
                else:
                    bmp_path = convert_bmp(path, date['id'])
                
                if bmp_path is None:
                    RecycleTempFiles(date)
                    return None
                date['temp']['bmp'] = bmp_path
                
            elif date['format'] == 'PNG':
                jpg_path = convert_jpg(path, date['id'])
                if jpg_path is None:
                    return None
                date['temp']['jpg'] = jpg_path
                
                bmp_path = convert_bmp(jpg_path, date['id'])
                if bmp_path is None:
                    RecycleTempFiles(date)
                    return None
                date['temp']['bmp'] = bmp_path
                
            elif date['format'] == 'BMP':
                # BMP格式可以直接转换
                date['temp']['bmp'] = path
            else:
                logger.warning(f"[格式错误]: 不支持的图片格式 {date['format']} -x {path}")
                return None
            
            # 执行矢量转换
            out_path = os.path.splitext(path)[0] + f'.{out_type}'
            result = potrace_cmd(date['temp']['bmp'], out_path, type=out_type)
            
            # 清理临时文件
            RecycleTempFiles(date)
            
            if result is None:
                return None
                
            return date
            
        except Exception as e:
            logger.error(f'[数据错误]: {e}')
            return None
    
    # 验证输出格式
    if out_type not in SUPPORTED_OUTPUT_FORMATS:
        logger.error(f'[格式错误]: 不支持的输出格式 {out_type}')
        return []
    
    dates = []
    for p in paths:
        if os.path.isdir(p):
            for i in iter_files_in_directory(p):
                dates.append(vector(i, out_type))
        elif os.path.isfile(p):
            dates.append(vector(p, out_type))
        else:
            logger.error(f'[路径错误]: 文件或目录不存在: {p}')
    
    # 过滤掉None值
    dates = [i for i in dates if i is not None]
    return dates