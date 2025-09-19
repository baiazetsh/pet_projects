# exam_E.py
# =============================
# Python Roadmap v2.0 — Level E (эксперт/олимпиадные)
# =============================

from collections import defaultdict
import math, json
from datetime import datetime
from collections import Counter
from math import dist
from operator import le
from unittest import result




# Q1. Уплотнение матрицы
matrix = [
    [0,0,0,0],
    [0,5,0,0],
    [0,0,0,0],
    [0,0,7,0],
]
# Удалить строки и столбцы, где только нули.
# Вернуть новую матрицу comprehension’ом.
# Подъёбка: не вздумай руками писать if row != [0,0,0,0]; должно быть общее решение.
cleared_row = [row for row in matrix if sum(row) != 0]
cleared_cols = [list(col) for col in zip(*cleared_row) if sum(col) != 0]
result_matrix = [list(row) for row in zip(*cleared_cols)]
print(result_matrix)
 
# Q2. Мини-парсер JSON-лайнов
lines = [
    '{"id":1,"name":"Alice"}',
    '{"id":2,"name":"Bob"}',
    '{"id":"oops","bad":1}',
    '{"id":1,"name":"Alice_dup"}',
    'not a json'
]
# Из lines собрать:
# - только валидные JSON-объекты (dict, с числовым id)
# - индекс {id: obj}, при дубликате id берём последний
# Нельзя писать try/except прямо в comprehension → вынеси is_valid(line).

def is_valid(l):
    try:
        json_l = json.loads(l)
        if isinstance(json_l, dict) and "id" in json_l and isinstance(json_l["id"], int):
            return json_l
    except (json.JSONDecodeError, TypeError):
        return None

valid_obj = [obj for l in lines if(obj := is_valid(l))]

print({obj["id"]: obj for obj in valid_obj})

# Q3. Подстрочные частоты
s = "aba" 
# Построить dict {length: count} для всех подстрок.
# "aba" → подстроки: "a","b","a","ab","ba","aba"
# → {1:3, 2:2, 3:1}
# Подъёбка: аккуратно с O(n^3), для строки в 1000 символов можно упасть.
freq = {}
n = len(s)
for k in range(1, n+1):    
    count = n - k + 1    
    freq[k]= count
print(freq)
print(
    {k: n-k+1 for k in range(1, n+1)}
)
# Q4. Мягкая нормализация дат
dates_raw = ["2024-05-06","06/05/2024","05-06-2024","20240506","wrong"]
# Вернуть dict {raw: norm_or_None} где norm = YYYY-MM-DD.
# Допусти 3–4 формата (iso, d/m/Y, m-d-Y, yyyymmdd).
# Вынеси parse_date функцию, comprehension — только сборка результата.
def parse_date(raw: str):
    formats = "%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%Y%m%d"
    for f in formats:
        try:
            dt = datetime.strptime(raw, f)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None
print(
    {d: parse_date(d) for d in dates_raw}
)    

# Q5. Биннинг чисел
nums = [1,2,3,7,15,22,25,26,33,40,41]
w = 10
# Построить dict {bin_start: count} для равных бинов ширины w.
# Для w=10 → {0:4, 10:1, 20:3, 30:2, 40:1}
# Подъёбка: не делай if-elif; формула bin_start = (x//w)*w.
bins = defaultdict(int)
for x in nums:
    bin_start = (x//w) * w    
    bins[bin_start] += 1
bins = dict(bins)    
print(bins)
print(
    {k: v for k,v in Counter((x//w)* w for x in nums).items()}
)
print(
    {b: sum(1 for x in nums if (x//w) * w == b) for b in {(x//w)* w for x in nums}}
)
# Q6. Разрежённая матрица
triplets = [(0,1,5),(2,3,7),(2,1,9)]
# Свести в dict {i: {j: val}}
# {0:{1:5}, 2:{3:7,1:9}}
matrix = defaultdict(dict)
for i, j, val in triplets:
    matrix[i][j] = val
print(dict(matrix))
print(
    {i: {j: val for _, j, val in triplets if _ == i} for i, _,_ in triplets}
)
# Q7. All-pairs distances
points1 = [(0,0),(3,4),(6,8),(0,5)]
# Построить список [((i,j), dist), ...] для всех i<j.
# dist — евклид. Отсортировать по dist.
# Подъёбка: не делай полный квадрат с i==j и дубликаты (j<i).
from math import dist  # можно sqrt, но dist удобнее

dists = [
    ((i, j), dist(points1[i], points1[j]))
    for i in range(len(points1))
    for j in range(i+1, len(points1))
]
dists_sorted = sorted(dists, key=lambda x: x[1])
print(dists_sorted)

# Q8. Топ-K по группам
data = [
    ("A",10),("A",5),("A",7),
    ("B",20),("B",15),
    ("C",3),("C",9),("C",12),
]
K = 2
# Сжать в dict {group: topK_values_desc}.
# "A":[10,7], "B":[20,15], "C":[12,9]
grouped = defaultdict(list)
for key, value in data:
    grouped[key].append(value)   
print(
    {k: sorted(val, reverse=True)[:K] for k, val in grouped.items()}
)
# Q9. Мульти-инверсия
d = {
    "x":["a","b"],
    "y":["b","c"],
    "z":["a"],
}
# → {"a":{"x","z"},"b":{"x","y"},"c":{"y"}}
res = defaultdict(set)
for k, vals in d.items():
    for v in vals:
        res[v].add(k)
print(dict(res))
print(
   {v: {k for k, vals in d.items() if v in vals} for vals in d.values() for v in vals}
)
# Q10. Плотность словаря
d2 = {
    "u":[1,2,3,4,5],
    "v":[10],
    "w":[7,8,9],
    "z":[100,200,300,400],
}
# Собрать {k: mean_of_top3} для ключей, где длина списка ≥3.
# { "u": (5+4+3)/3, "w": (9+8+7)/3, "z": (400+300+200)/3 }
result = {}
for key, vals in d2.items():
    if len(vals) >= 3:
        d = sum(sorted(vals, reverse=True)[:3]) / 3
        result[key] = d
print(result)
print(
    {k: sum(sorted(vals, reverse=True)[:3]) / 3 for k, vals in d2.items() if len(vals) >= 3}
)    +