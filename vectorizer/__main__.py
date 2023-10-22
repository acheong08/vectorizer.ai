from sys import argv
from vectorizer import Vectorizer, Img

if __name__ == '__main__':
    if len(argv) != 2:
        print("Usage: python -m vectorizer <filename>")
        exit(1)
    vec = Vectorizer(Img(argv[1]))
    print(vec.download_url)
    svg = vec.download()
    open('test.svg', 'wb').write(svg)
