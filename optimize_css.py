# optimize_css.py
import os
import re
import cssutils
import logging

# ----------------------------------------------------------------------
# Настройки
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.CRITICAL)
cssutils.log.setLevel(logging.CRITICAL)
cssutils.ser.prefs.keepComments = True
cssutils.ser.prefs.omitLastSemicolon = False
cssutils.ser.prefs.keepEmptyRules = False


# ----------------------------------------------------------------------
# 1. Загрузка классов
# ----------------------------------------------------------------------
def load_used_classes(classes_file: str) -> set:
    with open(classes_file, "r", encoding="utf-8") as f:
        txt = f.read()
    return {c.strip().lstrip(".") for c in re.split(r"[\s,]+", txt) if c.strip()}


# ----------------------------------------------------------------------
# 2. Проверка селектора
# ----------------------------------------------------------------------
def is_class_in_selector(sel: str, used: set) -> bool:
    if not sel or not used:
        return False
    for cls in used:
        pats = [
            rf"\.{re.escape(cls)}\b",
            rf'\[class[~*="\']{re.escape(cls)}["\']',
            rf'\[class\*="{re.escape(cls)}"\]',
            rf'\[.*="{re.escape(cls)}"\]',
        ]
        if any(re.search(p, sel) for p in pats):
            return True
    return False


# ----------------------------------------------------------------------
# 3. Рекурсивная проверка вложенных правил
# ----------------------------------------------------------------------
def has_used_class_in_rules(rules, used: set) -> bool:
    if not rules:
        return False
    for r in rules:
        if r.type == r.STYLE_RULE and r.selectorText:
            if is_class_in_selector(r.selectorText, used):
                return True
        if getattr(r, "cssRules", None):
            if has_used_class_in_rules(r.cssRules, used):
                return True
    return False


# ----------------------------------------------------------------------
# 4. Безопасное получение cssText
# ----------------------------------------------------------------------
def safe_css_text(rule) -> str:
    """Возвращает cssText или пустую строку, если None или ошибка"""
    try:
        text = rule.cssText
        return text.strip() if text and isinstance(text, str) else ""
    except:
        return ""


# ----------------------------------------------------------------------
# 5. Извлечение правил без дублей
# ----------------------------------------------------------------------
def extract_used_rules(css_folder: str, used_classes: set):
    seen = set()
    result = []

    for fn in os.listdir(css_folder):
        if not fn.lower().endswith(".css"):
            continue
        path = os.path.join(css_folder, fn)

        try:
            sheet = cssutils.parseFile(path)
        except Exception as e:
            print(f"Ошибка парсинга {fn}: {e}")
            continue

        for rule in sheet:
            css_text = safe_css_text(rule)
            if not css_text:
                continue  # пропускаем пустые/ошибочные правила

            # Нормализация для проверки дублей
            norm = re.sub(r"\s+", " ", css_text).strip()
            if norm in seen:
                continue
            seen.add(norm)

            rtype = rule.type

            # --- STYLE ---
            if rtype == rule.STYLE_RULE:
                if rule.selectorText and is_class_in_selector(rule.selectorText, used_classes):
                    result.append(("style", css_text))

            # --- COMMENT ---
            elif rtype == rule.COMMENT:
                result.append(("comment", css_text))

            # --- CONTAINER @-RULES (media, supports, etc.) ---
            elif getattr(rule, "cssRules", None) is not None:
                if has_used_class_in_rules(rule.cssRules, used_classes):
                    result.append(("at-rule", css_text))

            # --- OTHER @-RULES (font-face, keyframes, etc.) ---
            else:
                result.append(("at-rule", css_text))

    return result


# ----------------------------------------------------------------------
# 6. Сортировка и сохранение
# ----------------------------------------------------------------------
def sort_and_save_rules(rules, out_file: str):
    def key(item):
        typ, txt = item
        if typ == "comment":
            return (0, txt)
        if typ == "at-rule":
            return (1, txt.lower())
        m = re.search(r"\.([a-zA-Z_][\w-]*)", txt)
        cls = m.group(1).lower() if m else ""
        return (2, cls)

    rules_sorted = sorted(rules, key=key)

    with open(out_file, "w", encoding="utf-8", newline="\n") as f:
        for _, css in rules_sorted:
            f.write(css + "\n\n")

    print(f"Готово → {out_file}")
    print(f"   Сохранено правил: {len(rules_sorted)} (дубли удалены)")


# ----------------------------------------------------------------------
# 7. Запуск
# ----------------------------------------------------------------------
if __name__ == "__main__":
    CSS_FOLDER      = "css"
    CLASSES_FILE    = "used_classes.txt"
    OUTPUT_FILE     = "clear.css"

    print("Загрузка классов...")
    used = load_used_classes(CLASSES_FILE)
    print(f"   Классов: {len(used)}")

    print("Анализ CSS...")
    rules = extract_used_rules(CSS_FOLDER, used)

    print("Сохранение...")
    sort_and_save_rules(rules, OUTPUT_FILE)
