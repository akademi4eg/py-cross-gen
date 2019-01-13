import numpy as np
import cv2
import logging

from colors import get_symbol, get_text_color


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def draw_crosses(image, dpi):
    """
    Draws crosses pattern.
    :param image: Properly processed image with one pixel per cross.
    :param dpi: DPI for printing.
    :return: Image of pattern.
    """
    cross_size = int(0.3 * dpi / 2.54)  # 3mm cross size
    line_size = int(0.05 * dpi / 2.54)  # 0.5mm line size
    line_size += line_size % 2  # ensure line size is even
    cell_size = cross_size + line_size
    logger.info(f'Cell size: {cell_size}, line width: {line_size}, cross size: {cross_size}')
    new_image = 255 * np.ones((cell_size * image.shape[0], cell_size * image.shape[1], 3), dtype=np.uint8)
    logger.info(f'Image is {new_image.shape[1] / dpi * 2.54:2.1f}cm x {new_image.shape[0] / dpi * 2.54:2.1f}cm')
    # pattern
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            x_offset = x * cell_size + line_size // 2
            y_offset = y * cell_size + line_size // 2
            new_image[x_offset:x_offset + cross_size, y_offset:y_offset + cross_size, :] = image[x, y, :]
            cv2.putText(new_image, get_symbol(image[x, y, :]),
                        (y_offset + 6, x_offset + cross_size // 2 + line_size + 4),
                        cv2.FONT_HERSHEY_COMPLEX, 1.0, get_text_color(image[x, y, :]), 1, lineType=cv2.LINE_AA)
    # lines
    grey = 150
    black = 0
    # horizontal grey
    for x in range(0, new_image.shape[0], cell_size):
        new_image[x - line_size // 2:x + line_size // 2 + 1, :, :] = grey
    # vertical grey
    for x in range(0, new_image.shape[1], cell_size):
        new_image[:, x - line_size // 2:x + line_size // 2 + 1, :] = grey
    # horizontal black
    new_image[:line_size // 2 + 1, :, :] = black
    new_image[- line_size // 2:, :, :] = black
    for x in range(0, new_image.shape[0], cell_size * 5):
        new_image[x - line_size // 2:x + line_size // 2 + 1, :, :] = black
    # vertical black
    new_image[:, :line_size // 2 + 1, :] = black
    new_image[:, - line_size // 2:, :] = black
    for x in range(0, new_image.shape[1], cell_size * 5):
        new_image[:, x - line_size // 2:x + line_size // 2 + 1, :] = black
    # middle marker
    for d in range(-line_size // 2, line_size // 2 + 1):
        new_image[new_image.shape[0] // 2 + d, :, 0] = 200
        new_image[new_image.shape[0] // 2 + d, :, 1] = 0
        new_image[new_image.shape[0] // 2 + d, :, 2] = 0
        new_image[:, new_image.shape[1] // 2 + d, 0] = 200
        new_image[:, new_image.shape[1] // 2 + d, 1] = 0
        new_image[:, new_image.shape[1] // 2 + d, 2] = 0

    margin = int(1.5 * dpi / 2.54)  # 1.5cm margin
    framed = 255 * np.ones((2 * margin + new_image.shape[0], 2 * margin + new_image.shape[1], 3), dtype=np.uint8)
    framed[margin:-margin, margin:-margin, :] = new_image

    # rows labels
    for x in range(cell_size * 10, framed.shape[0] - 2 * margin, cell_size * 10):
        cv2.putText(framed, f'{x // cell_size}', (framed.shape[1] - margin + 20, margin + x + 2 * line_size),
                    cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), 2, lineType=cv2.LINE_AA)
    # columns labels
    for x in range(cell_size * 10, framed.shape[1] - 2 * margin, cell_size * 10):
        cv2.putText(framed, f'{x // cell_size}', (margin + x - cell_size, margin - 20),
                    cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), 2, lineType=cv2.LINE_AA)
    # size
    cv2.putText(framed, f'{image.shape[1]}x{image.shape[0]}',
                (framed.shape[1] // 2 - 2 * margin, framed.shape[0] - margin // 2),
                cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), 2, lineType=cv2.LINE_AA)
    logger.info(f'Printout image is {framed.shape[1] / dpi * 2.54:2.1f}cm x {framed.shape[0] / dpi * 2.54:2.1f}cm')
    return framed


def draw_flosses(orig_image, flosses, dpi):
    """
    Draws flosses legend and image preview.
    :param orig_image: Image to show in preview.
    :param flosses: Flosses information in format: [(id, (name, color), quantity), ...]
    :param dpi: DPI for printing.
    :return: Image of flosses legend.
    """
    flosses = sorted(flosses, key=lambda x: -x[2])
    cross_size = int(0.6 * dpi / 2.54)  # 6mm cross size
    margin = int(0.2 * dpi / 2.54)  # 2mm margin
    cell_size = cross_size + margin * 2
    col_width = int(12.0 * dpi / 2.54)  # 12cm per column
    per_col = 8
    image = 255 * np.ones((cell_size * per_col + margin * 2,
                           col_width * int(len(flosses) / per_col + 0.5) + margin * 2, 3), dtype=np.uint8)
    for i, fl in enumerate(flosses):
        col = i // per_col
        cv2.rectangle(image, (col * col_width + margin, margin + (i % per_col) * cell_size),
                      (col * col_width + margin + cross_size, margin + (i % per_col) * cell_size + cross_size),
                      fl[1][1], thickness=-1)
        cv2.putText(image, get_symbol(fl[1][1]),
                    (col * col_width + margin + 9, margin + (i % per_col) * cell_size + cell_size // 2 - 4),
                    cv2.FONT_HERSHEY_COMPLEX, 2.0, get_text_color(fl[1][1]), 2, lineType=cv2.LINE_AA)
        text = f'(#{fl[0]}) {fl[1][0]}: {fl[2]}'
        cv2.putText(image, text, (col * col_width + cell_size,
                                  margin + (i % per_col) * cell_size + cell_size // 2),
                    cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 0), 2, lineType=cv2.LINE_AA)
    new_height = int(orig_image.shape[0] / orig_image.shape[1] * col_width)
    orig_image = cv2.resize(orig_image, (col_width, new_height))

    delta = new_height - image.shape[0]
    if delta > 0:
        image = np.pad(image, [[0, new_height - image.shape[0]], [0, 0], [0, 0]], 'constant', constant_values=255)
    else:
        orig_image = np.pad(orig_image, [[0, image.shape[0] - new_height], [0, 0], [0, 0]],
                            'constant', constant_values=255)
    image = np.concatenate((image, orig_image), axis=1)
    frame_margin = int(1.5 * dpi / 2.54)  # 1.5cm margin
    framed = 255 * np.ones((image.shape[0] + frame_margin, 2 * frame_margin + image.shape[1], 3), dtype=np.uint8)
    framed[:-frame_margin, frame_margin:-frame_margin, :] = image
    logger.info(f'Printout flosses map is {framed.shape[1] / dpi * 2.54:2.1f}cm x {framed.shape[0] / dpi * 2.54:2.1f}cm')
    return framed
