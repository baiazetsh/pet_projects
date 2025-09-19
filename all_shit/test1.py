#A
print([x**2 for x in range(0,11,2)])

lines = ['  hello  ', 'world  ', '  python', '   ']
print(
    [l.strip().lower() for l in lines if l.strip()]
)
words = ['app', 'banana', 'ap', 'orange', 'banana', 'apple']
print(
    [w for w in words if len(w) > 4]
)
emails = ['user@example.com', 'admin@test.org', 'user@example.com', 'info@test.org']
print(
    [domain.split('@')[1] for domain in emails]
)
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
print(
    [ext.split('.')[-1] for ext in files]
)
print(
    {word: len(word) for word in words}
)
nums = [0, 54, -8, 64, 987, -88, 971, 3, 1]
print(
    ['odd' if x % 2 == 1 else "even" for x in nums]
)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print((
    [num for row in matrix for num in row]
))
lines = ['  Hello  ', 'woRld  ', '  python', '   ']
print(
    {letter.lower() for word in lines for letter in word if letter.isalpha()}
)
xs = [10, 20, 30, 40, 50]
print(
    {i: xs[i]**2 for i, _ in enumerate(xs) if i % 2 == 0}
)
#B
users ={
    1: {"id": 16, "name": "Alice", "role": "admin"},
    2: {"id": 28, "name": "Bob", "role": "user"},
    3: {"id": 83, "name": "Charlie", "role": "moderator"},
    4: {"id": 49, "name": "Diana", "role": "user"},
    5: {"id": 577, "name": "Eric", "role": "admin"}
}
print(
    {user["id"]: user for user in users.values()}
)
items = [
    {"name": "apple", "price": 1.0},
    {"name": "banana", "price": 1.5},
    {"name": "mango", "price": 2.25},
]
print(
    {item["name"]: item["price"]*1.2 for item in items}
)
pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 1)]
print(
    {v: k for k, v in pairs}
)
from collections import defaultdict

result = defaultdict(list)
for k, v in pairs:
    result[v].append(k)
print(dict(result)
    
)
products = [
    {"name": "pen", "price": 2, "stock": 100},
    {"name": "book", "price": 15, "stock": 0},
    {"name": "laptop", "price": 1200, "stock": 5},
    {"name": "notebook", "price": 3, "stock": 25},
]
limit = 20
print(
    {product["name"]: product["price"] for product in products if product["price"] <= limit and product["stock"] > 0}
)
text = "level madam kayak python racecar stats civic rotavator"
words = text.split()
print(
    {w:w[::-1] for w in words if w == w[::-1]}
)
records = [
    {"year": 2023, "month": 5, "day": 10},
    {"year": 2023, "month": 5, "day": 12},
    {"year": 2024, "month": 1, "day": 1},
    {"year": 2024, "month": 7, "day": 30},
]
print(
    {(r["year"], r["month"]) for r in records}
)
names = [" Alice ", "Bob", "  Charlie", "Diana  "]
print(
    {idx: name.strip() for idx, name in enumerate(names, 1)}
) 
students = {
    "Alice": [90, 80, 70],
    "Bob": [100],
    "Charlie": [],
    "Diana": [65, 75, 85, 95],
}
print(
    {name: round(sum(s)/len(s), 1) for name, s in students.items() if s}
)  
raw_strings = [" hello ", " ", "world", "", " python  "]

print(
    (','.join(str.strip() for str in raw_strings if str.strip()))
)
words = ["apple", "application", "banana", "band", "cat", "catalog"]
print(
    {w[:3]: w for w in words}
)
result = defaultdict(list)
[result[w[:3]].append(w) for w in words]
print(dict(result))
words2 = ["car", "bus", "train", "plane", "rocket", "AI", "data123"]
print(
    {w for w in words2 if w.isalpha() and 3 <= len(w) <= 7}
)
n = 5 
print(
    {(i, j) for i in range(n) for j in range(i+1, n)}
)