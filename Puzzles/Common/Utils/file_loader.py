import os

def load_puzzles(path):
    txt_files = []
    for root, dirs, files in os.walk(path):
        txt_files.extend([f for f in files if f.endswith('.txt')])
    return txt_files