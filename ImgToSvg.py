import os

import numpy as np
from PIL import Image, ImageOps
import argparse


def convert_png_to_jpg(image_path):
    img = Image.open(image_path)
    try:
        alpha = img.getchannel('A')
        alpha = Image.merge('RGB', (alpha, alpha, alpha))
    except ValueError:
        return convert_to_jpg(image_path)
    alpha = ImageOps.invert(alpha)
    image_path = os.path.splitext(image_path)[0] + '.jpg'
    alpha.save(image_path)
    return image_path


def convert_to_jpg(image_path):
    """
    :param image_path: 任意图片文件
    :return: 输出jpg图片路径
    """
    img = Image.open(image_path).convert('RGB')
    r, g, b = img.split()
    result = Image.merge('RGB', (r, g, b))
    image_path = os.path.splitext(image_path)[0] + '.jpg'
    result.save(image_path)
    return image_path


def convert_to_bmp(image_path):
    """
    :param image_path: 任意图片文件
    :return: 输出bmp格式文件路径
    """
    if os.path.splitext(image_path)[1] in ['.jpg', '.jpeg', '.JPG', '.JPEG']:
        print('传入文件不为BMP正在转换为bmp格式', image_path)
        img = Image.open(image_path)
        ary = np.array(img)

        # 将 RGB 图像转换为灰度图像
        if ary.shape[2] == 3:  # 确保图像有三个通道
            r, g, b = np.split(ary, 3, axis=2)
            gray = list(
                map(lambda x: 0.299 * x[0] + 0.587 * x[1] + 0.114 * x[2], zip(r.reshape(-1), g.reshape(-1), b.reshape(-1))))
            bitmap = np.array(gray).reshape((ary.shape[0], ary.shape[1]))
            bitmap = np.dot((bitmap > 128).astype(float), 255)

            # 保存为 BMP 文件
            im = Image.fromarray(bitmap.astype(np.uint8))

            name = os.path.splitext(image_path)[0] + '.bmp'
            im.save(name)
            return name
        else:
            print('图像不包含三个通道 [R,G,B]')
            return False
    elif os.path.splitext(image_path)[1] in ['.png', '.PNG']:
        jpg_file = convert_png_to_jpg(image_path)
        outfile = convert_to_bmp(jpg_file)
        os.remove(jpg_file)
        return outfile
    else:
        print('不支持的文件类型')
        return False


def out_svg(file):
    """
    :param file:输入文件格式[png,jpg,bmp]
    :return:cmd状态信息
    """
    img_type = True
    if os.path.splitext(file)[1] in ['.bmp', '.BMP']:
        img_type = False
    file = os.path.abspath(file)
    cmd_path = os.path.join(os.path.dirname(__file__), 'potraces', 'potrace.exe')
    file = convert_to_bmp(file) if not os.path.splitext(file)[1] == '.bmp' else file
    # 判断文件格式如果是bmp就交到下一步不是就调用out_bmp将图片转换到bmp
    if file:
        inx = os.popen(f'{cmd_path} --svg "{file}"').read()
        os.remove(file) if img_type and os.path.exists(file) else None
        return inx.rstrip()
    else:
        return False


def ImgToSvg(*img_paths):
    print('\n')
    for img_path in img_paths:
        if os.path.exists(img_path):
            print('处理文件路径:', img_path, end='\n')
            print(out_svg(img_path))
        else:
            print('文件不存在:', img_path)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 这里是程序主入口
    print('支持的文件类型有:png,jpg,bmp。')
    print('如需更快的执行速度请直接传入bmp格式图片。')
    parser = argparse.ArgumentParser(description='转换图片到svg矢量格式.')
    parser.add_argument('img_paths', metavar='N', type=str, nargs='+', help='输入要转换的文件路径。')
    args = parser.parse_args()
    print('程序运行中请稍后，正在处理图片...{}'.format(args.img_paths))
    ImgToSvg(*args.img_paths)