"""Append covariance and correlation exercises to the lesson 13 notebook builder."""


def add_tasks(md, code, theory, eq, box):
    """Build unanswered tasks; notebook execution does not import this module."""
    md("## Практика: сначала расчёт на бумаге, затем проверка")
    md("""Задачи 1–5 — основной набор. В них числа небольшие: сначала выполните расчёты на бумаге,
а затем перенесите их в NumPy. Таблицы отклонений и произведений сохраняйте вместе с ответом.
Задачи 6–8 можно оставить для самостоятельной работы.

Здесь везде используется **выборочная ковариация с делением на n − 1**, где n — число наблюдений,
и выборочное стандартное отклонение с тем же делителем. Все данные учебные и встроены в ячейки.
""")

    theory("Задача 1. Четыре пары наблюдений",
        "<p>Даны четыре пары значений двух признаков. Каждая строка — одно наблюдение.</p>"
        "<table><thead><tr><th>Наблюдение</th><th>x</th><th>y</th></tr></thead><tbody>"
        "<tr><td>1</td><td>1</td><td>6</td></tr><tr><td>2</td><td>2</td><td>4</td></tr>"
        "<tr><td>3</td><td>4</td><td>3</td></tr><tr><td>4</td><td>5</td><td>1</td></tr>"
        "</tbody></table>"
        "<ol><li>Найдите оба средних.</li><li>Для каждой строки запишите отклонение x от его среднего, "
        "отклонение y от его среднего и произведение этих отклонений.</li>"
        "<li>Сложите произведения и вычислите выборочную ковариацию.</li></ol>"
        + box("Сначала знак", "До вычислений предположите знак ковариации. Затем объясните его через знаки произведений отклонений."))
    code(r'''x_hand_task = np.array([1.0, 2.0, 4.0, 5.0])
y_hand_task = np.array([6.0, 4.0, 3.0, 1.0])
# TODO: Reproduce the handwritten table with elementary NumPy operations.
x_mean_task = ...
y_mean_task = ...
dx_hand_task = ...
dy_hand_task = ...
products_hand_task = ...
cov_hand_task = ...''', ("student-core", "task-1"))
    code(r'''if any(value is Ellipsis for value in [x_mean_task, y_mean_task, dx_hand_task,
                                          dy_hand_task, products_hand_task, cov_hand_task]):
    print("Сначала заполните задачу 1.")
else:
    print("Ваши средние:", x_mean_task, y_mean_task)
    display(pd.DataFrame({"x": x_hand_task, "y": y_hand_task,
                          "Отклонение x": dx_hand_task, "Отклонение y": dy_hand_task,
                          "Произведение": products_hand_task}))
    print("Ваша ковариация:", cov_hand_task)
    print("Проверка через NumPy:",
          np.allclose(cov_hand_task, np.cov(x_hand_task, y_hand_task, ddof=1)[0, 1]))''',
         ("provided", "task-check"))
    md("**Ваш вывод:** какой знак вы ожидали и как таблица отклонений объясняет полученный результат? …",
       ("interpretation", "task-1"))

    theory("Задача 2. От ковариации к коэффициенту Пирсона",
        "<p>Используйте те же четыре пары. На бумаге найдите сумму квадратов отклонений каждого признака, "
        "выборочные дисперсии и стандартные отклонения. Затем вычислите корреляцию Пирсона.</p>"
        "<p>Получите тот же коэффициент вторым способом: как скалярное произведение центрированных "
        "векторов, делённое на произведение их длин. Не округляйте промежуточные результаты.</p>"
        + box("Сверьте два расчёта", "Покажите в записи, как делитель n − 1 сокращается при переходе "
              "от ковариации и стандартных отклонений к скалярному произведению и длинам."))
    code(r'''# The inputs are repeated so the task can be completed independently.
x_pearson_task = np.array([1.0, 2.0, 4.0, 5.0])
y_pearson_task = np.array([6.0, 4.0, 3.0, 1.0])
# TODO: Use centered values and sums, not np.var, np.std, or np.corrcoef yet.
var_x_task = ...
var_y_task = ...
std_x_task = ...
std_y_task = ...
r_pearson_task = ...
r_cosine_task = ...''', ("student-core", "task-2"))
    code(r'''if any(value is Ellipsis for value in [var_x_task, var_y_task, std_x_task,
                                          std_y_task, r_pearson_task, r_cosine_task]):
    print("Сначала заполните задачу 2.")
else:
    print("Ваши дисперсии:", var_x_task, var_y_task)
    print("Ваши стандартные отклонения:", std_x_task, std_y_task)
    print("Пирсон через ковариацию:", r_pearson_task)
    print("Пирсон через косинус:", r_cosine_task)
    print("Дисперсии согласуются с NumPy:",
          np.allclose([var_x_task, var_y_task],
                      [np.var(x_pearson_task, ddof=1), np.var(y_pearson_task, ddof=1)]))
    print("Оба расчёта корреляции согласуются с NumPy:",
          np.allclose([r_pearson_task, r_cosine_task],
                      np.corrcoef(x_pearson_task, y_pearson_task)[0, 1]))''',
         ("provided", "task-check"))
    md("**Ваш вывод:** почему для этого косинуса нужно вычесть среднее из каждого вектора? Что описывает знак полученного коэффициента? …",
       ("interpretation", "task-2"))

    theory("Задача 3. Изменились числа — изменилась ли связь?",
        "<p>Вернитесь к исходным четырём парам. Считайте, что x измерено в метрах. "
        "Во всех трёх случаях y остаётся прежним.</p>"
        "<ol><li>К каждому x прибавили 10.</li><li>Метры перевели в сантиметры: каждый x умножили на 100.</li>"
        "<li>Каждый x умножили на −1.</li></ol>"
        "<p><b>До запуска кода</b> запишите ожидаемую ковариацию и корреляцию для каждого случая. "
        "Не пересчитывайте все четыре строки: используйте то, как меняются отклонения и длины.</p>")
    code(r'''x_scale_task = np.array([1.0, 2.0, 4.0, 5.0])
y_scale_task = np.array([6.0, 4.0, 3.0, 1.0])
# TODO: Enter three predicted values in the order: shift, centimeters, sign reversal.
cov_predictions_task = ...
r_predictions_task = ...''', ("student-core", "task-3"))
    code(r'''if cov_predictions_task is Ellipsis or r_predictions_task is Ellipsis:
    print("Сначала запишите прогнозы в задаче 3.")
else:
    transformed_inputs = [x_scale_task + 10, 100 * x_scale_task, -x_scale_task]
    cov_checks = [np.cov(values, y_scale_task, ddof=1)[0, 1] for values in transformed_inputs]
    r_checks = [np.corrcoef(values, y_scale_task)[0, 1] for values in transformed_inputs]
    display(pd.DataFrame({"Преобразование": ["Прибавили 10", "Метры → сантиметры", "Умножили на −1"],
                          "Ваша ковариация": cov_predictions_task, "Ковариация NumPy": cov_checks,
                          "Ваш Пирсон": r_predictions_task, "Пирсон NumPy": r_checks}))
    print("Прогнозы ковариации подтвердились:", np.allclose(cov_predictions_task, cov_checks))
    print("Прогнозы корреляции подтвердились:", np.allclose(r_predictions_task, r_checks))''',
         ("provided", "task-check"))
    md("**Ваш вывод:** какие из этих изменений затрагивают знак связи, какие — только численную величину ковариации? Объясните через отклонения от средних. …",
       ("interpretation", "task-3"))

    theory("Задача 4. Ковариационная матрица целиком",
        "<p>Даны три наблюдения с двумя признаками:</p>"
        + eq(r"X=\begin{pmatrix}1&3\\2&5\\3&7\end{pmatrix}.",
             r"$X$ — матрица данных: строки соответствуют трём наблюдениям, столбцы — двум признакам.")
        + "<ol><li>На бумаге найдите среднее каждого столбца и запишите центрированную матрицу.</li>"
        "<li>Выполните матричное умножение, необходимое для выборочной ковариационной матрицы. "
        "Выпишите все четыре элемента и нужный делитель.</li>"
        "<li>Объясните, что означают диагональные и внедиагональные элементы.</li>"
        "<li>Найдите связь между исходными столбцами. Сравните ранги исходной и центрированной матриц.</li></ol>")
    code(r'''X_cov_task = np.array([[1.0, 3.0], [2.0, 5.0], [3.0, 7.0]])
# TODO: Reproduce the handwritten calculation using column means and matrix multiplication.
means_cov_task = ...
Xc_cov_task = ...
C_cov_task = ...
rank_raw_task = ...
rank_centered_task = ...''', ("student-core", "task-4"))
    code(r'''if any(value is Ellipsis for value in [means_cov_task, Xc_cov_task, C_cov_task,
                                          rank_raw_task, rank_centered_task]):
    print("Сначала заполните задачу 4.")
else:
    print("Средние столбцов:", means_cov_task)
    print("Центрированная матрица:\n", Xc_cov_task)
    print("Ваша ковариационная матрица:\n", C_cov_task)
    print("Совпадает с NumPy:", np.allclose(C_cov_task, np.cov(X_cov_task, rowvar=False, ddof=1)))
    print("Ранг исходной матрицы:", rank_raw_task)
    print("Ранг после центрирования:", rank_centered_task)''',
         ("provided", "task-check"))
    md("**Ваш вывод:** как записать второй исходный столбец через первый? Что произошло с постоянным слагаемым после центрирования? …",
       ("interpretation", "task-4"))

    theory("Задача 5. Спирмен с повторяющимися значениями",
        "<p>Даны пять пар. В x встречается повтор:</p>"
        "<table><thead><tr><th>Наблюдение</th><th>x</th><th>y</th></tr></thead><tbody>"
        "<tr><td>1</td><td>10</td><td>1</td></tr><tr><td>2</td><td>20</td><td>4</td></tr>"
        "<tr><td>3</td><td>20</td><td>2</td></tr><tr><td>4</td><td>40</td><td>5</td></tr>"
        "<tr><td>5</td><td>50</td><td>3</td></tr></tbody></table>"
        "<ol><li>На бумаге присвойте ранги отдельно значениям x и y. Наименьшее значение получает ранг 1; "
        "одинаковым значениям присвойте среднее занятых ими мест.</li>"
        "<li>Запишите ранги в <b>исходном порядке наблюдений</b>, чтобы пары не перемешались.</li>"
        "<li>Вычислите корреляцию Пирсона между рангами: это коэффициент Спирмена.</li></ol>"
        + box("Повторяющиеся значения", "После усреднения занятых мест ранги могут быть дробными. "
              "Это нормально: вычисляйте корреляцию между ними как между обычными числами."))
    code(r'''x_rank_task = np.array([10.0, 20.0, 20.0, 40.0, 50.0])
y_rank_task = np.array([1.0, 4.0, 2.0, 5.0, 3.0])
# TODO: Enter your handwritten ranks, then compute Pearson correlation of the ranks.
ranks_x_task = ...
ranks_y_task = ...
rho_task = ...''', ("student-core", "task-5"))
    code(r'''if any(value is Ellipsis for value in [ranks_x_task, ranks_y_task, rho_task]):
    print("Сначала заполните задачу 5.")
else:
    display(pd.DataFrame({"x": x_rank_task, "y": y_rank_task,
                          "Ваш ранг x": ranks_x_task, "Ваш ранг y": ranks_y_task}))
    correct_ranks_x = pd.Series(x_rank_task).rank(method="average").to_numpy()
    correct_ranks_y = pd.Series(y_rank_task).rank(method="average").to_numpy()
    print("Ранги x верны:", np.allclose(ranks_x_task, correct_ranks_x))
    print("Ранги y верны:", np.allclose(ranks_y_task, correct_ranks_y))
    print("Ваш коэффициент Спирмена:", rho_task)
    print("Проверка коэффициента:",
          np.allclose(rho_task, np.corrcoef(correct_ranks_x, correct_ranks_y)[0, 1]))''',
         ("provided", "task-check"))
    md("**Ваш вывод:** почему двум одинаковым значениям нельзя присвоить разные ранги по порядку строк? Почему нельзя независимо отсортировать оба столбца перед расчётом корреляции? …",
       ("interpretation", "task-5"))

    md("## Дополнительные задачи")
    md("Здесь главное — сопоставить вычисления с графиком или со связью между столбцами. "
       "Сначала сформулируйте ожидание, затем проверьте его кодом.")

    theory("Задача 6. Что показывают три столбца вместе",
        "<p>Ниже четыре наблюдения с тремя признаками. Найдите соотношение между всеми тремя столбцами. "
        "Затем вычислите ранг и матрицу попарных корреляций.</p>"
        "<p>После этого увеличьте последнее значение третьего столбца на 0.01. "
        "До расчёта предположите, что произойдёт с рангом и насколько изменятся корреляции. "
        "Проверьте оба предположения.</p>")
    code(r'''X_three_task = np.array([[-1.0, -1.0, -2.0],
                         [-1.0,  1.0,  0.0],
                         [ 1.0, -1.0,  0.0],
                         [ 1.0,  1.0,  2.0]])
X_changed_task = X_three_task.copy()
X_changed_task[-1, 2] += 0.01
# TODO: Compare exact rank and pairwise correlations before and after the change.
rank_three_task = ...
R_three_task = ...
rank_changed_task = ...
R_changed_task = ...''', ("student-core", "task-6", "optional"))
    code(r'''if any(value is Ellipsis for value in [rank_three_task, R_three_task,
                                          rank_changed_task, R_changed_task]):
    print("Дополнительная задача 6 пока не заполнена.")
else:
    print("Ранги до и после изменения:", rank_three_task, rank_changed_task)
    print("Корреляции до изменения:\n", R_three_task)
    print("Корреляции после изменения:\n", R_changed_task)
    print("Наибольшее изменение корреляции:", np.max(np.abs(R_changed_task - R_three_task)))''',
         ("provided", "task-check", "optional"))
    md("**Ваш вывод:** достаточно ли искать только пары с корреляцией ±1, чтобы обнаружить любую зависимость столбцов? "
       "Чем точная зависимость в этом примере отличается от приблизительной? …",
       ("interpretation", "task-6", "optional"))

    theory("Задача 7. Парабола и новый признак",
        "<p>Даны пять пар. На бумаге найдите средние, произведения отклонений и коэффициент Пирсона. "
        "Затем замените x новым признаком — квадратом x — и снова вычислите корреляцию с y.</p>"
        + eq(r"x=(-2,-1,0,1,2),\qquad y=(4,1,0,1,4),\qquad u_i=x_i^2.",
             r"$x,y$ — пять пар наблюдений; $x_i$ — значение x в строке $i$; "
             r"$u_i$ — новое значение в той же строке, квадрат $x_i$.")
        + "<p>Вычислите также ранг матрицы из двух <b>центрированных</b> столбцов u и y. "
        "После расчётов рассмотрите два графика.</p>")
    code(r'''x_curve_task = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
y_curve_task = np.array([4.0, 1.0, 0.0, 1.0, 4.0])
# TODO: Compute the first correlation from centered values; then transform x.
r_curve_task = ...
u_curve_task = ...
r_transformed_task = ...
rank_curve_task = ...''', ("student-core", "task-7", "optional"))
    code(r'''if any(value is Ellipsis for value in [r_curve_task, u_curve_task,
                                          r_transformed_task, rank_curve_task]):
    print("Дополнительная задача 7 пока не заполнена.")
else:
    print("Пирсон до преобразования:", r_curve_task)
    print("Пирсон после преобразования:", r_transformed_task)
    print("Ранг двух центрированных столбцов после преобразования:", rank_curve_task)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    axes[0].scatter(x_curve_task, y_curve_task, s=60)
    axes[0].set(xlabel="x", ylabel="y", title="Исходные пары")
    axes[1].scatter(u_curve_task, y_curve_task, s=60)
    axes[1].set(xlabel="Новый признак u", ylabel="y", title="После преобразования x")
    for ax in axes:
        ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.show()''', ("provided", "task-check", "optional"))
    md("**Ваш вывод:** что описывал первый коэффициент и чего он не показывал? "
       "Сколько разных точек видно справа и почему их число отличается от числа наблюдений? …",
       ("interpretation", "task-7", "optional"))

    theory("Задача 8. Синтетические квартиры: выберите представление признака",
        "<p>Ниже восемь <b>синтетических</b> квартир. Площадь измерена в квадратных метрах, "
        "цена — в тысячах долларов. Числа придуманы для упражнения; это не данные рынка.</p>"
        "<ol><li>Нарисуйте от руки примерное расположение точек и предположите форму связи.</li>"
        "<li>Выберите преобразование площади из изученных в занятии, которое имеет смысл для этой формы. "
        "Запишите, что означает новый признак и в каких единицах он измеряется.</li>"
        "<li>Вычислите корреляцию цены с исходной площадью и с новым признаком. "
        "Сопоставьте оба числа с графиками.</li></ol>"
        + box("Объяснение важнее большего числа", "Обоснуйте выбор формы по расположению точек. "
              "Высокая корреляция на этих восьми наблюдениях сама по себе не проверяет прогноз цены новой квартиры."))
    code(r'''area_flat_task = np.array([20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0])
price_flat_task = np.array([30.0, 40.0, 54.0, 68.0, 86.0, 107.0, 130.0, 154.0])
display(pd.DataFrame({"Площадь, м²": area_flat_task, "Цена, тыс. долларов": price_flat_task}))
# TODO: Choose a feature transformation, name it, and compare the two correlations.
feature_flat_task = ...
feature_label_task = ...
r_area_task = ...
r_feature_task = ...''', ("student-core", "task-8", "optional"))
    code(r'''if any(value is Ellipsis for value in [feature_flat_task, feature_label_task,
                                          r_area_task, r_feature_task]):
    print("Дополнительная задача 8 пока не заполнена.")
else:
    print("Пирсон для исходной площади:", r_area_task)
    print("Пирсон для выбранного признака:", r_feature_task)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    axes[0].scatter(area_flat_task, price_flat_task, s=55)
    axes[0].set(xlabel="Площадь, м²", ylabel="Цена, тыс. долларов", title="Исходный признак")
    axes[1].scatter(feature_flat_task, price_flat_task, s=55)
    axes[1].set(xlabel=feature_label_task, ylabel="Цена, тыс. долларов", title="Выбранное преобразование")
    for ax in axes:
        ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.show()''', ("provided", "task-check", "optional"))
    md("**Ваш вывод:** какое преобразование вы выбрали и почему? Что стало проще увидеть на втором графике? "
       "Каких данных не хватает, чтобы говорить о реальных ценах и качестве прогноза? …",
       ("interpretation", "task-8", "optional"))
