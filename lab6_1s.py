"""
=======================================================================
 Сравнение РЕКУРСИВНОГО и ИТЕРАТИВНОГО построения бинарного дерева
 Вариант №1: root = 1, height = 5, left = root*2, right = root+3

 В файле:
   1) build_tree_recursive  - рекурсия
   2) build_tree_iterative  - цикл + очередь (deque)
   3) проверка, что деревья совпадают
   4) замер времени через timeit
   5) график matplotlib
   6) выводы
=======================================================================
"""

import sys
import timeit
from collections import deque
import matplotlib.pyplot as plt

# рекурсия глубокая -> поднимаем лимит на всякий случай
sys.setrecursionlimit(10000)


# =====================================================================
#  НАСТРОЙКИ ВАРИАНТА (меняем только эти 4 строки под свой номер)
# =====================================================================
MY_ROOT = 1
MY_HEIGHT = 5
MY_LEFT = lambda root: root * 2
MY_RIGHT = lambda root: root + 3


# =====================================================================
#  1. РЕКУРСИВНОЕ ПОСТРОЕНИЕ
# =====================================================================

def build_tree_recursive(height=MY_HEIGHT,
                         root=MY_ROOT,
                         left_branch=MY_LEFT,
                         right_branch=MY_RIGHT):
    """
    Строит дерево РЕКУРСИЕЙ.

    Идея: узел = {значение, левое поддерево, правое поддерево},
    а поддеревья строит та же самая функция с height-1.

    Результат: {'value': 1, 'left': {...}, 'right': {...}}
    height <= 0 -> None (база рекурсии)
    """
    if height <= 0:                      # база: дальше не идём
        return None

    return {
        'value': root,
        'left':  build_tree_recursive(height - 1, left_branch(root),
                                      left_branch, right_branch),
        'right': build_tree_recursive(height - 1, right_branch(root),
                                      left_branch, right_branch),
    }


# =====================================================================
#  2. ИТЕРАТИВНОЕ ПОСТРОЕНИЕ (цикл + очередь)
# =====================================================================

def build_tree_iterative(height=MY_HEIGHT,
                         root=MY_ROOT,
                         left_branch=MY_LEFT,
                         right_branch=MY_RIGHT):
    """
    Строит ТО ЖЕ дерево БЕЗ рекурсии.

    Идея: заводим очередь необработанных узлов.
    Достаём узел -> создаём ему двух потомков -> кладём их в очередь.
    Так дерево заполняется по уровням (обход в ширину, BFS).

    Результат в точности такой же, как у рекурсивной версии.
    """
    if height <= 0:
        return None

    tree = {'value': root, 'left': None, 'right': None}   # корень
    queue = deque([(tree, 1)])                            # (узел, уровень)

    while queue:
        node, level = queue.popleft()    # popleft() = O(1)

        if level >= height:              # достигли дна -> это лист
            continue

        node['left'] = {'value': left_branch(node['value']),
                        'left': None, 'right': None}
        node['right'] = {'value': right_branch(node['value']),
                         'left': None, 'right': None}

        queue.append((node['left'], level + 1))
        queue.append((node['right'], level + 1))

    return tree


# =====================================================================
#  ПЕЧАТЬ ДЕРЕВА (только для наглядности)
# =====================================================================

def print_tree(root_node):
    """Печатает дерево 'лёжа': корень слева, ветви вправо."""
    if root_node is None:
        print('(пустое дерево)')
        return

    stack = [(root_node, '', '')]        # (узел, отступ, маркер)
    while stack:
        node, indent, marker = stack.pop()
        print(indent + marker + str(node['value']))
        child_indent = indent + '   '
        if node['right'] is not None:
            stack.append((node['right'], child_indent, 'R-'))
        if node['left'] is not None:
            stack.append((node['left'], child_indent, 'L-'))


def count_nodes(tree):
    """Считает узлы БЕЗ рекурсии - для проверки размера дерева."""
    if tree is None:
        return 0
    n, stack = 0, [tree]
    while stack:
        node = stack.pop()
        n += 1
        if node['left'] is not None:
            stack.append(node['left'])
        if node['right'] is not None:
            stack.append(node['right'])
    return n


# =====================================================================
#  3. ПРОВЕРКА: оба способа дают ОДИНАКОВОЕ дерево
# =====================================================================

def check_equal():
    print('=' * 64)
    print('1. ПРОВЕРКА: рекурсия и цикл строят одинаковое дерево')
    print('=' * 64)

    for h in range(1, 8):
        rec = build_tree_recursive(height=h)
        itr = build_tree_iterative(height=h)
        status = 'совпадают' if rec == itr else 'РАЗНЫЕ!'
        print(f'  height={h}:  узлов={count_nodes(rec):>5}  ->  {status}')


# =====================================================================
#  4. ДЕМОНСТРАЦИЯ ДЕРЕВА
# =====================================================================

def demo():
    print('\n' + '=' * 64)
    print('2. ДЕРЕВО height=3 (рекурсия) - словарь')
    print('=' * 64)
    print(build_tree_recursive(height=3))

    print('\nНаглядно:')
    print_tree(build_tree_recursive(height=3))

    print('\n' + '=' * 64)
    print(f'3. МОЙ ВАРИАНТ: root={MY_ROOT}, height={MY_HEIGHT} (цикл)')
    print('=' * 64)
    print_tree(build_tree_iterative())

    print('\n' + '=' * 64)
    print('4. ПАРАМЕТРИЗАЦИЯ: свои формулы через аргументы')
    print('=' * 64)
    print_tree(build_tree_iterative(height=3, root=100,
                                    left_branch=lambda r: r - 10,
                                    right_branch=lambda r: r + 10))


# =====================================================================
#  5. ЗАМЕР ВРЕМЕНИ + ГРАФИК
# =====================================================================

# один фиксированный список высот для ВСЕХ прогонов
HEIGHTS = [4, 6, 8, 10, 12, 14, 16]
REPEAT = 5      # сколько прогонов усредняем
NUMBER = 3      # сколько построений внутри одного прогона


def bench(func, height):
    """
    Чистый бенчмарк ОДНОГО построения дерева.
    Берём минимум из REPEAT прогонов -> меньше помех от ОС.
    Возвращает время в миллисекундах.
    """
    times = timeit.repeat(lambda: func(height=height),
                          repeat=REPEAT, number=NUMBER)
    return min(times) / NUMBER * 1000


def benchmark_and_plot():
    print('\n' + '=' * 64)
    print('5. СРАВНЕНИЕ ВРЕМЕНИ ПОСТРОЕНИЯ')
    print('=' * 64)
    print(f"{'height':>7} | {'узлов':>7} | {'рекурсия,мс':>12} | "
          f"{'цикл,мс':>9} | {'во сколько раз':>14}")
    print('-' * 64)

    rec_times, itr_times, nodes = [], [], []

    for h in HEIGHTS:
        t_rec = bench(build_tree_recursive, h)
        t_itr = bench(build_tree_iterative, h)
        n = 2 ** h - 1

        rec_times.append(t_rec)
        itr_times.append(t_itr)
        nodes.append(n)

        print(f'{h:>7} | {n:>7} | {t_rec:>12.3f} | '
              f'{t_itr:>9.3f} | {t_rec / t_itr:>13.2f}x')

    # ---------- график ----------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # слева: обычная шкала
    ax1.plot(HEIGHTS, rec_times, 'o-', label='build_tree_recursive')
    ax1.plot(HEIGHTS, itr_times, 's-', label='build_tree_iterative')
    ax1.set_xlabel('Высота дерева (height)')
    ax1.set_ylabel('Время построения, мс')
    ax1.set_title('Обычная шкала')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.5)

    # справа: логарифмическая - видно рост в 2 раза на каждый уровень
    ax2.plot(HEIGHTS, rec_times, 'o-', label='build_tree_recursive')
    ax2.plot(HEIGHTS, itr_times, 's-', label='build_tree_iterative')
    ax2.set_yscale('log')
    ax2.set_xlabel('Высота дерева (height)')
    ax2.set_ylabel('Время построения, мс (лог. шкала)')
    ax2.set_title('Логарифмическая шкала')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', alpha=0.5)

    fig.suptitle('Построение бинарного дерева: рекурсия vs цикл', fontsize=13)
    plt.tight_layout()
    plt.savefig('tree_benchmark.png', dpi=120)
    print('\nГрафик сохранён в файл tree_benchmark.png')
    plt.show()

    return rec_times, itr_times


# =====================================================================
#  6. ГРАНИЦА РЕКУРСИИ
# =====================================================================

def recursion_limit_test():
    print('\n' + '=' * 64)
    print('6. ГДЕ ЛОМАЕТСЯ РЕКУРСИЯ, А ЦИКЛ - НЕТ')
    print('=' * 64)

    sys.setrecursionlimit(100)           # искусственно занижаем лимит
    print('Ставим лимит рекурсии = 100 и строим дерево height=200:')

    try:
        build_tree_recursive(height=200, root=1)
        print('  рекурсия: построила')
    except RecursionError:
        print('  рекурсия: RecursionError - стек переполнен!')

    try:
        t = build_tree_iterative(height=20, root=1)   # 20, чтобы влезло в память
        print(f'  цикл    : построил дерево height=20, узлов = {count_nodes(t)}')
    except RecursionError:
        print('  цикл    : RecursionError')

    sys.setrecursionlimit(10000)         # возвращаем как было


# =====================================================================
#  ТОЧКА ВХОДА
# =====================================================================

if __name__ == '__main__':
    check_equal()
    demo()
    rec, itr = benchmark_and_plot()
    recursion_limit_test()

    # ---------- выводы ----------
    avg = sum(r / i for r, i in zip(rec, itr)) / len(rec)
    print('\n' + '=' * 64)
    print('7. ВЫВОДЫ')
    print('=' * 64)
    print(f'  - Сложность обоих алгоритмов: O(2^height) - число узлов.')
    print(f'  - Рекурсия в среднем медленнее в {avg:.2f} раза.')
    print(f'  - Причина: каждый узел = отдельный вызов функции')
    print(f'    (создание кадра стека, передача 4 аргументов, возврат).')
    print(f'  - Рекурсия расходует стек: глубина = height,')
    print(f'    при большой высоте -> RecursionError (см. п.6).')
    print(f'  - Цикл использует обычную очередь в куче - ограничен')
    print(f'    только объёмом ОЗУ.')
    print(f'  - ИТОГ: результат одинаковый, но итеративная версия')
    print(f'    быстрее и надёжнее. Рекурсия короче и нагляднее.')