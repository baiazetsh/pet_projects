import ctypes

MB_YESNO = 0x04   # кнопки Yes/No
MB_ICONQUESTION = 0x20  # иконка с вопросом

IDYES = 6
IDNO = 7

result = ctypes.windll.user32.MessageBoxW(
    0,
    "Хочешь записать файл?",
    "Подтверждение",
    MB_YESNO | MB_ICONQUESTION
)

if result == IDYES:
    print("Пользователь выбрал YES")
elif result == IDNO:
    print("Пользователь выбрал NO")
