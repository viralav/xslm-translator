from collections import deque
from googletrans import Translator
import asyncio
from utils.logging_mech import logger
import traceback


# class Cell:
#     def __init__(self, val):
#         self.value = val

# class Row:
#     def __init__(self, data: list):
#         self.data = [Cell(val) for val in data]
#         self.index = 0

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.index < len(self.data):
#             result = self.data[self.index]
#             self.index += 1
#             return result
#         else:
#             raise StopIteration
        
#     def __len__(self):
#         return len(self.data)
class CancellationException(Exception):
    pass

class CancellationToken:
    def __init__(self):
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def is_cancelled(self):
        return self._is_cancelled


class TranslateRow:

    def __init__(self, row):
        self.row = row
        self.row_len = len(self.row)
        self.no_translate_queue = deque()
        self.no_translate_idx = []
        self.pre_translate_queue = deque()
        self.post_translate_queue = deque()
        self.rebuilt_queue = deque()

    @staticmethod
    def no_translate_cell(cell):

        if not isinstance(cell.value, str):
            return True
        
        if not cell.value:
            return True
        
        if cell.value.startswith("="):
            return True
        
        return False

    def prepare_data_to_translate(self):


        for idx, cell in enumerate(self.row):
            if self.no_translate_cell(cell):
                self.no_translate_idx.append(idx)
                self.no_translate_queue.append(cell.value)
            else:
                self.pre_translate_queue.append(cell.value)


    async def translate_row(self, src, dest, cancellation_token):
        async with Translator() as translator:
            if cancellation_token.is_cancelled():
                raise CancellationException
            translations = await translator.translate(list(self.pre_translate_queue), src=src, dest=dest)

            for translation in translations:
                self.post_translate_queue.append(translation.text)


    def post_translation_rebuild(self):

        assert len(self.pre_translate_queue) == len(self.post_translate_queue), "Pre and post translate queue are of different length"

        for idx in range(self.row_len):
            if idx in self.no_translate_idx:
                self.rebuilt_queue.append(self.no_translate_queue.popleft())
            else:
                self.rebuilt_queue.append(self.post_translate_queue.popleft())


    async def perform_translation(self, src, dest, cancellation_token):

        self.prepare_data_to_translate()

        try:
            await self.translate_row(src, dest, cancellation_token)
            self.post_translation_rebuild()
            return list(self.rebuilt_queue)
        except Exception as exc:
            t = traceback.format_exc()
            logger.error(f"Error originates: {t}")
            logger.error(f"Error while translating {exc}")