"""
fiche_recap_widget.py

Reproduit visuellement la "Fiche Recap" de l'outil Prep@udit d'origine :

- Tableau "Nature des Engagements" (Utilisations + Pourcentage)
- Tableau "Nature des Impayés" (Montant)
- En-têtes rouges
- Lignes de total en jaune pâle et en gras
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame
)

from PyQt6.QtCore import Qt


HEADER_BG = "#c0392b"
HEADER_TEXT = "#ffffff"
CREAM_TOTAL = "#fdf0c8"
BORDER = "#999999"
DARK = "#2d2d2d"


def _cell(
    text,
    bold=False,
    bg=None,
    align=Qt.AlignmentFlag.AlignLeft,
    color=DARK
):
    lbl = QLabel(str(text))

    weight = "bold" if bold else "normal"

    style = (
        f"color: {color}; "
        f"font-weight: {weight}; "
        f"padding: 4px 8px; "
        f"border: 1px solid {BORDER};"
    )

    if bg:
        style += f" background-color: {bg};"
    else:
        style += " background-color: white;"

    lbl.setStyleSheet(style)

    lbl.setAlignment(
        align | Qt.AlignmentFlag.AlignVCenter
    )

    return lbl


class FicheRecapWidget(QWidget):

    def __init__(
        self,
        fiche_recap: dict,
        date_execution: datetime = None
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setSpacing(20)
        layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        # ==================================================
        # DATE D'EXECUTION
        # ==================================================

        if date_execution:

            date_row = QHBoxLayout()

            date_row.addStretch()

            date_label = QLabel(
                f"Date   {date_execution:%d/%m/%Y}"
            )

            date_label.setStyleSheet(
                f"""
                color: {DARK};
                font-style: italic;
                font-weight: bold;
                """
            )

            date_row.addWidget(date_label)

            layout.addLayout(date_row)

        # ==================================================
        # NATURE DES ENGAGEMENTS
        # ==================================================

        if "nature" in fiche_recap:

            layout.addWidget(
                self._build_nature_table(
                    fiche_recap["nature"]
                )
            )

        # ==================================================
        # NATURE DES IMPAYES
        # ==================================================

        if "impayes" in fiche_recap:

            layout.addWidget(
                self._build_impayes_table(
                    fiche_recap["impayes"]
                )
            )

        layout.addStretch()

    # ======================================================
    # FRAME
    # ======================================================

    def _grid_frame(self):

        frame = QFrame()

        frame.setStyleSheet(
            "background: white;"
        )

        return frame

    # ======================================================
    # TABLE NATURE DES ENGAGEMENTS
    # ======================================================

    def _build_nature_table(self, rows):

        container = QVBoxLayout()

        wrapper = QWidget()

        wrapper.setLayout(container)

        container.setSpacing(0)

        # --------------------------------------------------
        # TITRE
        # --------------------------------------------------

        title = _cell(
            "NATURE DES ENGAGEMENTS",
            bold=True,
            bg=HEADER_BG,
            color=HEADER_TEXT,
            align=Qt.AlignmentFlag.AlignCenter
        )

        title_row = QHBoxLayout()

        title_row.setSpacing(0)

        title_row.addWidget(
            title,
            2
        )

        container.addLayout(
            title_row
        )

        # --------------------------------------------------
        # EN-TETES
        # --------------------------------------------------

        header_row = QHBoxLayout()

        header_row.setSpacing(0)

        header_row.addWidget(
            _cell(
                "NATURE",
                bold=True,
                bg=HEADER_BG,
                color=HEADER_TEXT,
                align=Qt.AlignmentFlag.AlignCenter
            ),
            1
        )

        header_row.addWidget(
            _cell(
                "UTILISATIONS",
                bold=True,
                bg=HEADER_BG,
                color=HEADER_TEXT,
                align=Qt.AlignmentFlag.AlignCenter
            ),
            1
        )

        header_row.addWidget(
            _cell(
                "POURCENTAGE %",
                bold=True,
                bg=HEADER_BG,
                color=HEADER_TEXT,
                align=Qt.AlignmentFlag.AlignCenter
            ),
            1
        )

        container.addLayout(
            header_row
        )

        # --------------------------------------------------
        # LIGNES
        # --------------------------------------------------

        totals = {
            "ENGAGEMENTS GLOBALAUX HORS CONTENTIEUX",
            "ENGAGEMENTS GLOBALAUX"
        }

        for label, montant, pct in rows:

            is_total = (
                label in totals
            )

            bg = (
                CREAM_TOTAL
                if is_total
                else None
            )

            row = QHBoxLayout()

            row.setSpacing(0)

            # Nature
            row.addWidget(
                _cell(
                    label,
                    bold=is_total,
                    bg=bg
                ),
                1
            )

            # Montant
            montant_formate = (
                f"{float(montant):,.0f}"
                .replace(",", " ")
            )

            row.addWidget(
                _cell(
                    montant_formate,
                    bold=is_total,
                    bg=bg,
                    align=Qt.AlignmentFlag.AlignRight
                ),
                1
            )

            # Pourcentage
            pct_formate = (
                f"{float(pct):.2f}%"
                .replace(".", ",")
            )

            row.addWidget(
                _cell(
                    pct_formate,
                    bold=is_total,
                    bg=bg,
                    align=Qt.AlignmentFlag.AlignRight
                ),
                1
            )

            container.addLayout(
                row
            )

        return wrapper

    # ======================================================
    # TABLE NATURE DES IMPAYES
    # ======================================================

    def _build_impayes_table(self, rows):

        container = QVBoxLayout()

        wrapper = QWidget()

        wrapper.setLayout(container)

        container.setSpacing(0)

        # --------------------------------------------------
        # TITRE
        # --------------------------------------------------

        title = _cell(
            "NATURE DES IMPAYES",
            bold=True,
            bg=HEADER_BG,
            color=HEADER_TEXT,
            align=Qt.AlignmentFlag.AlignCenter
        )

        title_row = QHBoxLayout()

        title_row.setSpacing(0)

        title_row.addWidget(
            title,
            2
        )

        container.addLayout(
            title_row
        )

        # --------------------------------------------------
        # EN-TETES
        # --------------------------------------------------

        header_row = QHBoxLayout()

        header_row.setSpacing(0)

        header_row.addWidget(
            _cell(
                "NATURE",
                bold=True,
                bg=HEADER_BG,
                color=HEADER_TEXT,
                align=Qt.AlignmentFlag.AlignCenter
            ),
            1
        )

        header_row.addWidget(
            _cell(
                "MONTANT",
                bold=True,
                bg=HEADER_BG,
                color=HEADER_TEXT,
                align=Qt.AlignmentFlag.AlignCenter
            ),
            1
        )

        container.addLayout(
            header_row
        )

        # --------------------------------------------------
        # LIGNES
        # --------------------------------------------------

        for label, montant in rows:

            is_total = (
                label == "TOTAL"
            )

            bg = (
                CREAM_TOTAL
                if is_total
                else None
            )

            row = QHBoxLayout()

            row.setSpacing(0)

            align_label = (
                Qt.AlignmentFlag.AlignCenter
                if is_total
                else Qt.AlignmentFlag.AlignLeft
            )

            row.addWidget(
                _cell(
                    label,
                    bold=is_total,
                    bg=bg,
                    align=align_label
                ),
                1
            )

            montant_formate = (
                f"{float(montant):,.0f}"
                .replace(",", " ")
            )

            row.addWidget(
                _cell(
                    montant_formate,
                    bold=is_total,
                    bg=bg,
                    align=Qt.AlignmentFlag.AlignRight
                ),
                1
            )

            container.addLayout(
                row
            )

        return wrapper