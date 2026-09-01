import sys
import timeit
from collections import deque
import matplotlib.pyplot as plt

sys.setrecursionlimit(10000)

MY_ROOT = 1
MY_HEIGHT = 5
MY_LEFT = lambda root: root * 2
MY_RIGHT = lambda root: root + 3

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

def build_tree_iterative(height=MY_HEIGHT,
                         root=MY_ROOT,
                         left_branch=MY_LEFT,
                         right_branch=MY_RIGHT):

    if height <= 0:
        return None

    tree = {'value': root, 'left': None, 'right': None}   
    queue = deque([(tree, 1)])                            

    while queue:
        node, level = queue.popleft()   

        if level >= height:              
            continue

        node['left'] = {'value': left_branch(node['value']),
                        'left': None, 'right': None}
        node['right'] = {'value': right_branch(node['value']),
                         'left': None, 'right': None}

        queue.append((node['left'], level + 1))
        queue.append((node['right'], level + 1))

    return tree


def print_tree(root_node):
    """Печатает дерево 'лёжа': корень слева, ветви вправо."""
    if root_node is None:
        print('(пустое дерево)')
        return

    stack = [(root_node, '', '')]      
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

def check_equal():
    print('=' * 64)
    print('1. ПРОВЕРКА: рекурсия и цикл строят одинаковое дерево')
    print('=' * 64)

    for h in range(1, 8):
        rec = build_tree_recursive(height=h)
        itr = build_tree_iterative(height=h)
        status = 'совпадают' if rec == itr else 'РАЗНЫЕ!'
        print(f'  height={h}:  узлов={count_nodes(rec):>5}  ->  {status}')

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

HEIGHTS = [4, 6, 8, 10, 12, 14, 16]
REPEAT = 5    
NUMBER = 3     


def bench(func, height):

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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(HEIGHTS, rec_times, 'o-', label='build_tree_recursive')
    ax1.plot(HEIGHTS, itr_times, 's-', label='build_tree_iterative')
    ax1.set_xlabel('Высота дерева (height)')
    ax1.set_ylabel('Время построения, мс')
    ax1.set_title('Обычная шкала')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.5)

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

def recursion_limit_test():
    print('\n' + '=' * 64)
    print('6. ГДЕ ЛОМАЕТСЯ РЕКУРСИЯ, А ЦИКЛ - НЕТ')
    print('=' * 64)

    sys.setrecursionlimit(100)          
    print('Ставим лимит рекурсии = 100 и строим дерево height=200:')

    try:
        build_tree_recursive(height=200, root=1)
        print('  рекурсия: построила')
    except RecursionError:
        print('  рекурсия: RecursionError - стек переполнен!')

    try:
        t = build_tree_iterative(height=20, root=1)   
        print(f'  цикл    : построил дерево height=20, узлов = {count_nodes(t)}')
    except RecursionError:
        print('  цикл    : RecursionError')

    sys.setrecursionlimit(10000)        

if __name__ == '__main__':
    check_equal()
    demo()
    rec, itr = benchmark_and_plot()
    recursion_limit_test()

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
