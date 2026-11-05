import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
# ferramentas do framework e scripts próprios do caso resolvido (comum, validar_pleito)
sys.path[:0] = [str(RAIZ / "scripts"), str(RAIZ / "exemplo" / "reajusta" / "scripts")]
