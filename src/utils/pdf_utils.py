# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

from pathlib import Path
import PyPDF2


class PDFParser:
    def __init__(self, path: str):
        self.path: str = path
        self._reader = None

    @property
    def reader(self) -> None:
        if not self._reader:
            self.__validate_path()
            self._reader = PyPDF2.PdfReader(self.path)
        return self._reader

    def __validate_path(self) -> None:
        pf_path = Path(self.path)
        if not (pf_path.is_file() and pf_path.suffix.lower() == ".pdf"):
            raise FileNotFoundError(rf"File not found or not a PDF: {self.path}")

    def extract_text(self) -> str:
        text: str = ""
        for page in self.reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text.strip()
