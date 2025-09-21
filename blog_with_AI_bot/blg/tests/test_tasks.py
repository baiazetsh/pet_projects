#blg/test_tasks.py
import pytest
from zz.models import Post
from zz.tasks import summarize_post


@pytest.mark.django_db
def test_summarize_post_saves_and_returns(monkeypatch):
    # 1. Подготовка: создаём пост без summary
    post = Post.objects.create(
        title="Тестовый пост",
        content="Это очень длинный текст для проверки работы таска. " * 20
    )

    # 2. Мокаем generate_text, чтобы не стучаться в Ollama
    def fake_generate_text(prompt, model):
        return "Фейковое резюме от Ollama"

    monkeypatch.setattr("zz.tasks.generate_text", fake_generate_text)

    # 3. Запускаем таск напрямую (без Celery брокера)
    result = summarize_post(post.id)

    # 4. Проверяем результат
    post.refresh_from_db()
    assert result == "Фейковое резюме от Ollama"
    assert post.summary == "Фейковое резюме от Ollama"
