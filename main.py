import argparse
import cv2
import matplotlib.pyplot as plt
import logging
import numpy as np

from colors import Colors, reduce_to
from drawing import draw_crosses, draw_flosses


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='data/image.jpg', help='Image to convert to scheme.')
    parser.add_argument('--enhance', type=bool, default=True, help='Whether to attempt to enhance image colors.')
    parser.add_argument('--width', type=int, default=120, help='Number of crosses in row.')
    parser.add_argument('--max_colors', type=int, default=15, help='Max number of flosses to use.')
    parser.add_argument('--show', type=bool, default=True, help='Whether to show result in separate window.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    dpi = 300
    colors = Colors()
    filename = 'data/image.jpg'
    image = cv2.imread(args.image)
    if args.enhance:
        img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    width = args.width
    image = cv2.resize(image, (width, width * image.shape[0] // image.shape[1]))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = reduce_to(image, args.max_colors)
    image, flosses = colors.convert_image(image)
    for i, fl in enumerate(flosses):
        logger.info(f'{i + 1}. {colors.get(fl)[0]} (#{fl})')
    pattern = draw_crosses(image, dpi)
    fl_image = draw_flosses(image, [(fl, colors.get(fl), flosses[fl]) for fl in flosses], dpi)
    scheme_width = max(pattern.shape[1], fl_image.shape[1])
    scheme = 255 * np.ones((pattern.shape[0] + fl_image.shape[0], scheme_width, 3), dtype=np.uint8)
    scheme[:pattern.shape[0], :pattern.shape[1], :] = pattern
    scheme[pattern.shape[0]:pattern.shape[0] + fl_image.shape[0], :fl_image.shape[1], :] = fl_image
    logger.info(f'Scheme size is {scheme.shape[1] / dpi * 2.54:2.1f}cm x {scheme.shape[0] / dpi * 2.54:2.1f}cm')
    cv2.imwrite('data/scheme.png', cv2.cvtColor(scheme, cv2.COLOR_RGB2BGR))

    if args.show:
        plt.imshow(scheme)
        x_ticks = np.linspace(0, scheme.shape[0] + 9, 10)
        plt.xticks(x_ticks, [f'{x / dpi * 2.54:2.1f}' for x in x_ticks])
        y_ticks = np.linspace(0, scheme.shape[1] + 9, 10)
        plt.yticks(x_ticks, [f'{x / dpi * 2.54:2.1f}' for x in y_ticks])
        plt.show()
