import numpy as np
import string
import random


def generate_dummy_data():
    # generate random coordinates for the face bounding box
    x1, y1, x2, y2 = np.random.randint(0, 1280, size=4)
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # generate a random 512-dimensional embedding
    embedding = np.random.randn(512)

    # generate a random confidence score
    confidence = np.random.rand()

    # create a dictionary to store the results
    results = {'title': name,
               'coordinates': [int(x1), int(y1), int(x2), int(y2)],
               'embedding': embedding.tolist(),
               'confidence': confidence}

    return results


if __name__ == "__main__":
    import json
    data = generate_dummy_data()

    print(json.dumps(data))

