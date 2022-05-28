import os
import sys
import cv2

import numpy as np
from pathlib import Path
from face_recognition import face_encodings, face_distance

from keras import backend as K

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

# add packages to python load paths
sys.path.append(str(BASE_PATH.parent.resolve()))
sys.path.append(str((BASE_PATH.parent / 'detection').resolve()))
sys.path.append(str((BASE_PATH.parent / 'recognition').resolve()))

# module or package level imports
from detection import FaceDetector
from recognizer_utils import Database

K.set_image_data_format('channels_first')

class FaceRecognizer:
    
    def __init__(self, path='vitals/database.json') -> None:
        self.model = face_encodings
        self.detector = FaceDetector()
        self.database = Database.from_json_file(BASE_PATH / path) if path else None

    def get_locations(self, image):
        return self.detector(image)

    def get_faces(self, image):
        locations = self.detector(image)
        ecodings = face_encodings(image, locations)
        return list(zip(locations, ecodings))

    def __call__(self, image, tolerance=0.3):
        results = []

        for loc, encoding in self.get_faces(image):
            name = 'unknown'
            # find the euclidean distance between known faces and new face
            distances = face_distance(self.database.encodings, encoding)
            # index of matched face encoding with minimum euclidean distance
            best_match_index = np.argmin(distances)
            print(distances)
            # Check if the face is enough accurate to be recognized
            if distances[best_match_index] <= tolerance:
                name = self.database.names[best_match_index]
                
            results.append((name, loc))
        
        return results

    def mark(self, results, image):
        for label, coors in results:
            cv2.rectangle(image, (coors[0], coors[1]), (coors[2], coors[3]), [0,0,255], 2)
            cv2.rectangle(image, (coors[0], coors[3]), (coors[2], coors[3] + 50), (0, 0, 255), cv2.FILLED)
            cv2.putText(image, label, (coors[0]+10,coors[3]+40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, [255,255,255], 2, cv2.LINE_AA)

        return image


if __name__ == "__main__":
    test_folder = BASE_PATH / 'tests'
    save_dir = BASE_PATH / 'results'
    model = FaceRecognizer()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            print(str(BASE_PATH / 'results' / file))
            cv2.imwrite(str(BASE_PATH / 'results' / file), image)