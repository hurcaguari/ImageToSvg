
import argparse
import logging
import os
import sys
from ImageLib import VectorConversion
from ImageLib import setup_logging


if __name__ == '__main__':
    sys.stdout.flush()
    sys.stderr.flush()

    setup_logging()
    logger = logging.getLogger("Main")
    
    # 这里是程序主入口
    parser = argparse.ArgumentParser(description='转换图片到矢量格式.')
    parser.add_argument('img_paths', metavar='P', type=str, nargs='+', 
                       help='输入要转换的文件路径(支持文件夹): [png,jpg,bmp]')
    parser.add_argument('-t', '--type', metavar='T', type=str, nargs='?', 
                       default='svg', choices=['svg', 'eps', 'pdf'],
                       help='要输出的文件类型(默认: svg): [svg,eps,pdf]')

    # 如果没有提供参数，则显示帮助信息
    if len(os.sys.argv) == 1:
        parser.print_help()
        input('按任意键退出...')
        sys.exit(0)
    
    try:
        args = parser.parse_args()
        logger.info('[正在启动]: 程序运行中请稍后，正在处理图片...')
        logger.info('[文件类型]: [{}]'.format(args.type))
        logger.info('[文件路径]: {}'.format(args.img_paths))
        
        results = VectorConversion(*args.img_paths, out_type=args.type)
        
        if results:
            logger.info('[处理完成]: 成功处理 {} 个图片文件。'.format(len(results)))
        else:
            logger.warning('[处理完成]: 没有成功处理任何图片文件。')
            
    except KeyboardInterrupt:
        logger.info('[用户中断]: 程序被用户中断。')
        sys.exit(1)
    except Exception as e:
        logger.error('[程序错误]: {}'.format(e))
        sys.exit(1)
    
    input('按任意键退出...')
    sys.exit(0)