from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kb = 2048  # 2 МБ
    if file.size > max_size_kb * 1024:
        raise ValidationError("Файл слишком большой. Максимум 2 МБ.")
