import os
import json
import random
import numpy as np

from skimage import transform, exposure


def random_rotate(image):
    random_degree = random.uniform(-10, 10)
    new_img = 255 * transform.rotate(image, random_degree)
    new_img = new_img.astype(np.uint8)
    return new_img


def random_shear(image):
    random_degree = random.uniform(-0.1, 0.1)
    afine_tf = transform.AffineTransform(shear=random_degree)
    new_img = 255 * transform.warp(image, inverse_map=afine_tf)
    new_img = new_img.astype(np.uint8)
    return new_img


def change_contrast(image, percent_change=(0, 15)):
    percent_change = random.uniform(percent_change[0], percent_change[1])
    v_min, v_max = np.percentile(image, (0.0 + percent_change, 100.0 - percent_change))
    new_img = exposure.rescale_intensity(image, in_range=(v_min, v_max))
    new_img = new_img.astype(np.uint8)
    return new_img


def gamma_correction(image, gamma_range=(0.7, 1.0)):
    gamma = random.uniform(gamma_range[0], gamma_range[1])
    new_img = exposure.adjust_gamma(image, gamma=gamma, gain=random.uniform(0.8, 1.0))
    new_img = new_img.astype(np.uint8)
    return new_img


avail_transforms = {
    "rotate": random_rotate,
    "shear": random_shear,
    "contrast": change_contrast,
    "gamma": gamma_correction,
}

def apply_transform(image, num_transform=2):
    choices = random.sample(range(0, len(avail_transforms)), num_transform)
    img_out = image
    for choice in choices:
        operation = list(avail_transforms)[choice]
        img_out = avail_transforms[operation](img_out)
    return img_out


class Database:
    def __init__(self, encodings=[], names=[], emails={}) -> None:
        self.encodings = encodings
        self.names = names
        self.emails = emails

    @classmethod
    def from_json_file(cls, path):
        database = cls()
        with open(path) as file:
            data = json.load(file)

        for entitty in data:
            encodings = list(map(lambda array: np.array(array), entitty["encodings"]))

            database.encodings.extend(encodings)
            database.names.extend([entitty["label"]] * len(encodings))
            database.emails[entitty["label"]] = entitty["email"]

        return database

    @staticmethod
    def to_json_file(data, path, name):
        with open(os.path.join(path, name), "w") as file:
            json.dump(data, file, indent=4)
