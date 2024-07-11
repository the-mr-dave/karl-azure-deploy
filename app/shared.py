# shared.py
import multiprocessing

# Globale Variable für das geteilte Dictionary
tasks = None


def init_global_variable():
    global tasks
    manager = multiprocessing.Manager()
    tasks = manager.dict()
