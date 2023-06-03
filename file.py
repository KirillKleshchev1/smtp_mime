import base64
from pathlib import Path


class File:
    def __init__(self, path: Path):
        self.path = path
        self.file_ext = path.suffix[1:]
        self.encoded_name = base64.b64encode(path.name.encode('utf-8')).decode('utf-8')

    def get_encoded_file(self):
        with open(self.path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
