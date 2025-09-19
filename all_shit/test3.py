# exam_CD.py
# =============================
# Python Roadmap v2.0 — Level C (жёстче) / D (тяжёлые)
# =============================

import string
from datetime import datetime, time


# -----------------------------
# LEVEL C. Comprehension + логика
# -----------------------------

# Q1. Транспонирование матрицы comprehension’ом
matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
# Получить [[1,4],[2,5],[3,6]]
# Подъёбка: если сделаешь через zip — слишком легко, надо comprehension.
print(
    [[row[i] for row in matrix] for i in range(len(matrix[0]))]
)

# Q2. Dict группировки по первой букве
words = ["apple", "banana", "apricot", "blueberry", "cherry", "cranberry"]
# Сначала: {letter: [] for letter in ascii_lowercase}
# Потом циклом наполнить: каждое слово в свой список по первой букве.
from string import ascii_lowercase
alfab = {letter: [] for letter in ascii_lowercase}
for word in words:
    first = word[0]
    alfab[first].append(word)
    print(alfab)
#v2
print(
    {letter: [w for w in words if w.startswith(letter)] for letter in ascii_lowercase}
)    
    
# Q3. Список “окон” длиной k
xs = [1, 2, 3, 4, 5, 6]
k = 3
# windows = [xs[i:i+k] for i in ...] (без выходов за границы)
print(
    [xs[i:i+k] for i in range(len(xs) - k + 1)]
)
print(
    [list(t) for t in zip(*(xs[i:] for i in range(k)))]
)

# Q4. Dict фильтра названий файлов
files = ["report.docx", "a.py", "bigdata.csv", "hi", "image.PNG"]
# Взять названия без расширения, только где длина > 2.
# В нижнем регистре.
print(
    {fn.lower().split('.')[0]:[i] for i,fn in enumerate(files) if len(fn.split('.')[0]) > 2}
)

# Q5. Список уникальных слов из текста в порядке появления
text = "hello world hello python code world python"
# Подсказка: dict.fromkeys
# Подъёбка: set() использовать нельзя — порядок потеряется.
print(
    (list(dict.fromkeys(text.split())))
)

# Q6. Сет всех биграмм букв в словах
word = "hello"
words2 = ["car", "bus", "train", "plane", "rocket", "AI", "data123"]
# "hello" → {"he","el","ll","lo"}
# Применить к списку слов: words2 = ["python","civic","stats"]
print(
    [set(word[i:i+2] for i in range(len(word)-1) for word in words2)  ]
)
print(
    set(
    word[i:i+2]
    for word in words2
    for i in range(len(word) - 1)
)
)
# Q7. Dict {row_id: sum(nums)} по строкам матрицы
matrix2 = [
    [1, 2, 3],
    [10, 20, 30],
    [5, 5, 5],
]
T = 10
# Только строки, где сумма > T
print(
  {i:sum(row) for i, row in enumerate(matrix2) if sum(row)  > T}
)

# Q8. “Расплющить” список списков списков на 2 уровня
nested = [
    [[1, 2], [3, 4]],
    [[5, 6]],
    [[7], [8, 9]]
]
# Получить [1,2,3,4,5,6,7,8,9]
print(
    [x for sublist in nested for inner in sublist for x in inner]
)

# Q9. Из paths собрать dict {dir_name: count_files}
paths = [
    "/home/user/docs/report.docx",
    "/home/user/docs/data.csv",
    "/home/user/music/song.mp3",
    "/home/user/music/track.wav",
]
# dir_name = предпоследний компонент пути.
# Подсчитать сколько файлов в каждой папке.
from itertools import count
print(
    {path.split("/")[-2]:[p.split("/")[-2] for p in paths].count(path.split("/")[-2]) for path in paths}
)
from collections import Counter

counts = Counter(path.split("/")[-2] for path in paths)
print(counts)
# Q10. Dict {word: count_vowels}
words3 = ["banana","apple","cherry","sky"]
# Считать гласные "aeiou".

result = {}
vowels = ['a','e','i','u','o']
for word in words3:
    vowel_count =[]
    for i, letter  in enumerate(word.lower()):
        if letter in vowels:
            vowel_count.append((letter, i))
    result[word] = vowel_count    
print(result)
print(
    {word: sum(letter in vowels for letter in word.lower()) for word in words3}
)
print(
    {word: sum(1 for letter in word.lower()if letter in vowels) for word in words3}
)        
        
# Q11. Сет IP-адресов из лога
log_lines = [
    "127.0.0.1 GET /index.html",
    "192.168.0.1 POST /login",
    "10.0.0.256 FAIL",   # это невалидный IP
]
# Валидный = 4 числа 0–255 через "."
# Вытащить сет уникальных IP.
def check_ip(raw_ip):
    parts_ip = raw_ip.split('.')
    if len(parts_ip) != 4:
        return False
    for part in parts_ip:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True

set_ip = set()
for line in log_lines:
    parts = line.split()
    ip = parts[0]
    if check_ip(ip):
        set_ip.add(ip)
print(set_ip)

print(
    {line.split()[0] for line in log_lines if check_ip(line.split()[0])}
)     

# -----------------------------
# LEVEL D. Тяжёлые
# -----------------------------

# Q12. Матрица m: взять три вещи comprehension’ами
m = [
    [1,2,3],
    [4,5,6],
    [7,8,9],
]
# 1) Главная диагональ [1,5,9]
# 2) Побочная [3,5,7]
# 3) Граница (рамка): [1,2,3,6,9,8,7,4]
m = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]
diag = []
for i in range(len(m)):    
    diag.append(m[i][i])
print(diag)        
print(
    [m[i][i] for i in range(len(m))]
)
print(
    [m[i][len(m)-1-i] for i in range(len(m))]
)
frame = []
for i in range(len(m[0])):
    frame.append(m[0][i])
    
for i in range(1, len(m)-1):
    frame.append(m[i][-1])
    
for i in range(len(m[0])-1, -1, -1):
    frame.append(m[-1][i])
    
for i in range(len(m)-2, 0, -1):
    frame.append(m[i][0])
    
print(f"frame={frame}") 

def frame(matrix):
    rows, cols = len(matrix), len(matrix[0])
    return (
        
        [matrix[0][i] for i in range(cols)] +                       # верхняя строка
        [matrix[i][cols-1] for i in range(1, rows-1)] +             # правый столбец
        [matrix[rows-1][i] for i in range(cols-1, -1, -1)] +        # нижняя строка
        [matrix[i][0] for i in range(rows-2, 0, -1)]                # левый столбец
    )
print(frame(m))
# Q13. Dict {user_id: total_amount} из transactions
transactions = [
    {"user_id":1, "amount":100, "status":"paid"},
    {"user_id":2, "amount":50, "status":"failed"},
    {"user_id":1, "amount":70, "status":"paid"},
    {"user_id":3, "amount":200, "status":"paid"},
]
# Суммировать только по status="paid". 
total_amount_dict = {}     
for transaction in transactions:
    if transaction["status"] == "paid":
        uid = transaction["user_id"]
        amt = transaction["amount"]
        total_amount_dict[uid] = total_amount_dict.get(uid, 0) + amt            
print(f"total amount={total_amount_dict}")

from collections import defaultdict
total_amount_dict = defaultdict(int)
for t in transactions:
    if t["status"] == "paid":
        total_amount_dict[t["user_id"]] +=t["amount"]
print(total_amount_dict)
# Q14. Нормализатор CSV
rows = [
    {"email":"User@EXAMPLE.com", "age":"25"},
    {"email":"bademail.com", "age":"17"},
    {"email":"ok@test.org", "age":"40"},
    {"email":"", "age":""} 
]
# Преобразовать в список dict’ов:
# - email → lower и содержит "@"
# - age → int, 18<=age<=100
# - пустые → None
# - мусорные строки отфильтровать
# Разбей на comprehension’ы.
filtered_data =[
    user for user in rows if isinstance(user, dict)
                                        and ("email" in user or "age" in user)
]
processed_data = [{
    "email": (email if (email := str(user.get("email", "")).strip().lower())
              and "@" in email else None),
    "age": (int(age) if (age := user.get("age"))
                         and str(age).isdigit()
                         and 18 <= (age_int := int(age)) <= 100
                         else None)
    }
    for user in filtered_data
    if ((email := str(user.get("email", "")).strip().lower()) and "@" in email)
    or (age := user.get("age")) and str(age).isdigit() and 18 <= int(age) <= 100
]
for i, user in enumerate(processed_data, 1):
    print(f"{i}. {user}")

# Q15. Частотный словарь → top-K
text2 = "apple banana apple orange banana apple pear banana"
K = 3
# Составить словарь частот {word: count}.
# Взять top-K по (-count, word).
# Вернуть список строк "word:count".
raw_dict = dict(Counter(text2.lower().split()))
top_k3 = dict(sorted(raw_dict.items(), key=lambda item: item[1], reverse=True))
result = [f"{key}: {value}" for key, value in top_k3.items()]
print(result)

# Q16. Сжатие последовательности (RLE)
xs2 = [1,1,1,2,2,3,1,1]
# Построить [(value, run_length)].
# Пример: [(1,3),(2,2),(3,1),(1,2)]
from itertools import groupby
print(
    [(key, len(list(group))) for key, group in groupby(xs2)]
)
result = []
current_data = xs2[0]
counter = 1
for i in range(1, len(xs2)):
    if xs2[i] == current_data:
        counter += 1
    else:
        result.append((current_data, counter)) # double ()!!!!!
        counter = 1
        current_data = xs2[i]
result.append((current_data, counter))
print(result)
        
    

# Q17. Окна с шагом
xs3 = [10,20,30,40,50,60]
k, s = 3, 2
# Сгенерировать окна длиной k со сдвигом s:
# [[10,20,30],[30,40,50], ...]
windows = []
for i in range(0, len(xs3)-k+1, s):
   windows.append(xs3[i:i+k])
print(windows)

print([xs3[i:i+k] for i in range(0, len(xs3)-k+1, s)])

# Q18. Сетка координат
R = 3
step = 1
# [(x,y) ...] для всех целых x,y внутри круга радиуса R
# Условие: x*x+y*y <= R*R
result =[]
for x in range(-3, 4, 1):
    for y in range(-3, 4, 1):
        if x*x + y*y <= R*R:
            result.append((x,y))
print(f"R={result}")            
print(
    [(x, y)for x in range(-3, 4, 1) for y in range(-3, 4, 1) if x*x+y*y <= R*R]
)
# Q19. Индексы по двум ключам
records2 = [
    {"id":1,"country":"US","city":"NY"},
    {"id":2,"country":"US","city":"LA"},
    {"id":3,"country":"UK","city":"London"},
    {"id":4,"country":"US","city":"NY"},
]
# Собрать {(country,city): [ids...]}
result = defaultdict(list)
for rec in records2:
    key = (rec["country"], rec["city"])
    result[key].append(rec["id"])
print(dict(result))
print(
   # {(rec["country"], rec["city"]):[rec["id"]]for rec in records2}
) # doesn't work 

# Q20. Dict {formula: value_or_None}
formulas = ["2+2","10/2","abc","5*(3+2)"]
# eval только безопасные выражения из [0-9+-*/()]
# Остальные → None
allowed = set("0123456789+-*/()")
print(
    {f: eval(f) if set(f) <= allowed else None for f in formulas}
)
# Q21. Events → ISO-даты будни 9–18
events = [
    datetime(2024,5,6,10,0),   # понедельник
    datetime(2024,5,7,20,0),   # вторник, но вечер
    datetime(2024,5,11,12,0),  # суббота
    datetime(2024,5,8,15,0),   # среда
]
# Взять только будни, время 9–18.
# Вернуть список ISO-строк, отсортированный.
print(
    sorted(
        [dt.isoformat() for dt in events if 0 <= dt.weekday() <= 4
         and 9 <= dt.hour < 18]
    )
)

#Q22 Extra  - Slugy matrix

def slugy_route_generator(matrix):
    if not matrix or not matrix[0]:
        return[]
    result = []
    rows, cols = len(matrix), len(matrix[0])
    t, b = 0, len(matrix) - 1
    l, r = 0, len(matrix[0]) - 1
    
    def top_gen():
        for j in range(l, r +1):
           
            yield matrix[t][j]
    
    def right_gen():
        for i in range(t + 1, b):
            yield matrix[i][r]
            
    def bottom_gen():
        for j in range(r, l -1, -1):
            yield matrix[b][j]
    
    def left_gen():
        for i in range(b - 1, t, -1):
            yield matrix[i][t]          
        
    while t <= b and l <= r:
        
        result.extend(top_gen())
        
        if t < b:
            result.extend(right_gen())
            result.extend(bottom_gen())
            
        if l < r:            
            result.extend(left_gen())
        t += 1
        b -= 1
        l += 1
        r -= 1

    return result

result_gen = slugy_route_generator(m)
print(f"generation:{result_gen}")


    

 