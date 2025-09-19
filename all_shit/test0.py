# exam.py  
# Python Roadmap v2.0: Жестяной Экзамен
# Каждое задание = уровень. Ты отвечаешь в коде или комменте.
# Я потом разнесу твои ответы, если будут дырки.

# -----------------------------
# LEVEL A. List/Lambda/GenExp
# -----------------------------

# Q1. Сделай dict comprehension:
# {слово: длина} только для слов длиннее 3.
# words = ["cat", "parrot", "dog", "elephant"]
# Подъёбка: если сделаешь через for+if, я тебе минус поставлю.
words = ["cat", "parrot", "dog", "elephant"]
averages = {w: len(w) for w in words if len(w) >3}
print(averages)

# Q2. Отсортируй список чисел по последней цифре через lambda.
numbers = [21, 4, 32, 45, 87, 50]
# Подъёбка: попробуй без key=lambda x: x % 10 — тогда я поверю, что ты не бот.


# -----------------------------
# LEVEL B. yield / generators
# -----------------------------

# Q3. Напиши генератор chunked(seq, n).
# >>> list(chunked("abcdefg", 3)) → ["abc", "def", "g"]
# Подъёбка: если сделаешь через while True и break — я спалю костыли.

# Q4. Реализуй генератор, который даёт бесконечную последовательность
# степеней двойки: 1, 2, 4, 8, 16...
# Подъёбка: если используешь range, значит, не понял сути.


# -----------------------------
# LEVEL C. Функциональщина
# -----------------------------

# Q5. Напиши reduce, который перемножает все элементы списка.
# nums = [2, 3, 5, 7]
# Подъёбка: если сделаешь через for, тебя отправлю назад в школу.

# Q6. Сделай декоратор @debug, который печатает имя функции и её аргументы
# перед вызовом.
# Подъёбка: если забудешь functools.wraps — я тебя спалю на плагиате.


# -----------------------------
# LEVEL D. ООП мясо
# -----------------------------

# Q7. Класс RangeLike(start, stop, step=1)
# Работает как range: len(), in, итерирование.
# Подъёбка: если используешь готовый range внутри — я тебя спалю как ленивого.

# Q8. Напиши датакласс Product(name, price).
# Добавь метод __str__, который выводит "Product: <name> — $<price>"
# Подъёбка: если забудешь про type hints — считай, не сделал.


# -----------------------------
# LEVEL E. Iterators Hardcore
# -----------------------------

# Q9. Реализуй PeekableIterator.
# >>> it = PeekableIterator([10, 20, 30])
# >>> it.peek() → 10, it.next() → 10, it.peek() → 20
# Подъёбка: если у тебя вылезет StopIteration в peek() — иди перечитывай Пеп8.


# -----------------------------
# LEVEL F. Async
# -----------------------------

# Q10. async def fetch_all(urls): грузит список урлов параллельно и возвращает длины ответов.
# Подъёбка: если сделаешь через requests — я тебя высмею и отправлю изучать asyncio.
sq = [x**2 for x  in range(0, 11, 2)]
print(sq)


lines = ['  hello  ', 'world  ', '  python', '   ']
cl = [line.strip().lower() for line in lines if line.strip()]
print(cl)

mtrx = [[1,2],[3]]
fl = [num for row in mtrx for num in row]
print(fl)

A = [34,345,4,5431,4]
B=[45,45,56,3,55]

sm = [a+b for a, b in zip(A, B)]
print(f"zip={sm}")

words = ['app', 'banana', 'ap', 'orange', 'banana', 'apple']

lw = [word for word in words if len(word) >3 ]
print((lw))

d0 = {"France": "Paris", "Germany": "Berlin"}
invd1 = {v:k for k, v in d0.items()}
print(d0)
print((invd1))

users = {
    "alice": {"role": "admin", "age": 30},
    "bob": {"role": "user", "age": 22},
    "charlie": {"role": "moderator", "age": 27},
    "diana": {"role": "user", "age": 25},
    "eric": {"role": "admin", "age": 35}
}
by_role = {
    name: info for name, info in users.items() if info["role"] == 'user'
    }
print(by_role)

emails = ['user@example.com', 'admin@test.org', 'user@example.com', 'info@test.org']

domains = {email.split('@')[1] for email in emails}
print(domains)

files = [
    "report.docx",
    "data.csv",
    "presentation.pptx",
    "script.py",
    "archive.zip",
    "image.png",
    "notes.txt",
    "backup.tar.gz",
    "music.mp3",
    "video.mp4"
]
unique_ext = {f.split('.')[-1] for f in files}
print(unique_ext)

words = ['python', 'web', 'django', 'data', 'pandas', 'javascript', 'react']

unique_w = {
    sym for word in words for sym in word.lower() if sym.isalpha()
}
print(unique_w)