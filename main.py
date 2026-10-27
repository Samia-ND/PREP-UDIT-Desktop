# ============================================================
# main.py
# Prep@udit Desktop
# ============================================================

import sys
import os

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QStackedWidget,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QDialog,
    QProgressBar,
)

from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor, QPixmap, QFont


# ============================================================
# IMPORTS DES ÉCRANS
# ============================================================

from engagement_screen import EngagementScreen
from garantie_screen import GarantieScreen


# ============================================================
# DOSSIER APPLICATION
# ============================================================

if getattr(sys, "frozen", False):

    BASE_DIR = os.path.dirname(
        sys.executable
    )

    RESOURCE_DIR = os.path.join(
        BASE_DIR,
        "_internal"
    )

else:

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    RESOURCE_DIR = BASE_DIR


LOGO_PATH_PNG = os.path.join(
    RESOURCE_DIR,
    "logo.png"
)

LOGO_PATH_JPG = os.path.join(
    RESOURCE_DIR,
    "logo.jpg"
)
# ============================================================
# COULEURS
# ============================================================

SALMON_BG = "#f6c9a8"
ORANGE = "#e67e22"
RED = "#c0392b"
GREEN = "#2d5a2d"
DARK = "#2d2d2d"
WHITE = "#ffffff"
GOLD = "#C67D0A"
BORDER_BROWN = "#8C4318"

CARD_BG = "rgba(255, 255, 255, 0.75)"
CARD_BORDER = "rgba(255, 255, 255, 0.9)"


# ============================================================
# FENÊTRE DE PROGRESSION
# ============================================================
# IMPORTANT :
# Cette fenêtre appartient maintenant à main.py.
#
# Elle est utilisée pour les modules qui ont besoin
# d'afficher une progression pendant leur traitement.
# ============================================================

class ProgressDialog(QDialog):

    def __init__(
        self,
        parent=None,
        title="Traitement en cours..."
    ):

        super().__init__(parent)

        # ----------------------------------------------------
        # TAILLE
        # ----------------------------------------------------

        self.setFixedSize(
            450,
            160
        )

        # ----------------------------------------------------
        # TITRE WINDOWS
        # ----------------------------------------------------

        self.setWindowTitle(
            "Traitement en cours"
        )

        self.setWindowModality(
            Qt.WindowModality.ApplicationModal
        )

        # ----------------------------------------------------
        # STYLE
        # ----------------------------------------------------

        self.setStyleSheet(
            """
            QDialog {
                background-color: white;
                border: 2px solid #8C4318;
                border-radius: 8px;
            }

            QLabel {
                background: transparent;
                color: #2d2d2d;
            }

            QProgressBar {
                border: 1px solid #999999;
                border-radius: 7px;
                background-color: #eeeeee;
                height: 32px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background-color: #c0392b;
                border-radius: 6px;
            }
            """
        )

        # ----------------------------------------------------
        # LAYOUT
        # ----------------------------------------------------

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            35,
            25,
            35,
            25
        )

        layout.setSpacing(
            12
        )

        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        self.title_label = QLabel(
            title
        )

        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.title_label.setFont(
            QFont(
                "Arial",
                15,
                QFont.Weight.Bold
            )
        )

        # ----------------------------------------------------
        # BARRE
        # ----------------------------------------------------

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setTextVisible(
            True
        )

        # ----------------------------------------------------
        # LIGNES
        # ----------------------------------------------------

        self.lines_label = QLabel(
            "> Lignes traitées : 0 / 0"
        )

        self.lines_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.lines_label.setFont(
            QFont(
                "Arial",
                11
            )
        )

        # ----------------------------------------------------
        # PATIENTER
        # ----------------------------------------------------

        self.wait_label = QLabel(
            "Veuillez patienter..."
        )

        self.wait_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.wait_label.setFont(
            QFont(
                "Arial",
                11,
                QFont.Weight.Bold
            )
        )

        self.wait_label.setStyleSheet(
            """
            color: #555555;
            """
        )

        # ----------------------------------------------------
        # AJOUT
        # ----------------------------------------------------

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.progress_bar
        )

        layout.addWidget(
            self.lines_label
        )

        layout.addWidget(
            self.wait_label
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update_progress(
        self,
        percent,
        processed=0,
        total=0
    ):

        percent = max(
            0,
            min(
                100,
                int(percent)
            )
        )

        self.progress_bar.setValue(
            percent
        )

        if total:

            self.lines_label.setText(
                f"> Lignes traitées : "
                f"{processed:,} / {total:,}"
                .replace(
                    ",",
                    " "
                )
            )

        else:

            self.lines_label.setText(
                f"> Lignes traitées : "
                f"{processed:,}"
                .replace(
                    ",",
                    " "
                )
            )

        QApplication.processEvents()


# ============================================================
# MODULES DU MENU
# ============================================================

SECTIONS = [

    (
        "Gestion & Fichiers",
        [
            ("Chercher PCI", "🔍"),
            ("Extrait des Comptes", "📄"),
            ("Modification Adresse", "📍"),
            ("Fermetures de Comptes", "🔒"),
            ("RDTI", "📊"),
        ],
    ),

    (
        "Opérations Comptables",
        [
            ("Journal des Opérations", "📓"),
            ("Opérations Annulées", "❌"),
            ("Seuils des Encaisses", "💰"),
            ("Listing Comptable", "📋"),
            ("Brouillard Comptable", "🌫️"),
        ],
    ),

    (
        "Rapports & Engagements",
        [
            ("Etat des Comptes (Sans Thématiques)", "📂"),
            ("Etat des Comptes (Avec Thématiques)", "📁"),
            ("Cautions", "🛡️"),
            ("Etat des Engagements", "📈"),
            ("Garanties", "📜"),
        ],
    ),
]


# ============================================================
# CARTE MODULE
# ============================================================

class ModuleCard(QFrame):

    def __init__(
        self,
        title,
        icon_symbol,
        on_click
    ):

        super().__init__()

        self.title_text = title
        self.on_click = on_click

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            12,
            9,
            12,
            9
        )

        # ----------------------------------------------------
        # ICONE
        # ----------------------------------------------------

        icon_lbl = QLabel(
            icon_symbol
        )

        icon_lbl.setStyleSheet(
            """
            font-size: 15px;
            background: transparent;
            border: none;
            """
        )

        # ----------------------------------------------------
        # TEXTE
        # ----------------------------------------------------

        text_lbl = QLabel(
            title
        )

        text_lbl.setStyleSheet(
            f"""
            font-size: 12px;
            font-weight: 600;
            color: {DARK};
            background: transparent;
            border: none;
            """
        )

        # ----------------------------------------------------
        # FLECHE
        # ----------------------------------------------------

        arrow_lbl = QLabel(
            "→"
        )

        arrow_lbl.setStyleSheet(
            f"""
            color: {GOLD};
            font-weight: bold;
            background: transparent;
            border: none;
            """
        )

        layout.addWidget(
            icon_lbl
        )

        layout.addWidget(
            text_lbl,
            1
        )

        layout.addWidget(
            arrow_lbl
        )

        # ----------------------------------------------------
        # STYLE
        # ----------------------------------------------------

        self.setStyleSheet(
            f"""
            ModuleCard {{
                background-color:
                    rgba(255, 255, 255, 0.65);
                border: 1px solid transparent;
                border-radius: 8px;
            }}

            ModuleCard:hover {{
                background-color: #FFFFFF;
                border: 1px solid {GOLD};
            }}
            """
        )

    # ========================================================
    # CLICK
    # ========================================================

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.MouseButton.LeftButton:

            self.on_click(
                self.title_text
            )

        super().mousePressEvent(
            event
        )


# ============================================================
# ÉCRAN MENU
# ============================================================

class MenuScreen(QWidget):

    def __init__(
        self,
        on_select
    ):

        super().__init__()

        self.on_select = on_select

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {SALMON_BG};
            }}
            """
        )

        outer = QVBoxLayout(
            self
        )

        outer.setContentsMargins(
            0,
            0,
            0,
            0
        )

        outer.setSpacing(
            0
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        outer.addWidget(
            self._build_header()
        )

        # ----------------------------------------------------
        # CORPS
        # ----------------------------------------------------

        body_widget = QWidget()

        body_layout = QVBoxLayout(
            body_widget
        )

        body_layout.setContentsMargins(
            35,
            20,
            35,
            20
        )

        body_layout.setSpacing(
            20
        )

        body_layout.addLayout(
            self._build_file_toolbar()
        )

        body_layout.addWidget(
            self._build_modules_panel(),
            1
        )

        outer.addWidget(
            body_widget,
            1
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        outer.addWidget(
            self._build_footer()
        )

    # ========================================================
    # HEADER
    # ========================================================

    def _build_header(self):

        header_wrapper = QFrame()

        header_wrapper.setFixedHeight(
            100
        )

        header_wrapper.setStyleSheet(
            """
            QFrame {
                background-color: #F8CBA8;
                border: none;
            }
            """
        )

        wrapper_layout = QHBoxLayout(
            header_wrapper
        )

        wrapper_layout.setContentsMargins(
            12,
            6,
            12,
            6
        )

        inner_box = QFrame()

        inner_box.setStyleSheet(
            f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 2px solid {BORDER_BROWN};
                border-radius: 0px;
            }}
            """
        )

        inner_layout = QHBoxLayout(
            inner_box
        )

        inner_layout.setContentsMargins(
            15,
            4,
            15,
            4
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo_lbl = QLabel()

        logo_lbl.setStyleSheet(
            """
            border: none;
            background: transparent;
            """
        )

        if os.path.exists(
            LOGO_PATH_PNG
        ):

            logo_lbl.setPixmap(
                QPixmap(
                    LOGO_PATH_PNG
                ).scaledToHeight(
                    70,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        elif os.path.exists(
            LOGO_PATH_JPG
        ):

            logo_lbl.setPixmap(
                QPixmap(
                    LOGO_PATH_JPG
                ).scaledToHeight(
                    70,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        else:

            logo_lbl.setText(
                """
                <span style='color:#E67E22;
                font-weight:bold;
                font-size:18px;'>
                Attijariwafa
                </span>

                <span style='color:#333;'>
                bank
                </span>
                """
            )

        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        title_lbl = QLabel(
            """
            <div style="text-align: center;">

            <span style="
            color:#F38220;
            font-family: Georgia, serif;
            font-size:28px;
            font-style:italic;
            font-weight:bold;">
            Prep
            </span>

            <span style="
            color:#6B7A82;
            font-family: Times New Roman, serif;
            font-size:24px;">
            @
            </span>

            <span style="
            color:#D31B1B;
            font-family: Georgia, serif;
            font-size:28px;
            font-style:italic;
            font-weight:bold;">
            udit
            </span>

            <br>

            <span style="
            color:#1B4D3E;
            font-family: Georgia, serif;
            font-size:13px;
            font-style:italic;
            font-weight:bold;
            letter-spacing:1px;">
            Audit Général Groupe
            </span>

            </div>
            """
        )

        title_lbl.setStyleSheet(
            """
            border: none;
            background: transparent;
            """
        )

        title_lbl.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        info_lbl = QLabel(
            """
            <div style="
            text-align: right;
            color:#D97724;
            font-family: Georgia, serif;
            font-style:italic;
            font-size:11px;">

            Système d'information<br>

            <span style='font-size:11px;'>
            V1_desktop
            </span>

            </div>
            """
        )

        info_lbl.setStyleSheet(
            """
            border: none;
            background: transparent;
            """
        )

        info_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight
            |
            Qt.AlignmentFlag.AlignVCenter
        )

        inner_layout.addWidget(
            logo_lbl
        )

        inner_layout.addStretch()

        inner_layout.addWidget(
            title_lbl
        )

        inner_layout.addStretch()

        inner_layout.addWidget(
            info_lbl
        )

        wrapper_layout.addWidget(
            inner_box
        )

        return header_wrapper

    # ========================================================
    # BARRE FICHIER
    # ========================================================

    def _build_file_toolbar(self):

        toolbar = QHBoxLayout()

        toolbar.setSpacing(
            12
        )

        file_lbl = QLabel(
            "Fichier Cible :"
        )

        file_lbl.setStyleSheet(
            f"""
            font-size: 13px;
            font-weight: 700;
            color: {DARK};
            background: transparent;
            """
        )

        self.filename_input = QLineEdit(
            "Sélectionnez un module pour lancer un traitement..."
        )

        self.filename_input.setReadOnly(
            True
        )

        self.filename_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color:
                    rgba(255,255,255,0.9);
                border: 1px solid #E0C0B0;
                border-radius: 6px;
                padding: 8px 12px;
                color: {DARK};
                font-weight: 600;
                font-size: 12px;
            }}
            """
        )

        toolbar.addWidget(
            file_lbl
        )

        toolbar.addWidget(
            self.filename_input,
            1
        )

        return toolbar

    # ========================================================
    # PANNEAU MODULES
    # ========================================================

    def _build_modules_panel(self):

        container = QFrame()

        container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 14px;
            }}
            """
        )

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(
            20
        )

        shadow.setColor(
            QColor(
                0,
                0,
                0,
                15
            )
        )

        shadow.setYOffset(
            4
        )

        container.setGraphicsEffect(
            shadow
        )

        grid_layout = QHBoxLayout(
            container
        )

        grid_layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        grid_layout.setSpacing(
            25
        )

        for sec_title, items in SECTIONS:

            col = QVBoxLayout()

            col.setSpacing(
                10
            )

            title_lbl = QLabel(
                sec_title
            )

            title_lbl.setStyleSheet(
                f"""
                font-size: 13px;
                font-weight: 700;
                color: {DARK};
                border-bottom: 2px solid {GOLD};
                padding-bottom: 4px;
                background: transparent;
                """
            )

            col.addWidget(
                title_lbl
            )

            for name, icon in items:

                col.addWidget(
                    ModuleCard(
                        name,
                        icon,
                        self.on_select
                    )
                )

            col.addStretch()

            grid_layout.addLayout(
                col,
                1
            )

        return container

    # ========================================================
    # FOOTER
    # ========================================================

    def _build_footer(self):

        footer = QFrame()

        footer.setFixedHeight(
            35
        )

        footer.setStyleSheet(
            """
            background-color:
            rgba(255,255,255,0.6);
            """
        )

        layout = QHBoxLayout(
            footer
        )

        layout.setContentsMargins(
            30,
            0,
            30,
            0
        )

        status_lbl = QLabel(
            "● Système d'information opérationnel"
        )

        status_lbl.setStyleSheet(
            f"""
            color: {GOLD};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            """
        )

        time_str = (
            f"{QDate.currentDate().toString('dd/MM/yyyy')}"
            f" — "
            f"{QTime.currentTime().toString('hh:mm')}"
        )

        time_lbl = QLabel(
            time_str
        )

        time_lbl.setStyleSheet(
            """
            color: #7A655C;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            """
        )

        layout.addWidget(
            status_lbl
        )

        layout.addStretch()

        layout.addWidget(
            time_lbl
        )

        return footer


# ============================================================
# FENÊTRE PRINCIPALE
# ============================================================

class PrepDesktopMenuDemo(QMainWindow):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # FENÊTRE
        # ----------------------------------------------------

        self.setWindowTitle(
            "Prep@udit Desktop"
        )

        self.resize(
            1300,
            750
        )

        # ----------------------------------------------------
        # STACK
        # ----------------------------------------------------

        self.stack = QStackedWidget()

        self.setCentralWidget(
            self.stack
        )

        # ----------------------------------------------------
        # MENU
        # ----------------------------------------------------

        self.menu_screen = MenuScreen(
            on_select=self.handle_select
        )

        self.stack.addWidget(
            self.menu_screen
        )

        # ----------------------------------------------------
        # ENGAGEMENTS
        # ----------------------------------------------------

        self.engagement_screen = EngagementScreen(
            on_back=self.show_menu
        )

        self.engagement_screen.on_results_ready = (
            self.show_engagement_results
        )

        self.stack.addWidget(
            self.engagement_screen
        )

        # ----------------------------------------------------
        # GARANTIES
        # ----------------------------------------------------

        self.garantie_screen = GarantieScreen(
            on_back=self.show_menu
        )

        self.stack.addWidget(
            self.garantie_screen
        )

        # ====================================================
        # PROGRESSION GARANTIES
        # ====================================================
        #
        # La fenêtre est créée par MAIN.
        #
        # On ne touche pas au traitement de
        # garantie_screen.py.
        #
        # On remplace uniquement ses méthodes de progression
        # afin qu'elles utilisent la fenêtre appartenant à main.
        # ====================================================

        self.garantie_progress_dialog = None

        self._connect_garantie_progress()

        # ----------------------------------------------------
        # ÉTAT INITIAL
        # ----------------------------------------------------

        self.stack.setCurrentWidget(
            self.menu_screen
        )

        self.statusBar().showMessage(
            "Prêt"
        )

        self.statusBar().setStyleSheet(
            f"""
            background-color: {SALMON_BG};
            color: {DARK};
            """
        )

    # ========================================================
    # CONNEXION PROGRESSION GARANTIES
    # ========================================================

    def _connect_garantie_progress(self):

        # ----------------------------------------------------
        # On remplace les méthodes du screen
        # ----------------------------------------------------

        self.garantie_screen._show_progress = (
            self._garantie_show_progress
        )

        self.garantie_screen._set_progress = (
            self._garantie_set_progress
        )

        self.garantie_screen._close_progress = (
            self._garantie_close_progress
        )

    # ========================================================
    # AFFICHER PROGRESSION GARANTIES
    # ========================================================

    def _garantie_show_progress(self):

        # ----------------------------------------------------
        # Si une ancienne fenêtre existe
        # ----------------------------------------------------

        if self.garantie_progress_dialog is not None:

            self.garantie_progress_dialog.close()

            self.garantie_progress_dialog.deleteLater()

            self.garantie_progress_dialog = None

        # ----------------------------------------------------
        # Création dans MAIN
        # ----------------------------------------------------

        self.garantie_progress_dialog = ProgressDialog(
            self,
            "Traitement des garanties en cours..."
        )

        # ----------------------------------------------------
        # Position centrale par rapport à la fenêtre principale
        # ----------------------------------------------------

        self.garantie_progress_dialog.adjustSize()

        main_geometry = self.geometry()

        dialog_geometry = (
            self.garantie_progress_dialog.geometry()
        )

        x = (
            main_geometry.x()
            +
            (
                main_geometry.width()
                -
                dialog_geometry.width()
            )
            // 2
        )

        y = (
            main_geometry.y()
            +
            (
                main_geometry.height()
                -
                dialog_geometry.height()
            )
            // 2
        )

        self.garantie_progress_dialog.move(
            x,
            y
        )

        # ----------------------------------------------------
        # Affichage
        # ----------------------------------------------------

        self.garantie_progress_dialog.show()

        self.garantie_progress_dialog.raise_()

        self.garantie_progress_dialog.activateWindow()

        QApplication.processEvents()

    # ========================================================
    # UPDATE PROGRESSION GARANTIES
    # ========================================================

    def _garantie_set_progress(
        self,
        percent,
        processed=0,
        total=0
    ):

        if self.garantie_progress_dialog is None:

            return

        self.garantie_progress_dialog.update_progress(
            percent,
            processed,
            total
        )

    # ========================================================
    # FERMER PROGRESSION GARANTIES
    # ========================================================

    def _garantie_close_progress(self):

        if self.garantie_progress_dialog is None:

            return

        self.garantie_progress_dialog.close()

        self.garantie_progress_dialog.deleteLater()

        self.garantie_progress_dialog = None

        QApplication.processEvents()

    # ========================================================
    # SÉLECTION MODULE
    # ========================================================

    def handle_select(
        self,
        name
    ):

        # ====================================================
        # ÉTAT DES ENGAGEMENTS
        # ====================================================

        if name == "Etat des Engagements":

            self.menu_screen.filename_input.setText(
                "Etat des Engagements"
            )

            try:

                success = (
                    self.engagement_screen.import_csv()
                )

            except AttributeError:

                QMessageBox.warning(
                    self,
                    "Erreur",
                    "La méthode import_csv() "
                    "n'existe pas dans "
                    "engagement_screen.py."
                )

                return

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors du traitement :\n\n{e}"
                )

                return

            # ------------------------------------------------
            # On ne change pas de page ici.
            # ------------------------------------------------

            if success:

                self.statusBar().showMessage(
                    "Traitement : "
                    "État des Engagements en cours..."
                )

            return

        # ====================================================
        # GARANTIES
        # ====================================================

        if name == "Garanties":

            self.menu_screen.filename_input.setText(
                "Garanties"
            )

            try:

                success = (
                    self.garantie_screen.import_csv()
                )

            except AttributeError:

                QMessageBox.warning(
                    self,
                    "Erreur",
                    "La méthode import_csv() "
                    "n'existe pas dans "
                    "garantie_screen.py."
                )

                return

            except Exception as e:

                # ------------------------------------------------
                # Si une erreur survient, fermer la progression
                # ------------------------------------------------

                self._garantie_close_progress()

                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors du traitement :\n\n{e}"
                )

                return

            # ------------------------------------------------
            # IMPORTANT
            #
            # Le traitement de Garantie est terminé ici.
            #
            # On affiche maintenant la page Garanties.
            # ------------------------------------------------

            if success:

                self.stack.setCurrentWidget(
                    self.garantie_screen
                )

                self.statusBar().showMessage(
                    "Module : Garanties"
                )

            return

        # ====================================================
        # AUTRES MODULES
        # ====================================================

        self.menu_screen.filename_input.setText(
            name.replace(
                " ",
                "_"
            )
        )

        self.statusBar().showMessage(
            f"Module '{name}' — pas encore implémenté"
        )

    # ========================================================
    # AFFICHER RÉSULTATS ENGAGEMENTS
    # ========================================================

    def show_engagement_results(
        self,
        page_resultat
    ):

        self.stack.setCurrentWidget(
            page_resultat
        )

        self.statusBar().showMessage(
            "Module : État des Engagements"
        )

    # ========================================================
    # RETOUR MENU
    # ========================================================

    def show_menu(
        self
    ):

        # ----------------------------------------------------
        # Fermer éventuellement la progression
        # ----------------------------------------------------

        self._garantie_close_progress()

        # ----------------------------------------------------
        # Retour
        # ----------------------------------------------------

        self.stack.setCurrentWidget(
            self.menu_screen
        )

        self.menu_screen.filename_input.setText(
            "Sélectionnez un module pour lancer un traitement..."
        )

        self.statusBar().showMessage(
            "Prêt"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = PrepDesktopMenuDemo()

    window.show()

    sys.exit(
        app.exec()
    )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    main()