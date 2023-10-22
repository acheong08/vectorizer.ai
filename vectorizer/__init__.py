import json
from websockets.sync.client import connect, ClientConnection
from PIL import Image
import requests

DEFAULT_DOWNLOAD_OPTIONS = """file_format=svg&svg.version=svg_1_1&dxf.compatibility_level=lines_and_arcs&draw_style=fill_shapes&shape_stacking=cutouts&group_by=none&curves.allowed.quadratic_bezier=true&curves.allowed.quadratic_bezier=false&curves.allowed.cubic_bezier=true&curves.allowed.cubic_bezier=false&curves.allowed.circular_arc=true&curves.allowed.circular_arc=false&curves.allowed.elliptical_arc=true&curves.allowed.elliptical_arc=false&curves.line_fit_tolerance=0.1&gap_filler.enabled=true&gap_filler.enabled=false&gap_filler.non_scaling_stroke=true&gap_filler.non_scaling_stroke=false&gap_filler.stroke_width=2.0&strokes.non_scaling_stroke=true&strokes.non_scaling_stroke=false&strokes.override_color=%23000000&strokes.stroke_width=1.0&pdf.version=PDF_1_4&eps.version=PS_3_0_EPSF_3_0"""


class Img:
    size: int
    width: int
    height: int
    filename: str
    data: bytes

    def __init__(self, filename: str):
        self.filename = filename
        self.data = open(filename, 'rb').read()
        self.size = len(self.data)
        self.width, self.height = Image.open(filename).size


class Vectorizer:
    wss_url: str = 'wss://vectorizer.ai/internal/websocket'
    download_url: str

    def __init__(self, img: Img):
        self.wss_url += f'?lc=en-US&len={img.size}&w={img.width}'
        self.wss_url += f'&h={img.height}&filename={img.filename}'

        with connect(self.wss_url) as websocket:
            websocket: ClientConnection = websocket
            websocket.send(json.dumps({
                "index": 0, "command": 0
            }))
            websocket.send(json.dumps({
                "index": 0, "command": 0
            }))
            websocket.send(json.dumps({
                "index": 0,
                "command": 2,
                "body": {
                           "jobId": 1,
                           "meta": {
                               "width": img.width, "height": img.height,
                               "dpi": 72, "isCmyk": False
                           }
                           }
            }))
            print("Debug: Sent metadata")

            # Slit the image into parts of 14.85KB
            for i in range(0, img.size, 14850):
                print("Debug: Sending image part", i)
                # Ensure the last part is not out of range
                end = min(i + 14850, img.size)
                websocket.send(img.data[i:end])

            websocket.send(json.dumps({"index": 0, "command": 11, "body": {}}))

            # Wait for the response

            while True:
                data = websocket.recv()
                try:
                    data = json.loads(data)
                    if data.get('command') == 7:
                        # We should get the URL of the original image
                        self.download_url = data.get('body', {}).get(
                            'spec', {}).get('originalUrl', '').replace(
                            '/original', '/download')
                        print(self.download_url)
                    elif data.get('command') == 9:
                        print("Reached end")
                        return
                except Exception:
                    continue

    def download(self, options: str = DEFAULT_DOWNLOAD_OPTIONS):
        print("Debug: Downloading file")
        form_data = options
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Referer': self.download_url.replace('/download', '')
        }
        resp = requests.post(
            'https://vectorizer.ai' +
            self.download_url, data=form_data, headers=headers)
        if resp.status_code != 200:
            raise Exception("Error downloading file")
        print("Debug: Download success")
        return resp.content
