# Dashboard Financeiro - Análise Técnica

Dashboard interativo para análise técnica de ações usando Streamlit, com os seguintes indicadores:
- Stochastic (14,3,3)
- RSI (7)
- MACD (12,26,9)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como usar

Execute o aplicativo:
```bash
streamlit run app.py
```

## Funcionalidades

- Visualização de gráfico de candlestick
- Indicadores técnicos configurados
- Sistema de sinais por cores:
  - Verde: Todos indicadores positivos
  - Vermelho: Todos indicadores negativos
  - Preto: Sinais mistos
- Seleção flexível de ativos e períodos
- Interface responsiva e intuitiva

## Estrutura do Projeto

```
├── app.py                 # Aplicativo principal
├── requirements.txt       # Dependências do projeto
├── utils/
│   ├── data.py           # Funções para busca de dados
│   ├── indicators.py     # Cálculo de indicadores
│   └── plotting.py       # Funções de visualização
└── README.md             # Documentação
```