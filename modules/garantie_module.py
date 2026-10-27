"""
garantie_module.py

Module : État des Garanties

Reproduction de la macro VBA Garanties() de Prep@udit.

Thèmes produits :
    - Base Garanties
    - Constituée
    - Incomplète
    - Retenue NC
    - Echue

La colonne Statut permet de classer les garanties :
    CONSTITUEE
    INCOMPLETE
    ECHUE
    NON CONSTITUE
    RETENUE
"""

import pandas as pd

from modules.module_base import (
    ModuleAudit,
    ResultatAudit,
    ThemeResultat,
)


class GarantieModule(ModuleAudit):

    nom = "État des Garanties"

    # ---------------------------------------------------------
    # STATUTS
    # ---------------------------------------------------------

    STATUT_CONSTITUEE = "CONSTITUEE"
    STATUT_INCOMPLETE = "INCOMPLETE"
    STATUT_ECHUE = "ECHUE"
    STATUT_NON_CONSTITUE = "NON CONSTITUE"
    STATUT_RETENUE = "RETENUE"

    # ---------------------------------------------------------
    # OUTILS
    # ---------------------------------------------------------

    @staticmethod
    def _normaliser_colonnes(df):

        df = df.copy()

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        return df

    @staticmethod
    def _normaliser_texte(series):

        return (
            series
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace("\u00a0", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
        )

    @staticmethod
    def _nombre(series):

        if series is None:
            return pd.Series(dtype=float)

        if not isinstance(series, pd.Series):
            series = pd.Series(series)

        texte = (
            series
            .astype(str)
            .str.strip()
            .str.replace("\u00a0", "", regex=False)
            .str.replace(" ", "", regex=False)
        )

        texte = texte.str.replace(",", ".", regex=False)

        texte = texte.replace(
            {
                "": "0",
                "nan": "0",
                "None": "0",
                "NaN": "0",
            }
        )

        return pd.to_numeric(
            texte,
            errors="coerce"
        ).fillna(0)

    @staticmethod
    def _excel_column(df, letter):

        numero = 0

        for char in letter.upper():

            numero = (
                numero * 26
                + ord(char) - ord("A") + 1
            )

        index = numero - 1

        if index < 0 or index >= len(df.columns):
            return None

        return df.columns[index]

    # ---------------------------------------------------------
    # PREPARATION DE LA BASE
    # ---------------------------------------------------------

    def _preparer_base(self, df):

        df = df.copy()

        # Nettoyage général
        df = self._normaliser_colonnes(df)

        df = df.dropna(
            how="all"
        ).copy()

        if df.empty:
            raise ValueError(
                "Le fichier des garanties ne contient aucune donnée."
            )

        # -----------------------------------------------------
        # Reproduction du VBA :
        #
        # Columns("E:E").Delete
        # Columns("I:I").Delete
        # Columns("J:J").Delete
        #
        # IMPORTANT :
        # Les suppressions sont faites successivement.
        # -----------------------------------------------------

        colonnes_a_supprimer = []

        col_e = self._excel_column(df, "E")
        if col_e is not None:
            colonnes_a_supprimer.append(col_e)

        # suppression E
        if col_e is not None:
            df = df.drop(columns=[col_e])

        # après suppression E, recherche I
        col_i = self._excel_column(df, "I")
        if col_i is not None:
            df = df.drop(columns=[col_i])

        # après suppression I, recherche J
        col_j = self._excel_column(df, "J")
        if col_j is not None:
            df = df.drop(columns=[col_j])

        # -----------------------------------------------------
        # La macro impose ensuite :
        #
        # B = Id
        # C = Relation
        # D = N° Dossier
        # E = N° Garantie
        # F = Code Garantie
        # G = Garantie
        # H = Montant
        # I = Statut
        # J = Observation
        # -----------------------------------------------------

        noms = list(df.columns)

        if len(noms) < 10:
            raise ValueError(
                "Le fichier des Garanties ne contient pas suffisamment "
                "de colonnes après préparation."
            )

        nouveaux_noms = noms.copy()

        nouveaux_noms[1] = "Id"
        nouveaux_noms[2] = "Relation"
        nouveaux_noms[3] = "N° Dossier"
        nouveaux_noms[4] = "N° Garantie"
        nouveaux_noms[5] = "Code Garantie"
        nouveaux_noms[6] = "Garantie"
        nouveaux_noms[7] = "Montant"
        nouveaux_noms[8] = "Statut"
        nouveaux_noms[9] = "Observation"

        df.columns = nouveaux_noms

        # -----------------------------------------------------
        # Nettoyage des champs
        # -----------------------------------------------------

        for colonne in [
            "Id",
            "Relation",
            "N° Dossier",
            "N° Garantie",
            "Code Garantie",
            "Garantie",
            "Statut",
            "Observation",
        ]:

            if colonne in df.columns:

                df[colonne] = (
                    df[colonne]
                    .astype(str)
                    .str.strip()
                )

        # -----------------------------------------------------
        # Montant
        # -----------------------------------------------------

        if "Montant" in df.columns:

            df["Montant"] = self._nombre(
                df["Montant"]
            )

        # -----------------------------------------------------
        # Statut normalisé
        # -----------------------------------------------------

        if "Statut" in df.columns:

            df["Statut"] = self._normaliser_texte(
                df["Statut"]
            )

        return df

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def executer(
        self,
        transactions: pd.DataFrame
    ) -> ResultatAudit:

        if transactions is None:
            raise ValueError(
                "Aucune donnée à traiter."
            )

        # -----------------------------------------------------
        # Préparation
        # -----------------------------------------------------

        df = self._preparer_base(
            transactions
        )

        # -----------------------------------------------------
        # Vérification Statut
        # -----------------------------------------------------

        if "Statut" not in df.columns:

            raise ValueError(
                "La colonne 'Statut' est introuvable "
                "dans l'état des Garanties."
            )

        # =====================================================
        # THÈME 1 : BASE GARANTIES
        # =====================================================

        base_garanties = df.copy()

        # =====================================================
        # THÈME 2 : CONSTITUÉE
        # =====================================================

        constituee = df[
            df["Statut"]
            == self.STATUT_CONSTITUEE
        ].copy()

        # =====================================================
        # THÈME 3 : INCOMPLÈTE
        # =====================================================

        incomplete = df[
            df["Statut"]
            == self.STATUT_INCOMPLETE
        ].copy()

        # =====================================================
        # THÈME 4 : RETENUE NC
        #
        # VBA :
        # Criteria1: "=NON CONSTITUE"
        # Criteria2: "=RETENUE"
        # =====================================================

        retenue_nc = df[
            df["Statut"].isin(
                [
                    self.STATUT_NON_CONSTITUE,
                    self.STATUT_RETENUE,
                ]
            )
        ].copy()

        # =====================================================
        # THÈME 5 : ECHUE
        # =====================================================

        echue = df[
            df["Statut"]
            == self.STATUT_ECHUE
        ].copy()

        # =====================================================
        # THEMES
        # =====================================================

        themes = [

            ThemeResultat(
                "Base Garanties",
                base_garanties,
                "Montant"
            ),

            ThemeResultat(
                "Constituée",
                constituee,
                "Montant"
            ),

            ThemeResultat(
                "Incomplète",
                incomplete,
                "Montant"
            ),

            ThemeResultat(
                "Retenue NC",
                retenue_nc,
                "Montant"
            ),

            ThemeResultat(
                "Echue",
                echue,
                "Montant"
            ),
        ]

        # =====================================================
        # RESULTAT
        # =====================================================

        resultat = ResultatAudit(
            nb_lignes_total=len(df),
            themes=themes
        )

        return resultat