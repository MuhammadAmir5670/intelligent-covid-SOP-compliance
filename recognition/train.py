import os
import cv2

from pathlib import Path

from inference import FaceRecognizer
from recognizer_utils import apply_transform, Database

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


class Prepare:
    def __init__(self, dir_path="faces_database", save_dir="vitals", model=None) -> None:
        self.dir_path = BASE_PATH / dir_path
        self.save_dir = BASE_PATH / save_dir
        self.model = model if model is not None else FaceRecognizer(path=False)

    def get_face(self, image):
        results = self.model.get_faces(image)
        if len(results):
            return results[0]
        return None, None

    def generate_database(self, augmentations=2, output_name="database.json"):
        encoded_database = []

        # For each person director in facesdatabase directory
        for root, _, files in os.walk(self.dir_path):
            print("\n\n--------------------------------------------\n")

            database = {"encodings": []}
            # for each image file in person directory
            for file_name in files:
                # Name of the person based on the directory name
                database["label"], database["email"] = list(map(lambda value: value.strip(), os.path.basename(root).split("-")))

                print(f"Prerprocessing data for {database['label']}")
                # complete absolute path to image file
                file_path = Path(root) / file_name

                # Read the image from the disk
                image = cv2.imread(str(file_path))

                # Number of Augmentations to perform for each image
                operations = augmentations + 1
                for ops in range(operations):
                    print("Augmentations # ", ops + 1)

                    if ops > 0:
                        image = apply_transform(image, num_transform=2)

                    location, encoding = self.get_face(image)
                    if location != None:
                        database["encodings"].append(encoding.tolist())

                    print(
                        f"Face of {file_name} {files.index(file_name)+1}-{ops} folder added to Encoded Database"
                    )

            if len(files):
                encoded_database.append(database)

        Database.to_json_file(encoded_database, self.save_dir, output_name)


if __name__ == "__main__":
    prepare = Prepare()
    prepare.generate_database()
