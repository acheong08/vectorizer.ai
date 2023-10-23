from sys import argv
from vectorizer import Vectorizer, Img

if __name__ == '__main__':
    if len(argv) != 2:
        print("Usage: python -m vectorizer <filename>")
        exit(1)
    img_data = open(argv[1], 'rb').read()
    if img_data is None:
        raise Exception("Could not read file")
    img = Img.from_data(argv[1], img_data)
    vec = Vectorizer(img)
    print(vec.download_url)
    svg = vec.download()
    open('test.svg', 'wb').write(svg)
