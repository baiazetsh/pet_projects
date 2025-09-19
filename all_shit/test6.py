# exam_F.py
# =============================
# Python Roadmap v2.0 — Level F: Итераторы / Генераторы
# =============================

from collections import deque
from typing import Iterable, Iterator, Generator, TypeVar, Optional, Any, Callable
import heapq
import time

T = TypeVar("T")

# -----------------------------
# A. Разминка
# -----------------------------

# Q1. CountDown
class CountDown:
    def __init__(self, n: int):
        self.n = n
    def __iter__(self) -> "CountDown":
        return self 
    def __next__(self) -> int:
        if self.n > 0:
            current = self.n
            self.n -= 1
            return current
        else:       
            raise StopIteration
for x in CountDown(5):
    print(x, end=" ")

# Q2. pairwise(xs)
def pairwise(xs: Iterable[T]) -> Iterator[tuple[T,T]]:
    # >>> list(pairwise("abcd")) → [("a","b"),("b","c"),("c","d")]
    it1, it2 = iter(xs), iter(xs)
    next(it2, None)
    return zip(it1, it2)
    
print(list(pairwise("abcde")))

# Q3. flatten1(iterable_of_iterables)
def flatten1(it: Iterable[Iterable[T]]) -> Iterator[T]:
    # Ровно 1 уровень — не рекурсивный!
    #res = []
    res = [sub for i in it for sub in i]
    return res
print(flatten1([[1,[2,3]],[4]]))
        
# -----------------------------
# B. Средние
# -----------------------------

# Q4. window(xs, k)
def window(xs: Iterable[T], k: int) -> Iterator[tuple[T,...]]:
    # Ленивые окна длиной k.
    # >>> list(window("abcd", 2)) → [("a","b"),("b","c"),("c","d")]
    buffer = deque(maxlen=k)
    for x in xs:
        buffer.append(x)
        if len(buffer) == k:
            yield tuple(buffer)
    
print(list(window("abcd", 2)))
print(list(window("abcd", 3)))

# Q5. take / drop
def take(n: int, it: Iterable[T]) -> Iterator[T]:
    count = 0
    for x in it:
        if count <n:
            yield x
            count += 1
        else:
            break

def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    it = iter(it)
    for _ in range(n):
        next(it, None) #skip
    for x in it:
        yield  x

print(list(take(3, 'abcdef')))
print(list(drop(3, 'abcdef')))

# Q6. peekable(it)
class Peekable:
    def __init__(self, it: Iterable[T]):
        self._it = iter(it)
        self._buf: deque[T] = deque()
    def peek(self) -> Optional[T]:
        if  not self._buf:
            try:
                self._buf.append(next(self._it))
            except StopIteration:
                return None
        return self._buf[0]
    def __next__(self) -> T:
        # Вернуть элемент, учитывая буфер.
        if self._buf:               
            return self._buf.popleft()
        return next(self._it)
    def __iter__(self) -> "Peekable":
        return self
num = Peekable(["abcde"])
print(num.peek())
print(next(num))
# -----------------------------
# C. Жёстче
# -----------------------------

# Q7. merge_sorted(*iters)
from heapq import heappush, heappop
def merge_sorted(*iters: Iterable[T]) -> Iterator[T]:
    # Слияние K отсортированных потоков (heapq.merge запрещён).
    iterators = [iter(it) for it in iters] 
    heap = []
    
    #init
    for idx, it in enumerate(iterators):
        try:
            first = next(it)
            heappush(heap, (first, idx))
        except StopIteration:
            pass
    # main cycle
    while heap:
        val, idx = heappop(heap)
        yield val
        try:
            nxt = next(iterators[idx])
            heappush(heap, (nxt, idx))
        except StopIteration: 
            pass
a = [1,4,7]
b = [2,5,8]
c = [3,6,9]
print(list(merge_sorted(a,b,c)))

# Q8. unique_everseen
def unique_everseen(it: Iterable[T], key: Optional[Callable[[T], Any]] = None) -> Iterator[T]:
    # Лениво, без set для бесконечных.
    seen =set()
    for element in it:
        k = key(element) if key else element
        if k not in seen:
            seen.add(k)
            yield element        
print(list(unique_everseen("AAAABBBCCCDDDEEEFFF")))
print(list(unique_everseen(["a","A","b"], key=str.lower)))
print("======================8===================")
# Q9. tee_safe(it, n=2)
def tee_safe(it: Iterable[T], n: int = 2) -> tuple[Iterator[T], ...]:
    # Свои «разветвители», с буферизацией.
    it = iter(it)
    deques = [deque() for _ in range(n)]
    print(deques)
    def gen(mydeque: deque):
       
        while True:
            if not mydeque:               #if buffer is empty
                try:
                    val = next(it)        # pulling from source
                except StopIteration:
                    return
                for d in deques:          # push into all buffers
                    
                    d.append(val)
                   
            yield mydeque.popleft()        # taking from own buffer
    return tuple(gen(d) for d in deques)             
a, b = tee_safe([1,2,3,4,5], 2)
print(next(a))   # '1'
print(next(a))   # '2'
print(next(b))   # '1'  (второй итератор догнал, данные сохранились)
print(list(a))   # [3, 4, 5]
print(list(b))   # [2, 3, 4, 5]

# -----------------------------
# D. Эксперт
# -----------------------------

# Q10. chunks(stream, sep: bytes = b"\n\n")
def chunks(stream: Iterable[bytes], sep: bytes = b"\n\n") -> Iterator[bytes]:
    # Генератор блоков из байтового потока.
    # Подъёбка: нельзя читать весь файл целиком.
    buffer = b""
    for chunk in stream:
        buffer += chunk

        while True:
            idx = buffer.find(sep)        
            if idx == -1:
                break
            yield buffer[:idx]
            buffer = buffer[idx + len(sep):]
    if buffer:
        yield buffer
data = [b"Hello\n", b"World\n\nThis ", b"is test\n\nEnd"]
for block in chunks(data):
    print("BLOCK:", block)  


# Q11. rate_limit(it, per_sec: float)
import time
def rate_limit(it: Iterable[T], per_sec: float) -> Iterator[T]:
    # Ограничитель скорости (sync/async).
    # >>> list(rate_limit(range(3), 2)) # ~1.5 сек суммарно
    delay = 1.0 / per_sec
    for x in it:
        yield x
        time.sleep(delay)
start = time.time()
print(list(rate_limit(range(3), 2)))
print("Elapsed:", round(time.time()-start, 2))

# Q12. retry(gen_func, tries, backoff)
def retry(gen_func: Callable[[], Iterator[T]], tries: int, backoff: float) -> Iterator[T]:
    # Обёртка-генератор, возобновляет поток после исключений.
    # >>> retry(failing_gen, tries=3, backoff=0.1)
    attempt = 0
    while attempt < tries:
        gen = gen_func()
        try:
            for x in gen:
                yield x
            return 
        except Exception as e:
            attempt += 1
            if attempt >= tries:
                raise
        time.sleep(backoff)
def failing_gen():
    yield 1
    yield 2
    yield ValueError("oops!")
    yield 3
print(list(retry(failing_gen, tries=3, backoff=0.5)))