import pandas as pd

from modules.module_base import (
    ModuleAudit,
    ResultatAudit,
    ThemeResultat
)


class EngagementModule(ModuleAudit):

    nom = "État des Engagements"

    colonnes_attendues = [
        "N° Client",
        "N° Dossier",
        "Code Agence",
        "Libellé Agence",
        "N° Compte",
        "Réf Produit",
        "Montant Auto",
        "Montant Util",
    ]

    CODES_CONTENTIEUX = {
        "922",
        "923",
        "924",
        "925"
    }

    CODE_CMT_OXYGENE = {"437"}
    CODES_RELANCE = {"435", "436"}
    CODE_START_TPE = {"434"}
    CODE_ASMN = {"321"}
    CODE_ESC_COM = {"122"}

    CODES_ASM_CR_COMP = {
        "122",
        "130",
        "213",
        "321",
        "416"
    }

    NATURE_SIGNATURE = "8"

    # =====================================================
    # OUTILS
    # =====================================================

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
            .str.replace(",", ".", regex=False)
        )

        texte = texte.replace(
            {
                "": "0",
                "nan": "0",
                "NaN": "0",
                "None": "0"
            }
        )

        return pd.to_numeric(
            texte,
            errors="coerce"
        ).fillna(0)

    @staticmethod
    def _excel_column(df, letter):

        number = 0

        for char in letter.upper():
            number = number * 26 + (
                ord(char) - ord("A") + 1
            )

        index = number - 1

        if index < 0 or index >= len(df.columns):
            return None

        return df.columns[index]

    @staticmethod
    def _format_code(series):

        return (
            series
            .astype(str)
            .str.strip()
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
        )

    @staticmethod
    def _normaliser_colonnes(df):

        df = df.copy()

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        return df

    # =====================================================
    # CONTENTIEUX
    # =====================================================

    def _identifier_contentieux_direct(self, df):

        if "Réf Produit" not in df.columns:

            return pd.Series(
                False,
                index=df.index
            )

        return (
            df["Réf Produit"]
            .astype(str)
            .str.strip()
            .isin(
                self.CODES_CONTENTIEUX
            )
        )

    def _identifier_contentieux(self, df):

        direct = self._identifier_contentieux_direct(df)

        if "N° Client" not in df.columns:
            return direct

        clients = (
            df.loc[
                direct,
                "N° Client"
            ]
            .astype(str)
            .str.strip()
            .unique()
        )

        return (
            df["N° Client"]
            .astype(str)
            .str.strip()
            .isin(clients)
        )

    # =====================================================
    # IMPAYÉS
    # =====================================================

    def _identifier_impayes(self, df):

        colonne_s = self._excel_column(
            df,
            "S"
        )

        colonne_v = self._excel_column(
            df,
            "V"
        )

        if colonne_s is None or colonne_v is None:

            return pd.Series(
                False,
                index=df.index
            )

        s = self._nombre(
            df[colonne_s]
        )

        v = self._nombre(
            df[colonne_v]
        )

        return (
            (s != 0)
            |
            (v != 0)
        )

    # =====================================================
    # DOSSIERS IMPAYÉS
    # =====================================================

    def _dossiers_impayes(self, df):

        masque = self._identifier_impayes(df)

        if "N° Dossier" not in df.columns:
            return set()

        dossiers = set(
            df.loc[
                masque,
                "N° Dossier"
            ]
            .astype(str)
            .str.strip()
        )

        # Les dossiers ayant un produit contentieux
        # sont exclus des impayés.
        direct = self._identifier_contentieux_direct(df)

        dossiers_contentieux = set(
            df.loc[
                direct,
                "N° Dossier"
            ]
            .astype(str)
            .str.strip()
        )

        return dossiers - dossiers_contentieux

    # =====================================================
    # MONTANTS IMPAYÉS
    # =====================================================

    def _calculer_montants_impayes(
        self,
        df
    ):

        if "N° Dossier" not in df.columns:
            return 0.0, 0.0, 0.0

        dossiers = self._dossiers_impayes(df)

        if not dossiers:
            return 0.0, 0.0, 0.0

        base = df[
            df["N° Dossier"]
            .astype(str)
            .str.strip()
            .isin(dossiers)
        ].copy()

        # -------------------------------------------------
        # UNE SEULE VALEUR PAR DOSSIER
        # -------------------------------------------------

        base = (
            base
            .drop_duplicates(
                subset=["N° Dossier"]
            )
        )

        colonne_m = self._excel_column(
            df,
            "T"
        )

        colonne_w = self._excel_column(
            df,
            "W"
        )

        # -------------------------------------------------
        # CRÉDITS AMORTISSABLES
        # -------------------------------------------------

        if colonne_m is not None:

            montant_credit = float(
                self._nombre(
                    base[colonne_m]
                ).sum()
            )

        else:

            montant_credit = 0.0

        # -------------------------------------------------
        # ESCOMPTE
        # -------------------------------------------------

        if colonne_w is not None:

            montant_escompte = float(
                self._nombre(
                    base[colonne_w]
                ).sum()
            )

        else:

            montant_escompte = 0.0

        total = (
            montant_credit
            +
            montant_escompte
        )

        return (
            montant_credit,
            montant_escompte,
            total
        )

    # =====================================================
    # CLASSIFICATION NATURE
    # =====================================================

    def _classifier_nature(self, df):

        colonne_nature = None

        for colonne in df.columns:

            nom = (
                str(colonne)
                .strip()
                .lower()
            )

            if nom in {
                "nature",
                "nature au",
                "nature engagement",
                "nature des engagements"
            }:

                colonne_nature = colonne
                break

        # -------------------------------------------------
        # Si Nature existe réellement
        # -------------------------------------------------

        if colonne_nature is not None:

            nature = (
                df[colonne_nature]
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\.0$",
                    "",
                    regex=True
                )
            )

            return (
                nature == self.NATURE_SIGNATURE
            )

        # -------------------------------------------------
        # Sinon Réf Produit
        # -------------------------------------------------

        ref = (
            df["Réf Produit"]
            .astype(str)
            .str.strip()
        )

        return ref.str.startswith(
            self.NATURE_SIGNATURE
        )

    # =====================================================
    # EXECUTION
    # =====================================================

    def executer(
        self,
        transactions: pd.DataFrame
    ) -> ResultatAudit:

        if transactions is None:
            raise ValueError(
                "Aucune donnée à traiter."
            )

        df = self._normaliser_colonnes(
            transactions
        )

        df = df.dropna(
            how="all"
        ).copy()

        if df.empty:
            raise ValueError(
                "Le fichier ne contient aucune donnée."
            )

        # -------------------------------------------------
        # NUMÉRIQUES
        # -------------------------------------------------

        for colonne in [
            "Montant Auto",
            "Montant Util",
            "Dépassement"
        ]:

            if colonne in df.columns:

                df[colonne] = self._nombre(
                    df[colonne]
                )

        # -------------------------------------------------
        # CODES
        # -------------------------------------------------

        if "Réf Produit" in df.columns:

            df["Réf Produit"] = (
                self._format_code(
                    df["Réf Produit"]
                )
            )

        for colonne in [
            "N° Client",
            "N° Dossier",
            "N° Compte"
        ]:

            if colonne in df.columns:

                df[colonne] = (
                    df[colonne]
                    .astype(str)
                    .str.strip()
                    .str.replace(
                        r"\.0$",
                        "",
                        regex=True
                    )
                )

        # =================================================
        # MASQUES
        # =================================================

        masque_contentieux_direct = (
            self._identifier_contentieux_direct(df)
        )

        masque_contentieux = (
            self._identifier_contentieux(df)
        )

        masque_impayes = (
            self._identifier_impayes(df)
        )

        # =================================================
        # IMPAYÉS
        # =================================================

        (
            montant_impaye_credit,
            montant_impaye_escompte,
            total_impayes
        ) = self._calculer_montants_impayes(
            df
        )

        # =================================================
        # THEMES
        # =================================================

        themes = []

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        themes.append(
            ThemeResultat(
                "Total Engagement",
                df.copy(),
                "Montant Auto"
            )
        )

        # -------------------------------------------------
        # SANS DOSSIER
        # -------------------------------------------------

        sans_dossier = df[
            df["N° Dossier"] == "00000000"
        ].copy()

        themes.append(
            ThemeResultat(
                "Sans Dossier AU",
                sans_dossier,
                "Montant Auto"
            )
        )

        # -------------------------------------------------
        # DEP UTIL
        # -------------------------------------------------

        dep_util = df[
            df["Montant Util"] > 0
        ].copy()

        themes.append(
            ThemeResultat(
                "Dep. Util AU",
                dep_util,
                "Montant Util"
            )
        )

        # -------------------------------------------------
        # CONTENTIEUX
        # -------------------------------------------------

        contentieux = df[
            masque_contentieux
        ].copy()

        themes.append(
            ThemeResultat(
                "Contentieux AU",
                contentieux,
                "Montant Util"
            )
        )

        # -------------------------------------------------
        # IMPAYÉS
        # -------------------------------------------------

        impayes = df[
            masque_impayes
        ].copy()

        colonne_t = self._excel_column(
            df,
            "T"
        )

        colonne_w = self._excel_column(
            df,
            "W"
        )

        if colonne_t is not None:
            impayes["_Impayes_CMT"] = (
                self._nombre(
                    impayes[colonne_t]
                )
            )
        else:
            impayes["_Impayes_CMT"] = 0.0

        if colonne_w is not None:
            impayes["_Impayes_ESC"] = (
                self._nombre(
                    impayes[colonne_w]
                )
            )
        else:
            impayes["_Impayes_ESC"] = 0.0

        impayes["_Montant_Impayes"] = (
            impayes["_Impayes_CMT"]
            +
            impayes["_Impayes_ESC"]
        )

        themes.append(
            ThemeResultat(
                "Impayés ESC & CMT",
                impayes,
                "_Montant_Impayes"
            )
        )

        # -------------------------------------------------
        # BASE HORS CONTENTIEUX
        # -------------------------------------------------

        base_hors_contentieux = df[
            ~masque_contentieux
        ].copy()

        themes.append(
            ThemeResultat(
                "Base AU Hrs CTX",
                base_hors_contentieux,
                "Montant Auto"
            )
        )

        # =================================================
        # NATURE AU
        # =================================================

        masque_signature = (
            self._classifier_nature(df)
        )

        base_nature = df.copy()

        base_nature["Nature"] = (
            masque_signature
            .map(
                {
                    True: "8",
                    False: "Décaissement"
                }
            )
        )

        themes.append(
            ThemeResultat(
                "Nature AU",
                base_nature,
                "Montant Util"
            )
        )

        # -------------------------------------------------
        # DOSSIERS ÉCHUS
        # -------------------------------------------------

        colonne_date = None

        for nom in [
            "Date Echéance",
            "Date Échéance",
            "Date Echeance"
        ]:

            if nom in df.columns:
                colonne_date = nom
                break

        if colonne_date:

            dates = pd.to_datetime(
                df[colonne_date],
                errors="coerce"
            )

            echus = df[
                dates.notna()
                &
                (
                    dates < pd.Timestamp.now()
                )
            ].copy()

        else:

            echus = df.iloc[0:0].copy()

        themes.append(
            ThemeResultat(
                "Dossiers Echus AU",
                echus,
                "Montant Auto"
            )
        )

        # =================================================
        # AUTRES THEMES
        # =================================================

        def ajouter_theme(nom, codes):

            lignes = df[
                df["Réf Produit"].isin(codes)
            ].copy()

            themes.append(
                ThemeResultat(
                    nom,
                    lignes,
                    "Montant Auto"
                )
            )

        ajouter_theme(
            "CMT Oxygène",
            self.CODE_CMT_OXYGENE
        )

        ajouter_theme(
            "Relance",
            self.CODES_RELANCE
        )

        ajouter_theme(
            "Start TPE",
            self.CODE_START_TPE
        )

        ajouter_theme(
            "ASMN",
            self.CODE_ASMN
        )

        ajouter_theme(
            "ESC COM",
            self.CODE_ESC_COM
        )

        ajouter_theme(
            "ASM CR COMP",
            self.CODES_ASM_CR_COMP
        )

        # =================================================
        # RESULTAT
        # =================================================

        resultat = ResultatAudit(
            nb_lignes_total=len(df),
            themes=themes
        )

        resultat.fiche_recap = (
            self._calculer_fiche_recap(
                df,
                masque_contentieux_direct,
                masque_contentieux
            )
        )

        return resultat

    # =====================================================
    # FICHE RECAP
    # =====================================================

    def _calculer_fiche_recap(
        self,
        df,
        masque_contentieux_direct,
        masque_contentieux
    ):

        montant_util = self._nombre(
            df["Montant Util"]
        )

        # =================================================
        # SIGNATURE
        # =================================================

        masque_signature = (
            self._classifier_nature(df)
        )

        total_signature = float(
            montant_util[
                masque_signature
            ].sum()
        )

        # =================================================
        # DÉCAISSEMENT
        #
        # IMPORTANT :
        # on exclut uniquement les lignes dont le
        # produit est directement contentieux.
        #
        # Les impayés restent dans Décaissement.
        # =================================================

        total_decaissement = float(
            montant_util[
                (~masque_signature)
                &
                (~masque_contentieux_direct)
            ].sum()
        )

        # =================================================
        # IMPAYÉS
        # =================================================

        (
            montant_impaye_credit,
            montant_impaye_escompte,
            total_impayes
        ) = self._calculer_montants_impayes(
            df
        )

        # =================================================
        # CONTENTIEUX
        #
        # Ici on utilise le contentieux propagé au client.
        # =================================================

        total_contentieux = float(
            montant_util[
                masque_contentieux
            ].sum()
        )

        # =================================================
        # HORS CONTENTIEUX
        # =================================================

        engagements_hors_contentieux = (
            total_decaissement
            +
            total_signature
            +
            total_impayes
        )

        # =================================================
        # GLOBAL
        # =================================================

        engagements_globaux = (
            engagements_hors_contentieux
            +
            total_contentieux
        )

        # =================================================
        # POURCENTAGES
        # =================================================

        def pourcentage(valeur):

            if engagements_globaux == 0:
                return 0.0

            return (
                float(valeur)
                /
                float(engagements_globaux)
                *
                100
            )

        return {

            "nature": [

                (
                    "CREDIT PAR DECAISSEMENT",
                    total_decaissement,
                    pourcentage(
                        total_decaissement
                    )
                ),

                (
                    "CREDIT PAR SIGNATURE",
                    total_signature,
                    pourcentage(
                        total_signature
                    )
                ),

                (
                    "IMPAYES",
                    total_impayes,
                    pourcentage(
                        total_impayes
                    )
                ),

                (
                    "ENGAGEMENTS GLOBALAUX HORS CONTENTIEUX",
                    engagements_hors_contentieux,
                    pourcentage(
                        engagements_hors_contentieux
                    )
                ),

                (
                    "CONTENTIEUX",
                    total_contentieux,
                    pourcentage(
                        total_contentieux
                    )
                ),

                (
                    "ENGAGEMENTS GLOBALAUX",
                    engagements_globaux,
                    100.0
                )
            ],

            "impayes": [

                (
                    "Impayés Crédits Amortissables",
                    montant_impaye_credit
                ),

                (
                    "Impayés Escompte Papier Commercial",
                    montant_impaye_escompte
                ),

                (
                    "TOTAL",
                    total_impayes
                )
            ]
        }