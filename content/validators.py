from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kb = 5120  # 5 МБ
    if file.size > max_size_kb * 1024:
        raise ValidationError("Слишком большой файл превью! Максимальный размер: 5 МБ.")
