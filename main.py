import sys
from PyQt6.QtWidgets import QApplication
from electre_model import DecisionModel
from data_provider import get_variant5_data
from ui import ElectreApp


def main():
    app = QApplication(sys.argv)

    alts, crit_names, crit_types, raw_matrix, expert_scores = get_variant5_data()
    model = DecisionModel(alts, crit_names, crit_types, raw_matrix)

    window = ElectreApp(model, expert_scores)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()