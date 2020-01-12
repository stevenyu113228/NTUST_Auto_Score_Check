import pickle
import numpy as np
from PIL import Image


def main(img):

    # load data
    with open('data.data', 'rb') as fp:
        data = pickle.load(fp)
    with open('label.data', 'rb') as fp:
        label = pickle.load(fp)

    # convert RGB to BW
    img = img.convert('1')

    # crop every text from image
    number = [None] * 3
    number[0] = img.crop((13, 0, 27, 40))
    number[1] = img.crop((31, 0, 45, 40))
    number[2] = img.crop((49, 0, 63, 40))

    alphabet = [None] * 3
    alphabet[0] = img.crop((66, 0, 84, 40))
    alphabet[1] = img.crop((90, 0, 101, 40))
    alphabet[2] = img.crop((105, 0, 120, 40))

    # convert by mse
    text = ""
    for i in number:
        mse = [((i - x) ** 2).mean() for x in data[0]]
        text += label[0][mse.index(min(mse))]

    for i in enumerate(alphabet, start=1):
        mse = [((i[1] - x) ** 2).mean() for x in data[i[0]]]
        text += label[1][mse.index(min(mse))]

    return text


if __name__ == '__main__':
    from datetime import datetime
    img = Image.open("VCode.png")
    start = datetime.now()
    text = main(img)

    #print(text, datetime.now()-start)
    # img.show()
