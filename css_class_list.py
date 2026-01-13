# собирает в отдельный текстовый файл названия всех классов (class=) 
# из множества html-файлов в определенном каталоге
# collects into a separate text file the names of all classes (class=) 
# from multiple HTML files in a specific directory


import os
from bs4 import BeautifulSoup

input_dir = 'html/'
output_file = 'used_classes.txt'
seen_classes = set()

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(('.html', '.htm')):
        continue
    filepath = os.path.join(input_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            for tag in soup.find_all(class_=True):
                classes = tag.get('class')
                if isinstance(classes, list):
                    seen_classes.update(classes)
    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}")

# Сохранение
with open(output_file, 'w', encoding='utf-8') as f:
    for cls in sorted(seen_classes):
        f.write(cls + '\n')

print(f"Найдено {len(seen_classes)} уникальных классов. Сохранено в {output_file}")
