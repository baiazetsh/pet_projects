# exam_G.py
# =============================
# Python Roadmap v2.0 — Level G: Context Managers (sync/async)
# =============================
import snoop
import os
import sys
import json
import tempfile
import shutil
import sqlite3
import logging
import threading
import locale
import asyncio
from typing import Optional, Iterator, Generator, Any, List
from contextlib import contextmanager, ExitStack, AsyncExitStack, redirect_stdout
import time


# -----------------------------
# A. Разминка
# -----------------------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
clear()    
class Timer:
    """
    Контекст-менеджер Timer:
    - Засекает время в __enter__.
    - В __exit__ сохраняет elapsed (float).
    - Не подавляет исключения.
    Тест: внутри блока время должно быть > 0.
    """
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self
    def __exit__(self, exc_type, exc, tb) -> None:
        print(f"time elapsed: {time.perf_counter() - self.start:.2f}s")
        return False
        
with Timer() as t:
    time.sleep(0.8)

@contextmanager
def suppress_oserror(path: str) -> Generator[None, None, None]:
    """
    Контекст: пытается удалить файл path в __exit__.
    Если файла нет — FileNotFoundError игнорируется.
    Любые другие ошибки не подавляются.
    """
    try:
        yield # внутри блока ничего не делаем
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass  # игнорируем только "файла нет"
with suppress_oserror("temp.txt"):
    with open("temp.txt", "w") as f:
        f.write("test")
       # ← после выхода из блока "temp.txt" будет удалён 
@contextmanager       
def redirect_output_to(path: str) -> Generator[None, None, None]:
    """
    Контекст: перенаправляет stdout в файл.
    Используй contextlib.redirect_stdout, но заверни в свою оболочку.
    """
    with open(path, "w") as f, redirect_stdout(f):
        yield
        
with redirect_output_to("text.txt"):
    print("Hello, world")
    print(" It's gonna to fil, no to  consol")
print(("Again, to consol"))    

@contextmanager
def chdir_temp(path: str) -> Generator[None, None, None]:
    """
    Временно меняет текущую директорию (os.getcwd()).
    В __exit__ всегда возвращает назад.
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_cwd)
             
with chdir_temp(tempfile.gettempdir()):
    print("Текущая директория:", os.getcwd())
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Привет из временной папки!")    

@contextmanager
def patch_env(key: str, value: str) -> Generator[None, None, None]:
    """
    Временно меняет переменную окружения.
    После блока значение должно вернуться к исходному.
    Если её не было — удалить.
    """
    old_value = os.environ.get(key)
    try:
        os.environ[key] = value
        yield
    finally:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value
print("cwd to", os.getcwd())            
with chdir_temp(tempfile.gettempdir()):
    print('cwd inside:', os.getcwd())
print('cwd after', os.getcwd())    

# -----------------------------
# B. Средние
# -----------------------------

s1 = "qqqwwweeerrrkkk"
s2 = 'qqqwwweeeuckkk'
print(
    [(i, a, b) for i,(a,b) in enumerate(zip(s1,s2)) if a!= b]
)
print("----------------------------------")
@snoop
@contextmanager
def atomic_write(path: str) -> Generator[any, None, None]:
    """
    Атомарная запись в файл, совместимая с Windows:
    - создаёт временный файл через NamedTemporaryFile(delete=False);
    - пишет туда данные;
    - закрывает файл;
    - заменяет оригинал только если блок прошёл без ошибок.
    """
    dir_name = os.path.dirname(path) or "."
    tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name)  # создаём пустой файл
    os.close(tmp_fd)  # сразу закрываем дескриптор, чтобы Windows не держала лок

    try:
        with open(tmp_path, "w", encoding="utf-8") as tmp_file:
            yield tmp_file  # наружу отдаём файловый объект
        os.replace(tmp_path, path)  # безопасная замена
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

data = {"name": "Alice", "age": 30}

with atomic_write("data1.json") as f:
    json.dump(data, f)

print(open("data1.json").read())
print("----------------------------------")
@snoop
@contextmanager
def multi_open(paths: list[str], mode: str = "w") ->  Generator[list, None, None]:
    """
    Открывает несколько файлов сразу.
    Возвращает список файловых объектов.
    Все гарантированно закрываются в __exit__.
    Для N неизвестно заранее → используй ExitStack.
    """
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(path, mode, encoding="utf-8")) for path in paths
        ]
        yield files
        
with multi_open(["a.txt", "b.txt"], "w") as (f1, f2):
    f1.write("Hello\n")
    f2.write("World\n")
print(open("a.txt").read())
print(open("b.txt").read())

@snoop
@contextmanager
def log_capture(level: int = logging.INFO)-> Generator[List[str], None, None]:
    """
    Добавляет временный logging.Handler, который пишет в список строк.
    Возвращает этот список.
    После выхода — handler удаляется.
    """
    records: List[str] = []
    class ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            msg = self.format(record)
            records.append(msg)
    handler = ListHandler()            
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    try:
        yield records
    finally:
        logger.removeHandler(handler)
    
logging.basicConfig(level=logging.DEBUG)    
with log_capture(logging.INFO) as logs:
    logging.debug("Debug msg")
    logging.info("Info msg")
    logging.warning("Warning msg")
print(logs)    

@contextmanager
def temp_file(suffix: str = ".txt") -> Generator[str, None, None]:
    """
    Создаёт временный файл.
    Возвращает его путь.
    После выхода файл удаляется в любом случае.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd) #we immediately close the descriptor so that the file is not locked
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)
            
with temp_file(".log") as tmp:
    print("Temporary pathy:", tmp)
    with open(tmp, "w") as f:
        f.write("hello world")
print("Does the file exist  after exiting?", os.path.exists(tmp))            

@contextmanager
def sqlite_tx(conn: sqlite3.Connection):
    """
    Транзакция SQLite:
    - commit при успешном выходе.
    - rollback при исключении.
    Проверка: внутри блока INSERT виден, при исключении не сохраняется.
    """
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

# Успешная транзакция
with sqlite_tx(conn) as tx:
    tx.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))

print(list(conn.execute("SELECT * FROM users")))
# [(1, 'Alice')]

# Транзакция с ошибкой
try:
    with sqlite_tx(conn) as tx:
        tx.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
        raise ValueError("ошибка внутри транзакции")
except ValueError:
    pass

print(list(conn.execute("SELECT * FROM users")))
# всё ещё [(1, 'Alice')], "Bob" не сохранился


# -----------------------------
# C. Жёстче
# -----------------------------

class FileTransaction:
    """
    Мини-VCS для файлов.
    - __enter__: сохранить копии всех файлов в root.
    - Внутри блока можно создавать/изменять.
    - __exit__: при исключении вернуть всё назад, при успехе сохранить.
    """
    def __init__(self, root: str):
        self.root = root
    def __enter__(self) -> "FileTransaction":
        raise NotImplementedError
    def __exit__(self, exc_type, exc, tb) -> None:
        raise NotImplementedError

class LockedDict(dict):
    """
    Dict с блокировкой.
    Использование:
        with d.locked():
            d["x"] = 1
    Должен работать через threading.Lock.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()
    @contextmanager
    def locked(self):
        raise NotImplementedError

@contextmanager
def temporary_locale(name: str):
    """
    Временно ставит locale.setlocale(locale.LC_ALL, name).
    После блока возвращает исходное значение.
    Если локаль недоступна — пропусти тест (locale.Error).
    """
    raise NotImplementedError

@contextmanager
def stderr_to_null():
    """
    Временно перенаправляет sys.stderr в os.devnull.
    После выхода возвращает как было.
    """
    raise NotImplementedError

@contextmanager
def suppress_many(*exc_types: type[BaseException]):
    """
    Аналог contextlib.suppress, но принимает несколько исключений.
    Должен возвращать объект с атрибутом .suppressed (True/False),
    чтобы проверить, было ли подавление.
    """
    raise NotImplementedError

# -----------------------------
# D. Тяжёлые
# -----------------------------

@contextmanager
def AtomicDirectoryReplace(src_dir: str, dst_dir: str):
    """
    Атомарно заменить директорию dst_dir содержимым src_dir.
    Реализовать через os.replace.
    Если внутри блока исключение — вернуть всё назад.
    """
    raise NotImplementedError

def exitstack_pipeline(urls: list[str], max_workers: int = 4):
    """
    Скачай список URL параллельно (thread pool).
    Запись каждого файла делай через atomic_write.
    Собери индекс {url: path}.
    Используй ExitStack для управления ресурсами.
    """
    raise NotImplementedError

class ResourcePool:
    """
    Пул ресурсов (например соединений).
    with pool.acquire() as res: выдать ресурс либо ждать.
    При выходе ресурс возвращается в пул.
    """
    def __init__(self, size: int):
        raise NotImplementedError
    @contextmanager
    def acquire(self):
        raise NotImplementedError

@contextmanager
def capture_time_and_exceptions():
    """
    Контекст, который сохраняет:
    - elapsed (float)
    - exc (если было исключение)
    Не должен подавлять исключения.
    Возвращает объект с этими полями.
    """
    raise NotImplementedError

def sqlite_migrations(conn: sqlite3.Connection, scripts: list[str]):
    """
    Применить список SQL-скриптов транзакционно.
    Если любой упал — откатить все.
    """
    raise NotImplementedError

# -----------------------------
# E. Эксперт / async
# -----------------------------

async def async_open_many(urls: list[str]):
    """
    AsyncExitStack:
    - открыть несколько async-ресурсов (например aiohttp session.get()).
    - гарантировать закрытие всех даже при падении.
    """
    raise NotImplementedError

@contextmanager
def async_timeout(seconds: float):
    """
    Async timeout.
    - можно использовать asyncio.timeout (Python 3.11+).
    - или реализовать свой: отменять задачу по истечении времени.
    """
    raise NotImplementedError

async def async_tempdir():
    """
    Создать временную директорию.
    Вернуть её путь.
    В __aexit__ удалить.
    """
    raise NotImplementedError

async def async_log_capture():
    """
    Временный async logging.Handler.
    Собирает записи и возвращает список строк.
    """
    raise NotImplementedError

async def async_integration(urls: list[str]):
    """
    Интеграция:
    - асинхронно скачать N JSON-объектов.
    - транзакционно сохранить индекс {url: path} на диск.
    - либо всё, либо ничего.
    """
    raise NotImplementedError
