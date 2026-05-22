import os
import re


class Models:
    def __init__(self):
        self.models: list = []
        self.path: str = 'app/src'

    def get_models(self) -> list:
        self.det_folder(path=self.path)
        return self.models

    def det_folder(self, path) -> None:
        for i in os.listdir(path):
            if re.search(r'model.py', f'{path}/{i}'):
                self.models.append(
                    f'{path}/{i}'.replace('/', '.').replace('.py', '')
                )
            if os.path.isdir(f'{path}/{i}'):
                self.det_folder(f'{path}/{i}')
