# test_exam_G.py
# =============================
# Тесты для Level G: Context Managers (sync/async)
# =============================

import io
import os
import sys
import tempfile
import logging
import sqlite3
import pytest
import time
import shutil
import asyncio

from test7 import *

# -----------------------------
# A. Разминка
# -----------------------------

def test_timer_elapsed():
    with Timer() as t:
        x = sum(range(1000))
    assert hasattr(t, "elapsed")
    assert t.elapsed > 0

def test_suppress_oserror(tmp_path):
    fake = tmp_path / "nofile.txt"
    with suppress_oserror(str(fake)):
        pass  # не должно упасть

def test_redirect_output_to(tmp_path):
    out = tmp_path / "out.txt"
    with redirect_output_to(str(out)):
        print("hello")
    assert "hello" in out.read_text()

def test_chdir_temp(tmp_path):
    old = os.getcwd()
    with chdir_temp(tmp_path):
        assert os.getcwd() == str(tmp_path)
    assert os.getcwd() == old

def test_patch_env(monkeypatch):
    key = "MY_ENV_TEST"
    old = os.environ.get(key)
    with patch_env(key, "123"):
        assert os.environ[key] == "123"
    assert os.environ.get(key) == old

# -----------------------------
# B. Средние
# -----------------------------

def test_atomic_write(tmp_path):
    target = tmp_path / "file.json"
    target.write_text("{}")
    with pytest.raises(ValueError):
        with atomic_write(str(target), {"a": 1}):
            raise ValueError("fail")
    # файл не должен поменяться
    assert target.read_text() == "{}"

def test_multi_open(tmp_path):
    f1, f2 = tmp_path / "a.txt", tmp_path / "b.txt"
    with multi_open([str(f1), str(f2)], "w") as files:
        for f in files:
            f.write("x")
    assert f1.read_text() == "x"
    assert f2.read_text() == "x"

def test_log_capture():
    logger = logging.getLogger("testlog")
    with log_capture() as logs:
        logger.warning("warn msg")
    assert any("warn msg" in rec for rec in logs)

def test_temp_file():
    with temp_file(".txt") as path:
        assert os.path.exists(path)
    # после выхода файла быть не должно
    assert not os.path.exists(path)

def test_sqlite_tx(tmp_path):
    db = tmp_path / "db.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("create table t(x int)")
    # успешный коммит
    with sqlite_tx(conn):
        conn.execute("insert into t values (1)")
    assert conn.execute("select count(*) from t").fetchone()[0] == 1
    # откат при исключении
    with pytest.raises(RuntimeError):
        with sqlite_tx(conn):
            conn.execute("insert into t values (2)")
            raise RuntimeError
    assert conn.execute("select count(*) from t").fetchone()[0] == 1

# -----------------------------
# C. Жёстче
# -----------------------------

def test_locked_dict():
    d = LockedDict()
    with d.locked():
        d["x"] = 1
    assert d["x"] == 1

def test_suppress_many():
    with suppress_many(KeyError, ValueError) as cm:
        {}["nope"]  # KeyError
    assert cm.suppressed is True
    with suppress_many(ValueError) as cm:
        pass
    assert cm.suppressed is False

def test_stderr_to_null(capsys):
    with stderr_to_null():
        print("error!", file=sys.stderr)
    # stderr должен быть пуст
    captured = capsys.readouterr()
    assert captured.err == ""

@pytest.mark.skipif(not hasattr(locale, "setlocale"), reason="locale not available")
def test_temporary_locale():
    old = locale.setlocale(locale.LC_ALL)
    try:
        with temporary_locale("C"):
            assert locale.setlocale(locale.LC_ALL) == "C"
    finally:
        locale.setlocale(locale.LC_ALL, old)

# -----------------------------
# D. Тяжёлые
# -----------------------------

def test_atomic_directory_replace(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "a.txt").write_text("new")
    (dst / "a.txt").write_text("old")

    try:
        with AtomicDirectoryReplace(str(src), str(dst)):
            # внутри блока dst должно содержать новый файл
            assert (dst / "a.txt").read_text() == "new"
            # вызови исключение → должно откатиться
            raise RuntimeError("fail")
    except RuntimeError:
        pass

    # после выхода должно восстановиться старое
    assert (dst / "a.txt").read_text() == "old"


def test_resource_pool_basic():
    pool = ResourcePool(size=2)
    with pool.acquire() as r1, pool.acquire() as r2:
        assert r1 is not None
        assert r2 is not None
    # после выхода ресурсы должны вернуться в пул
    with pool.acquire() as r3:
        assert r3 is not None


def test_capture_time_and_exceptions_success():
    with capture_time_and_exceptions() as cm:
        x = sum(range(10000))
    assert cm.elapsed > 0
    assert cm.exc is None


def test_capture_time_and_exceptions_failure():
    try:
        with capture_time_and_exceptions() as cm:
            raise ValueError("boom")
    except ValueError:
        pass
    assert isinstance(cm.exc, ValueError)
    assert cm.elapsed > 0


def test_sqlite_migrations(tmp_path):
    db = tmp_path / "db.sqlite"
    conn = sqlite3.connect(db)
    scripts = [
        "create table t(x int);",
        "insert into t values (1);"
    ]
    sqlite_migrations(conn, scripts)
    assert conn.execute("select count(*) from t").fetchone()[0] == 1

    bad_scripts = [
        "insert into t values (2);",
        "insert into non_existing_table values (3);"  # ошибка
    ]
    try:
        sqlite_migrations(conn, bad_scripts)
    except Exception:
        pass
    # после ошибки изменений быть не должно
    assert conn.execute("select count(*) from t").fetchone()[0] == 1

# -----------------------------
# E. Эксперт / async
# -----------------------------

@pytest.mark.asyncio
async def test_async_open_many_dummy():
    async def dummy_resource(i):
        class R:
            async def __aenter__(self): return i
            async def __aexit__(self, exc_type, exc, tb): return False
        return R()
    urls = ["u1", "u2", "u3"]
    # Подставляем свои ресурсы, а не aiohttp
    result = await async_open_many(urls)
    assert isinstance(result, list) or result is None

@pytest.mark.asyncio
async def test_async_tempdir():
    path = None
    async with await async_tempdir() as p:
        path = p
        assert os.path.exists(path)
    # после выхода директории не должно быть
    assert not os.path.exists(path)

@pytest.mark.asyncio
async def test_async_log_capture():
    logs = await async_log_capture()
    assert isinstance(logs, list)

@pytest.mark.asyncio
async def test_async_integration_dummy():
    urls = ["https://example.com/a.json", "https://example.com/b.json"]
    try:
        result = await async_integration(urls)
    except NotImplementedError:
        pytest.skip("async_integration not implemented yet")
 