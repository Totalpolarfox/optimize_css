## css_class_list.py
### collects into a separate text file the names of all classes (class=) from multiple HTML files in a specific directory
### собирает в отдельный текстовый файл названия всех классов (class=) из множества html-файлов в определенном каталоге


## optimize_css.py
### Merge multiple CSS files with duplicate class (selector) detection and optimization.

Input:
- A text file containing a list of all class (selector) names;
- A directory with CSS files.

Output: A new CSS file with data.

The input CSS files are analyzed:
- Only the rules for the classes present in the list of names are retained;
- Rules are sorted alphabetically;
- CSS variables, fonts, and media queries are processed;
- Various selector formats are taken into account.

======================================================

### Слияние нескольких CSS-файлов с поиском дубликатов классов (селекторов) и оптимизацией.

На входе:
- текстовый файл, который содержит список названий всех классов (селекторов);
- каталог с CSS-файлами.

На выходе - новый CSS-файл с данными.

Анализируются входные CSS-файлы:
- остаются правила только тех классов, которые присутствуют в списке названий;
- правила сортируются по алфавиту;
- проводится обработка переменных CSS, шрифтов, медиа-запросов;
- учитываются различные форматы селекторов.

