"""
Дополнительное задание: Многозадачность, Конкурентность и Асинхронность
Вариант 19 (Телемедицина):
  A. Threading  — запись данных пациентов в электронную очередь
  B. Multiprocessing — анализ «рентгеновского снимка» (поиск светлых пятен в матрице пикселей)
  C. Asyncio — асинхронная рассылка рецептов в аптеки
"""
import time
import random
import asyncio
import threading
import multiprocessing
import logging

logger = logging.getLogger('shop')


# ------- A. Threading: запись пациентов в очередь с Lock -------

patient_queue = []
queue_lock = threading.Lock()


def register_patient(patient_id: int, results: list):
    time.sleep(random.uniform(0.05, 0.15))
    with queue_lock:
        patient_queue.append(f'Пациент #{patient_id}')
        results.append(f'Поток {patient_id}: Пациент #{patient_id} записан в очередь')


def run_threading_demo() -> dict:
    start = time.perf_counter()
    patient_queue.clear()
    results = []
    threads = [threading.Thread(target=register_patient, args=(i, results)) for i in range(1, 6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start
    return {
        'name': 'Threading — Запись пациентов в очередь',
        'results': results,
        'queue': list(patient_queue),
        'elapsed': round(elapsed, 3),
        'note': (
            'Использован threading.Lock() для предотвращения состояния гонки. '
            '5 потоков параллельно регистрируют пациентов. '
            f'Время: {round(elapsed,3)}с (без многопоточности ≈ 0.5с)'
        ),
    }


# ------- B. Multiprocessing: поиск «светлых пятен» в матрице -------

def _find_bright_spots(chunk: list) -> list:
    threshold = 200
    return [i for i, val in chunk if val > threshold]


def run_multiprocessing_demo() -> dict:
    start = time.perf_counter()
    size = 200_000
    pixels = [(i, random.randint(0, 255)) for i in range(size)]
    chunk_size = size // 4
    chunks = [pixels[i * chunk_size:(i + 1) * chunk_size] for i in range(4)]
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(_find_bright_spots, chunks)
    bright = [idx for chunk_res in results for idx in chunk_res]
    elapsed = time.perf_counter() - start
    return {
        'name': 'Multiprocessing — Поиск светлых пятен в матрице пикселей',
        'total_pixels': size,
        'bright_count': len(bright),
        'elapsed': round(elapsed, 3),
        'note': (
            f'Проанализировано {size} пикселей в 4 процессах. '
            f'Найдено {len(bright)} ярких пикселей (>200). '
            f'Время: {round(elapsed,3)}с. '
            'Без multiprocessing потребовалось бы значительно больше времени на CPU-bound задачу.'
        ),
    }


# ------- C. Asyncio: рассылка рецептов в аптеки -------

async def _send_prescription(pharmacy_id: int, patient_name: str) -> str:
    await asyncio.sleep(random.uniform(0.05, 0.2))
    return f'Рецепт для {patient_name} отправлен в аптеку #{pharmacy_id}'


async def _run_async_demo_inner():
    patients = [f'Пациент #{i}' for i in range(1, 11)]
    tasks = [_send_prescription(i + 1, name) for i, name in enumerate(patients)]
    results = await asyncio.gather(*tasks)
    return list(results)


def run_asyncio_demo() -> dict:
    start = time.perf_counter()
    try:
        loop = asyncio.new_event_loop()
        results = loop.run_until_complete(_run_async_demo_inner())
        loop.close()
    except Exception as e:
        results = [f'Ошибка: {e}']
    elapsed = time.perf_counter() - start
    return {
        'name': 'Asyncio — Асинхронная рассылка рецептов в аптеки',
        'results': results,
        'elapsed': round(elapsed, 3),
        'note': (
            f'10 рецептов разосланы конкурентно за {round(elapsed,3)}с. '
            'Asyncio работает в одном потоке, но за счёт кооперативной многозадачности '
            'обрабатывает все задачи эффективнее, чем последовательное выполнение (≈1.25с).'
        ),
    }


def run_all_demos() -> list:
    return [
        run_threading_demo(),
        run_multiprocessing_demo(),
        run_asyncio_demo(),
    ]
