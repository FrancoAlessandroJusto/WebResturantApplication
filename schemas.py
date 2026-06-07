# =========================
# IMPORT PER TIPI E VALIDAZIONE
# =========================

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


# =========================
# ENUMERAZIONI DI VALIDAZIONE
# =========================

class TipoIngrediente(str, Enum):
    base = 'base'
    salsa = 'salsa'
    formaggio = 'formaggio'
    carne = 'carne'
    verdura = 'verdura'
    premade = 'premade'
    altro = 'altro'


class UnitaRiferimento(str, Enum):
    g = 'g'
    ml = 'ml'
    pz = 'pz'
    kg = 'kg'
    l = 'l'


class CategoriaMenuItem(str, Enum):
    antipasti = 'Antipasti'
    pizza = 'Pizza'
    bevande = 'Bevande'
    dolci = 'Dolci'
    varie = 'Varie'


# =========================
# SCHEMI INGREDIENTI
# =========================

class IngredienteCreate(BaseModel):
    """
    Modello per la creazione di un ingrediente.
    """
    nome: str = Field(min_length=1)
    tipo: TipoIngrediente = TipoIngrediente.altro
    costo_unitario: float = Field(ge=0)
    unita_riferimento: UnitaRiferimento = UnitaRiferimento.pz
    quantita_riferimento: float = Field(default=1.0, gt=0)


class IngredienteUpdate(BaseModel):
    """
    Modello per aggiornare un ingrediente.
    """
    nome: Optional[str] = Field(default=None, min_length=1)
    tipo: Optional[TipoIngrediente] = None
    costo_unitario: Optional[float] = Field(default=None, ge=0)
    unita_riferimento: Optional[UnitaRiferimento] = None
    quantita_riferimento: Optional[float] = Field(default=None, gt=0)
    attiva: Optional[bool] = None
    """
    Modello per aggiornare un ingrediente.
    """
    nome: Optional[str] = Field(default=None, min_length=1)
    tipo: Optional[str] = None
    costo_unitario: Optional[float] = Field(default=None, ge=0)
    unita_riferimento: Optional[str] = None
    quantita_riferimento: Optional[float] = Field(default=None, gt=0)
    attiva: Optional[bool] = None


class IngredienteOut(BaseModel):
    """
    Modello di output per un ingrediente.
    """
    id: int
    nome: str
    tipo: str
    costo_unitario: float
    unita_riferimento: str
    quantita_riferimento: float
    attiva: bool = True


# =========================
# SCHEMI MENU
# =========================

class MenuItemIngredientCreate(BaseModel):
    ingrediente_id: int
    quantita: float = Field(gt=0)


class MenuItemIngredientReference(BaseModel):
    nome: str
    costo_unitario: float
    quantita_riferimento: float
    unita_riferimento: str


class MenuItemIngredientOut(BaseModel):
    nome: str
    quantita: float
    unita_riferimento: str
    costo_unitario: float
    quantita_riferimento: float
    ingrediente: MenuItemIngredientReference


class MenuItemCreate(BaseModel):
    nome: str = Field(min_length=1)
    prezzo: float = Field(ge=0)
    categoria: CategoriaMenuItem
    ingredienti: Optional[List[MenuItemIngredientCreate]] = Field(default_factory=list)


class MenuItemUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1)
    prezzo: Optional[float] = Field(default=None, ge=0)
    categoria: Optional[CategoriaMenuItem] = None
    ingredienti: Optional[List[MenuItemIngredientCreate]] = None
    nome: Optional[str] = Field(default=None, min_length=1)
    prezzo: Optional[float] = Field(default=None, ge=0)
    categoria: Optional[str] = Field(default=None, min_length=1)
    ingredienti: Optional[List[MenuItemIngredientCreate]] = None


class MenuItemOut(BaseModel):
    id: int
    nome: str
    prezzo: float
    categoria: str
    ingredienti: List[MenuItemIngredientOut] = Field(default_factory=list)
    costo_ingredienti: float
