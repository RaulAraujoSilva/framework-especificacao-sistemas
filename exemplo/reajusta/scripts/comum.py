"""Parâmetros e caminhos compartilhados pelos scripts da especificação.

O que é específico do órgão (feriados, fontes dos índices, séries públicas) vem do perfil em perfis/<nome>.py,
escolhido pela variável de ambiente PERFIL (padrão rj_agenersa, o caso de referência). Os scripts importam só de
`comum`. Os demais nomes do perfil (unidades do SEI, categorias de documento etc.) servem ao repositório de mapeamento
e são ignorados aqui.
"""
from __future__ import annotations

import importlib.util
import os
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _carregar_perfil():
    """Perfil por nome (perfis/<PERFIL>.py) ou por caminho de arquivo .py."""
    nome = os.environ.get("PERFIL") or "rj_agenersa"
    arq = Path(nome) if nome.endswith(".py") else RAIZ / "perfis" / f"{nome}.py"
    if not arq.exists():
        raise SystemExit(f"perfil não encontrado: {arq} (variável PERFIL)")
    spec = importlib.util.spec_from_file_location(f"perfil_{arq.stem}", arq)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PERFIL = _carregar_perfil()


def _caminho(var: str, valor: str, base: Path = RAIZ) -> Path:
    """Variável de ambiente, se definida; senão o valor padrão, relativo a `base` quando não for absoluto."""
    p = Path(os.environ.get(var) or valor)
    return p if p.is_absolute() else base / p


# ---------------------------------------------------------------- caminhos
DADOS = _caminho("SEI_DADOS", PERFIL.DADOS)  # fora do git: caches e textos de contrato
SAIDA = RAIZ / "saida"
LEVANTAMENTO = SAIDA / "levantamento"  # cálculos da coorte, cadastro do contrato, pleito e validação
DOCUMENTOS = SAIDA / "documentos_para_avaliacao"  # versões de leitura geradas (PDF, planilha); não editar à mão
ESPECIFICACAO = RAIZ / "especificacao"  # o pacote técnico: fonte única dos documentos de leitura
INSUMOS = RAIZ / "insumos" / "mapeamento"  # saídas do mapeamento do processo-piloto (repositório de mapeamento)

# ---------------------------------------------------------------- calendário
def _pascoa(ano: int) -> date:
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    return date(ano, (h + l_ - 7 * m + 114) // 31, ((h + l_ - 7 * m + 114) % 31) + 1)


def feriados(anos=PERFIL.ANOS_FERIADOS) -> list[date]:
    """Feriados que fecham o expediente: móveis contados da Páscoa e fixos (mês, dia), ambos do perfil."""
    out: list[date] = []
    for a in anos:
        p = _pascoa(a)
        out += [p + timedelta(days=k) for k in PERFIL.FERIADOS_MOVEIS]
        for m, d in PERFIL.FERIADOS_FIXOS:
            out.append(date(a, m, d))
    return sorted(set(out))


# ---------------------------------------------------------------- motor de cálculo do reajuste (P01)
TOL_RECALCULO_PP = 0.01  # pontos percentuais entre o IR escrito e o recalculado
# Textos integrais dos contratos e aditivos, citados pelo cadastro (campo "documento"). Ficam fora do git: aponte a
# variável TEXTOS_CONTRATOS para a pasta. Sem ela, o validador pula a conferência dos trechos literais (V02).
TEXTOS_CONTRATOS = _caminho("TEXTOS_CONTRATOS", str(DADOS / "textos_contratos"))
SERIES_CACHE = DADOS / "series"  # cache das séries públicas (fora do git)
# Fonte de cada componente das fórmulas de reajuste: (padrão no nome do índice, disponibilidade, onde buscar).
# A ordem importa: o primeiro padrão que casa decide. Subíndices da FGV não estão na base aberta do IPEA.
FONTES_COMPONENTE = [
    (r"(?i)acordo coletivo|ACT\b", "documento", "cláusula de reajuste salarial do acordo coletivo juntado ao pleito"),
    (r"(?i)pre[cç]o da [aá]gua|venda da [aá]gua|CEDAE", "outro reajuste",
     "deliberação do reajuste do preço da água no atacado (processo próprio da CEDAE)"),
    (r"(?i)energia|tarifa .*(Light|Enel)|Grupo A", "pública com regra", "ANEEL, tarifas homologadas (REH) e bandeiras; a regra de composição é do contrato"),
    (r"(?i)m[aã]o de obra|IPA|deriva|qu[ií]mic", "assinatura", "FGV Dados (série paga; o pleito anexa a série)"),
    (r"(?i)IPCA-E|especial", "pública", "IBGE SIDRA, tabela 3065 (número-índice do IPCA-15)"),
    (r"(?i)IPCA|amplo", "pública", "IBGE SIDRA, tabela 1737 (número-índice)"),
    (r"(?i)INCC|constru[cç][aã]o civil", "pública", "IPEADATA IGP12_INCC12 (INCC-DI geral)"),
    (r"(?i)IGP-M|mercado", "pública", "IPEADATA IGP12_IGPM12"),
    (r"(?i)IPC", "pública", "IPEADATA IGP12_IPC12 (IPC-Brasil)"),
    (r"(?i)liminar|judicial", "decisão", "percentual fixado por decisão judicial"),
    (r"(?i)IDG|desempenho", "verificador", "índice apurado pelo verificador independente"),
    (r"(?i)tarifa social|ITS", "concessionária", "bases de economias da concessionária, validadas pelo verificador"),
]
# Séries públicas usadas para procurar os números-índice citados nos pareceres (cache em dados/series/).
SERIES_PUBLICAS = {
    "IPEADATA IGP12_INCC12": ("ipeadata", "IGP12_INCC12"),
    "IPEADATA IGP12_IGPM12": ("ipeadata", "IGP12_IGPM12"),
    "IPEADATA IGP12_IPC12": ("ipeadata", "IGP12_IPC12"),
    "IBGE SIDRA, tabela 1737": ("sidra", "1737/n1/all/v/2266"),
    "IBGE SIDRA, tabela 3065": ("sidra", "3065/n1/all/v/1117"),
}
# O perfil pode trocar as fontes e séries (outro órgão, outros índices).
for _nome in ("TOL_RECALCULO_PP", "FONTES_COMPONENTE", "SERIES_PUBLICAS"):
    globals()[_nome] = getattr(PERFIL, _nome, globals()[_nome])
