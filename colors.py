import csv
from tqdm import tqdm
import logging
from sklearn.cluster import k_means
from collections import Counter


# Symbols for flosses legend.
SYMBOLS = ['*', '-', '+', 'T', '>', '<', 'V', 'O', 'X', 'U', 'B', 'A', 'X', '||', '^']


def get_text_color(color):
    """Gets color that would be visible on given background."""
    return (255, 255, 255) if sum(color) / 3 < 130 else (0, 0, 0)


def get_symbol(color):
    """
    Gets symbol for a given color.
    We don't care for collisions much. Just probability of two similar colors having the same symbol should be low.
    """
    return SYMBOLS[(color[0] * 17 + color[1] * 11 + color[2]) % len(SYMBOLS)]


def get_distance(color1, color2):
    """Distance between two colors."""
    return sum([((color1[i] - color2[i]) ** 2) for i in range(3)])


def reduce_to(image, num_colors):
    """Reduces number of image colors to at most `num_colors`."""
    logger = logging.getLogger(__name__)
    new_image = image.copy()
    data = image.reshape((-1, 3))
    logger.info(f'Original image had {data.shape[0]} colors. Reducing to {num_colors}.')
    clusters, indexes, _ = k_means(data, num_colors)
    for x in range(new_image.shape[0]):
        for y in range(new_image.shape[1]):
            new_image[x, y, :] = clusters[indexes[x * new_image.shape[1] + y], :]
    return new_image


class Colors:
    """Covers most of work with flosses."""
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._data = {}
        # Colors data taken from https://github.com/adrianj/CrossStitchCreator/
        with open('data/colors.csv', 'r') as f:
            for r in csv.DictReader(f):
                self._data[r['Floss#']] = (r['Description'], (int(r['Red']), int(r['Green']), int(r['Blue'])))
        self._map = {}

    def closest(self, ref):
        ref = (int(ref[0]), int(ref[1]), int(ref[2]))
        try:
            return self._map[ref]
        except KeyError:
            colors = sorted(self._data, key=lambda x: get_distance(ref, self._data[x][1]))
            self._map[ref] = colors[0]
            return colors[0]

    def get(self, f_id):
        return self._data[f_id]

    def convert_image(self, image):
        self._map = {}
        counter = Counter()
        new_image = image.copy()
        for x in tqdm(range(image.shape[0]), desc='Converting to flosses'):
            for y in range(image.shape[1]):
                new_image[x, y, :] = self.get(self.closest(image[x, y, :]))[1]
                counter[tuple(new_image[x, y, :])] += 1
        flosses = {f_id: counter[self._data[f_id][1]] for f_id in self._map.values()}
        self._logger.info(f'Image has {len(flosses)} unique flosses.')
        return new_image, flosses
