import os
import numpy as np
from collections import defaultdict
from typing import List
from pdfreader import SimplePDFViewer
from docx import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog

CHUNK_SIZE = 10000

class TrieNode:
    def __init__(self, char: str = ''):
        self.char = char
        self.count = 0
        self.children = {}

    def insert(self, text: str):
        if not text:
            return

        node = self
        for char in text:
            if char not in node.children:
                node.children[char] = TrieNode(char)

            node = node.children[char]
            node.count += 1

    def get_freq_arr(self) -> np.ndarray:
        freq_arr = np.zeros(256)
        self._dfs(self, freq_arr, 0)
        total_count = np.sum(freq_arr)
        freq_arr /= total_count
        return freq_arr

    def _dfs(self, node: 'TrieNode', freq_arr: np.ndarray, depth: int):
        for char, child in node.children.items():
            freq_arr[ord(char)] = child.count / depth
            self._dfs(child, freq_arr, depth+1)


def process_chunk(text: str) -> np.ndarray:
    trie = TrieNode()
    trie.insert(text)
    freq_arr = trie.get_freq_arr()

    return freq_arr


def process_file(filepath: str) -> np.ndarray:
    """
    读取文件并返回该文件中每个字符出现的频率

    :param filepath: 文件路径
    :return: 字符频率数组，numpy数组类型
    """
    _, ext = os.path.splitext(filepath)
    if ext == '.pdf':
        return process_pdf(filepath)
    elif ext in ['.doc', '.docx']:
        return process_doc(filepath)
    elif ext == '.txt':
        return process_txt(filepath)
    else:
        raise ValueError('Unsupported file type')



def process_pdf(filepath: str) -> np.ndarray:
    """
    读取PDF文件并返回该文件中每个字符出现的频率

    :param filepath: PDF文件路径
    :return: 字符频率数组，numpy数组类型
    """
    fd = open(filepath, "rb")
    viewer = SimplePDFViewer(fd)
    viewer.render()
    text = viewer.canvas.text_content


    freq_arr = np.zeros(256)
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i+CHUNK_SIZE]
            future = executor.submit(process_chunk, chunk)
            futures.append(future)

        for future in as_completed(futures):
            freq_arr += future.result()

    total_count = np.sum(freq_arr)
    freq_arr /= total_count
    return freq_arr


def process_doc(filepath: str) -> np.ndarray:
    """
    读取DOC或DOCX文件并返回该文件中每个字符出现的频率

    :param filepath: DOC或DOCX文件路径
    :return: 字符频率数组，numpy数组类型
    """
    try:
        doc = Document(filepath)
    except Exception as e:
        print(e)
        return np.zeros(256)

    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text

    freq_arr = np.zeros(256)
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i+CHUNK_SIZE]
            future = executor.submit(process_chunk, chunk)
            futures.append(future)

        for future in as_completed(futures):
            freq_arr += future.result()

    total_count = np.sum(freq_arr)
    freq_arr /= total_count
    return freq_arr


def process_txt(filepath: str) -> np.ndarray:
    """
    读取TXT文件并返回该文件中每个字符出现的频率

    :param filepath: TXT文件路径
    :return: 字符频率数组，numpy数组类型
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    freq_arr = np.zeros(256)

    # 将文本分成大小为 CHUNK_SIZE 的块，并使用多线程计算每个块中字符出现的频率
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i+CHUNK_SIZE]
            future = executor.submit(process_chunk, chunk)
            futures.append(future)

        # 将所有块的字符频率相加
        for future in as_completed(futures):
            freq_arr += future.result()

    # 计算字符频率
    total_count = np.sum(freq_arr)
    freq_arr /= total_count

    return freq_arr


def get_common_chars(f1_freq: np.ndarray, f2_freq: np.ndarray) -> List[int]:
    """
    返回两个文件中共同出现的字符列表

    :param f1_freq: 第一个文件的字符频率数组，numpy数组类型
    :param f2_freq: 第二个文件的字符频率数组，numpy数组类型
    :return: 共同出现的字符的ASCII码列表，Python List类型
    """
    common_chars = np.where((f1_freq != 0) & (f2_freq != 0))[0]

    return common_chars.tolist()


def get_distance(f1_freq: np.ndarray, f2_freq: np.ndarray) -> float:
    """
    计算两个文件的距离

    :param f1_freq: 第一个文件的字符频率数组，numpy数组类型
    :param f2_freq: 第二个文件的字符频率数组，numpy数组类型
    :return: 两个文件的距离，Python float类型
    """
    common_chars = get_common_chars(f1_freq, f2_freq)
    diff = f1_freq[common_chars] - f2_freq[common_chars]
    distance = np.sum(diff * diff)
    diff = f1_freq - f2_freq
    distance += np.sum(diff[common_chars] * diff[common_chars])
    return distance

def process_files(filepaths: List[str]) -> np.ndarray:
    """
    对多个文件计算距离矩阵

    :param filepaths: 文件路径列表，Python List类型
    :return: 距离矩阵，numpy数组类型
    """
    n = len(filepaths)
    distances = np.zeros((n, n))

    freqs = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, filepath) for filepath in filepaths]

        for future in as_completed(futures):
            freqs.append(future.result())

    for i in range(n):
        for j in range(i+1, n):
            distances[i][j] = get_distance(freqs[i], freqs[j])
            distances[j][i] = distances[i][j]

    return distances

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("文件相似度分析")
        self.filepaths = []
        self.distances = None
        self.create_widgets()

    def create_widgets(self):
        # 添加文件按钮
        self.add_button = tk.Button(self.master, text="添加文件", command=self.add_file)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)

        # 删除文件按钮
        self.del_button = tk.Button(self.master, text="删除文件", command=self.del_file)
        self.del_button.grid(row=0, column=1, padx=10, pady=10)

        # 计算距离矩阵按钮
        self.calc_button = tk.Button(self.master, text="计算距离矩阵", command=self.calc_distances)
        self.calc_button.grid(row=0, column=2, padx=10, pady=10)

        # 文件列表
        self.file_list = tk.Listbox(self.master, width=50, height=15)
        self.file_list.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # 距离矩阵
        self.dist_matrix = tk.Label(self.master, text="")
        self.dist_matrix.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def add_file(self):
        filepath = filedialog.askopenfilename()
        if filepath and os.path.isfile(filepath):
            self.filepaths.append(filepath)
            self.file_list.insert(tk.END, os.path.basename(filepath))

    def del_file(self):
        selected_items = self.file_list.curselection()
        for i in reversed(selected_items):
            self.file_list.delete(i)
            self.filepaths.pop(i)

    def calc_distances(self):
        if len(self.filepaths) < 2:
            return
        self.distances = process_files(self.filepaths)
        self.dist_matrix.config(text=str(self.distances))

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
