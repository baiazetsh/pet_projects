# test_exam_F.py
# =============================
# Тесты для Level F: Итераторы / Генераторы
# =============================

import pytest
from test6 import *

# -----------------------------
# A. Разминка
# -----------------------------

def test_countdown():
    assert list(CountDown(3)) == [3,2,1]
    assert list(CountDown(1)) == [1]

def test_pairwise():
    assert list(pairwise("abcd")) == [("a","b"),("b","c"),("c","d")]
    assert list(pairwise([1])) == []

def test_flatten1():
    xs = [[1,2],[3],[4,5]]
    assert list(flatten1(xs)) == [1,2,3,4,5]
    assert list(flatten1([])) == []

# -----------------------------
# B. Средние
# -----------------------------

def test_window():
    assert list(window("abcd", 2)) == [("a","b"),("b","c"),("c","d")]
    assert list(window([1,2,3,4], 3)) == [(1,2,3),(2,3,4)]

def test_take_drop():
    xs = range(10)
    assert list(take(3, xs)) == [0,1,2]
    assert list(drop(7, range(10))) == [7,8,9]

def test_peekable():
    it = Peekable([1,2,3])
    assert it.peek() == 1
    assert next(it) == 1
    assert it.peek() == 2
    assert list(it) == [2,3]

# -----------------------------
# C. Жёстче
# -----------------------------

def test_merge_sorted():
    a = [1,3,5]
    b = [2,4,6]
    assert list(merge_sorted(a,b)) == [1,2,3,4,5,6]

def test_unique_everseen():
    xs = [1,2,1,3,2,4]
    assert list(unique_everseen(xs)) == [1,2,3,4]
    assert list(unique_everseen(["a","A","b"], key=str.lower)) == ["a","b"]

def test_tee_safe():
    xs = [1,2,3]
    it1, it2 = tee_safe(xs, 2)
    assert list(it1) == [1,2,3]
    assert list(it2) == [1,2,3]

# -----------------------------
# D. Эксперт
# -----------------------------

def test_chunks():
    data = [b"foo\n", b"bar\n\n", b"baz\n\n"]
    result = list(chunks(data, sep=b"\n\n"))
    assert b"foo\nbar" in result[0]
    assert b"baz" in result[1]

def test_rate_limit():
    import time
    start = time.time()
    list(rate_limit(range(3), per_sec=5))
    elapsed = time.time() - start
    # ~3 элементов, при per_sec=5 → >=0.4 сек суммарно
    assert elapsed >= 0.4

def test_retry():
    counter = {"n":0}
    def gen():
        counter["n"] += 1
        if counter["n"] < 2:
            raise ValueError("fail once")
        yield 42
    out = list(retry(gen, tries=3, backoff=0.01))
    assert out == [42]
