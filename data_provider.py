def get_variant5_data():
    alternatives = ["M1", "M2", "M3", "M4", "M5", "M6"]
    criteria_names = [
        "Близость к сырью",
        "Близость к клиентам",
        "Затраты на подготовку"
    ]
    criteria_types = ['max', 'max', 'min']

    # Числовые эквиваленты шкалы Харрингтона нормированы
    raw_matrix = [
        [0.90, 0.30, 2.5],
        [0.75, 0.50, 4.0],
        [0.30, 0.75, 3.0],
        [0.90, 0.15, 2.0],
        [0.68, 0.30, 3.0],
        [0.50, 0.90, 3.5]
    ]

    expert_ratings = [
        [8, 5, 10],
        [10, 3, 8]
    ]

    return alternatives, criteria_names, criteria_types, raw_matrix, expert_ratings