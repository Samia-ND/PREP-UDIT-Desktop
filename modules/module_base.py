"""
module_base.py

Implémente les classes du diagramme de conception :
- ModuleAudit (abstraite) : contrat commun à tous les modules
- ThemeResultat : un thème d'analyse au sein d'un module (ex: Contentieux, Sans Dossier)
- ResultatAudit : regroupe tous les ThemeResultat produits par un module

Aucune persistance (pas de base de données) : tout est traité en mémoire,
à la volée, à chaque import.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd


@dataclass
class ThemeResultat:
    """Un thème d'analyse au sein d'un module (ex: 'Contentieux AU')."""
    nom_theme: str
    lignes: pd.DataFrame
    montant_colonne: str = "Montant Auto"

    @property
    def nb_lignes(self) -> int:
        return len(self.lignes)

    @property
    def montant_total(self) -> float:
        if self.montant_colonne not in self.lignes.columns:
            return 0.0
        return pd.to_numeric(self.lignes[self.montant_colonne], errors="coerce").fillna(0).sum()

    def calculer_synthese(self) -> dict:
        return {
            "theme": self.nom_theme,
            "nb_lignes": self.nb_lignes,
            "montant_total": self.montant_total,
        }


@dataclass
class ResultatAudit:
    """Résultat complet produit par l'exécution d'un module."""
    date_execution: datetime = field(default_factory=datetime.now)
    nb_lignes_total: int = 0
    themes: list[ThemeResultat] = field(default_factory=list)
    fiche_recap: dict | None = None  # Synthèse Nature (Décaissement/Signature/Contentieux)

    def get_theme(self, nom: str) -> ThemeResultat | None:
        return next((t for t in self.themes if t.nom_theme == nom), None)

    def afficher(self):
        print(f"--- Résultat audit ({self.date_execution:%d/%m/%Y %H:%M}) ---")
        print(f"Lignes totales traitées : {self.nb_lignes_total}")
        for t in self.themes:
            s = t.calculer_synthese()
            print(f"  {s['theme']:<25} {s['nb_lignes']:>6} lignes   {s['montant_total']:>15,.0f}")


class ModuleAudit(ABC):
    """
    Classe abstraite mère de tous les modules (Journal, Encaisse, Comptes,
    Engagement, Garantie...). Chaque module concret implémente executer()
    avec ses propres règles métier.
    """

    nom: str = "Module générique"
    colonnes_attendues: list[str] = []

    def valider(self, df: pd.DataFrame) -> list[str]:
        """Vérifie que les colonnes nécessaires sont présentes.
        Retourne la liste des colonnes manquantes (vide si tout est OK)."""
        return [c for c in self.colonnes_attendues if c not in df.columns]

    @abstractmethod
    def executer(self, transactions: pd.DataFrame) -> ResultatAudit:
        """Applique les règles métier du module et retourne un ResultatAudit.
        Doit être implémentée par chaque sous-classe."""
        raise NotImplementedError
