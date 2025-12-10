import os

# Создаем необходимые директории для проекта
folders = [
    'static/videos',
    'static/images',
    'static/css',
    'static/js',
    'templates'
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Создана директория: {folder}")

# Создаем placeholder для видео
placeholder_message = """
Эта директория предназначена для хранения фоновых видео.
Поместите сюда файл background.mp4 для использования его на странице доступа.
"""

with open('static/videos/README.txt', 'w') as f:
    f.write(placeholder_message)
    print("Создан файл README.txt в директории static/videos")

print("\nСтруктура проекта успешно создана!")
print("Чтобы добавить фоновое видео, поместите файл background.mp4 в директорию static/videos или воспользуйтесь страницей /upload")
