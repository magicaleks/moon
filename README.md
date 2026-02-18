# MOON (Magic Oriented Object Notation) [Under development!]

[![CI](https://github.com/magicaleks/moon/actions/workflows/ci.yml/badge.svg)](https://github.com/magicaleks/moon/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/magicmoon)](https://pypi.org/project/magicmoon/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Фреймворк для работы с MOON в Python.
MOON - это гибрид YAML и TOON. Отличительная особенность - 
это мультимодельность данных и неограниченная расширяемость.

## Почему MOON?
Вы сами можете определять теги и типы и реализовывать для них
требуемую логику.

Тег - это директива обозначающая начало определённой структуры данных,
например `@object` или `@array`. С помощью системы хуков можно
самостоятельно определять кастомные теги.

Основная идея использования - конфигурации приложений.

## Быстрый старт

Установка:
```shell
pip install magicmoon
```

Использование:
```python
import moon

obj = moon.load("./example.moon")
print(obj["context"])
```

## Эталонная реализация Python (v3.12.6)

Публичный интерфейс реализован в [_api.py](/moon/_api.py). Импортируется не напрямую, а из moon (`__init__.py`).
`load(file_path)` - парсинг файла в `object`. Оба потока поддерживаются, как строка (буфер), так и файл.
`dump(magicked_data, file_path)` - сохранение объекта в файл.

Ядро фреймворка [lib](/moon/core) определяет внутренние механизмы.
Принцип работы:
Из MOON в Python object:
1. Токенизация, [tokenizer.py](/moon/core/tokenizer.py) проходится по всему файлу и разбивает
его на токены. Это лексические части файла, например `word`, `colon`, `tab`.
2. Парсинг, [parser.py](/moon/core/tokenizer.py) парсит токены в поток событий.
События это декларативное описание: `tag_start` - начата структура определённого тега.
3. Композиция, [composer.py](/moon/core/composer.py) из потока событий формирует AST (Abstract Syntax Tree).
4. Сборка, [constructor.py](/moon/core/constructor.py) из AST собирает готовый python `dict[str, Any]`.
На этом же этапе все типы помеченные как `ScalarNode` в AST проходят определение типов. Расширить поддерживаемые типы
можно через `TypeHook`.

Из Python object в MOON:
1. Представление в AST, [representer.py](/moon/core/representer.py) преобразует python `dict[str, Any]` в AST, используя
обратные методы представления `TypeHook`.
2. Сериализация, [serializer.py](/moon/core/serializer.py) преобразует AST в поток событий.
3. Генерация, [emitter.py](/moon/core/emitter.py) генерирует финальный MOON текст из потока событий.

Модуль [schemas](/moon/schemas) хранит все определения типов:
1. Набор исключений [errors.py](/moon/schemas/errors.py)
2. Модель и типы токенов, лексем на которые разбивается исходный MOON [tokens.py](/moon/schemas/tokens.py)
3. Модель и типы событий, декларативных описаний происходящего в MOON [events.py](/moon/schemas/events.py)
4. Базовые узлы AST, в том числе `TagNode` - это базовая нода для каждого тега [nodes.py](/moon/schemas/nodes.py)

Основной принцип работы пайплайнов построен на:
1. `StatefulStreamer` - это абстрактный класс реализующий интерфейс для работы stream to stream (iterable to iterable)
2. `TagHook` - это хук тега, в пайплайне нет никаких точных реализаций парсинга структур тего. Для каждого тега на каждом
этапе вызывается соответсвующий метод хука, определённого для этого тега.

## Спецификация

Оригинальны фреймворк поставляется с тегами:
1. `@object` - это именованные объекты, поддерживающие вложенность, синтаксис как в YAML.
После тега `@object` идёт название, далее `key: value`
```moon
// Can be commented
@object Config
  user: Alex
  password: something-secret
  context:
    revision: 177
  friends_list: danil,vladimir
```
В Python представлении:
```python
magicked_data = {
    "Config": {
        "user": "Alex",
        "password": "something-secret",
        "context": {
            "revision": 177
        },
        "friends_list": ["danil", "vladimir"]
    }
}
```

## Лицензия
Проект инициирован, разработан и поддерживается Aleksandr @magicaleks.
Распространяется на основании лицензии Apache-2.0.
