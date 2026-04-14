# =========================
# IMPORT PER TIPI E VALIDAZIONE
# =========================

from typing import Optional          # Serve per indicare campi opzionali (possono essere None)
from pydantic import BaseModel, Field  # BaseModel: modello dati, Field: vincoli e metadati


# =========================
# SCHEMA: CREAZIONE PIZZA
# =========================

class PizzaCreate(BaseModel):
    """
    Modello usato quando si CREA una nuova pizza (POST).

    Tutti i campi sono obbligatori perché stiamo creando
    una nuova entità completa.
    """

    # nome:
    # - stringa
    # - deve avere almeno 1 carattere
    nome: str = Field(min_length=1)

    # prezzo:
    # - numero float
    # - deve essere >= 0
    prezzo: float = Field(ge=0)


# =========================
# SCHEMA: AGGIORNAMENTO PIZZA
# =========================

class PizzaUpdate(BaseModel):
    """
    Modello usato quando si AGGIORNA una pizza (PATCH).

    Tutti i campi sono opzionali:
    l’utente può inviare solo quelli che vuole modificare.
    """

    # nome:
    # - opzionale
    # - se presente, deve avere almeno 1 carattere
    nome: Optional[str] = Field(default=None, min_length=1)

    # prezzo:
    # - opzionale
    # - se presente, deve essere >= 0
    prezzo: Optional[float] = Field(default=None, ge=0)

    # attiva:
    # - opzionale
    # - booleano (True/False)
    # - usato per attivare/disattivare una pizza senza eliminarla
    attiva: Optional[bool] = None


# =========================
# SCHEMA: OUTPUT PIZZA
# =========================

class PizzaOut(BaseModel):
    """
    Modello usato per le RISPOSTE (response_model).

    Serve a:
    - documentare l’API (Swagger)
    - garantire che l’output abbia sempre questa forma
    """

    id: int        # id univoco della pizza (dal database)
    nome: str      # nome della pizza
    prezzo: float  # prezzo corrente
    attiva: bool   # stato (True=attiva, False=disattiva)
