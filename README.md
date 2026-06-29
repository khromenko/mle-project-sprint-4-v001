# Подготовка виртуальной машины

## Склонируйте репозиторий

Сначала копируем себе оригинальный репозиторий в личное пространство Github в качестве шаблона (через UI Github)
```
# оригинал
https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

Далее настраиваем рабочее пространство на ВМ
```
# клонируем репозиторий
git clone https://github.com/khromenko/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv .venv_mle-project-sprint-4-v001
```

После его инициализации следующей командой

```
. .venv_mle-project-sprint-4-v001/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

Скаченные файлы с данными переместим для удобства в директорию `data/datasets/`
```ll -h data/datasets/
:~/mle_projects/sprint-4/mle-project-sprint-4-v001$ ll -h data/datasets/
total 1.2G
-rw-rw-r-- 1 mle-user mle-user  35M Jul  4  2024 catalog_names.parquet
-rw-rw-r-- 1 mle-user mle-user 1.2G Jul 14  2024 interactions.parquet
-rw-rw-r-- 1 mle-user mle-user  19M Jul  4  2024 tracks.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```
Для удобства работы можно открыть файл ноутбука прямо в интерфейсе VC Code

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

- Код сервиса рекомендаций находится в файле `app\recommendations_service.py`.
- Настройки логирования находится в файле `app\logging_config.py`.
- Перед запуском необходимо прописать пути к подготовленным на Этапе 3 файлам модели в .env файле
    - ML_MODEL_USER_DATA_PATH = data/recsys/recommendations.parquet
    - ML_MODEL_COMMON_DATA_PATH = data/recsys/top_popular.parquet
    - ML_MODEL_SIM_DATA_PATH = data/recsys/similar.parquet

Все команды выполняются из корневой директории проекта (и активированной venv).

- Запуск основного сервиса рекомендаций:

    ``` bash
    uvicorn app.recommendations_service:app --port 8000
    ```

- Запуск сервиса сбора событий пользователя (Event store service)

    ``` bash
    uvicorn app.events.user_event_service:app --port 8001
    ```

- Запуск сервиса управления контентом для получения похожих объектов (Content service)

    ``` bash
    uvicorn app.content.content_service:app --port 8002
    ```    


# Инструкции для тестирования сервиса

- Установить модуль для тестирования

    ```bash
    pip install pytest
    ```
- Настройки для тестирования находятся в `test\conftest.py` (согласно соглашению pytest)

Все команды выполняются из корневой директории проекта (и активированной venv).

## Тестирование основного сервиса рекомендаций

- Код для тестирования сервиса находится в файле `test\test_service.py`.
- Доступн вызов 3-х тест-кейсов
    - offline - для получения оффлайн рекомендаций
    - online - для получения онлайн рекомендаций
    - full - для получения одновременно оффлайн и онлайн рекомендаций

    ```bash
    python -m pytest test/test_service.py --case=(offline|online|full) -s
    ```

## Тестирование сервиса сбора событий пользователей

- код для тестирования сервиса находится в файле `test\test_event_store.py`
- запуск тестов

    ```bash
    python -m pytest test/test_event_store.py -s
    ```
## Тестирование сервиса управление контентом

- код для тестирования сервиса находится в файле `test\test_event_store.py`
- запуск тестов

    ```bash
    python -m pytest test/test_event_store.py -s
    ```    