# AstroGraf - Gerador de Mapas Astrais Gráficos

Aplicação web para gerar, visualizar e baixar mapas astrais em formato SVG. Desenvolvida com Flask e Kerykeion, oferece uma interface intuitiva para calcular e visualizar posições planetárias.

## Funcionalidades

- **Geração de Mapas Astrais**: Calcula posições planetárias com base em data, hora e localização
- **Interface Intuitiva**: Formulário web com preenchimento automático de dados de cidades
- **Busca de Cidades**: Banco de dados integrado com mais de 40.000 cidades mundiais
- **Visualização em Popup**: Modal interativo para visualizar o mapa gerado
- **Cópia para Clipboard**: Duplo clique para copiar a imagem (700x1000px) para área de transferência
- **Download em SVG**: Salve o mapa em formato vetorial escalável
- **Suporte a Múltiplos Sistemas de Casas**: Regiomontanus, Placidus, Campanus, Koch e mais
- **Ajuste de Timezone**: Suporte a diferentes fusos horários mundiais

## Requisitos

- Python 3.8+
- Flask 2.3.0+
- Kerykeion 4.20.0+
- Swisseph 2.10.3.2+
- Arquivo de dados: `CidMundo.txt`

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/astrograf.git
cd astrograf
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Adicione o arquivo de dados
Coloque o arquivo `CidMundo.txt` no diretório raiz do projeto. Este arquivo contém dados de cidades mundiais com suas coordenadas e fusos horários.

O arquivo deve ter o seguinte formato:
```
Código|País|Estado|Cidade|Latitude|Longitude|Altitude|DST|UTC_Offset
```

### 5. Execute a aplicação
```bash
python astrograf.py
```

A aplicação estará disponível em `http://localhost:5000`

## Como Usar

1. **Preencha os dados pessoais**:
   - Nome do mapa
   - Data de nascimento (dia/mês/ano)
   - Hora de nascimento (hora/minuto/segundo)

2. **Defina a localização**:
   - Use o botão "🔍 Buscar" para localizar automaticamente sua cidade
   - Ou preencha manualmente latitude, longitude e fuso horário

3. **Configure as casas terrestres**:
   - Selecione o sistema de casas desejado

4. **Gere o mapa**:
   - Clique em "GERAR GRÁFICO"
   - O mapa abrirá em um popup

5. **Trabalhe com o mapa**:
   - **Duplo clique**: Copia a imagem (700x1000px) para clipboard
   - **Botão 📥 Baixar**: Salva como arquivo SVG
   - **Botão ↗ Nova Aba**: Abre em uma nova aba do navegador
   - **Clique fora ou botão ✕**: Fecha o popup

## Estrutura do Projeto

```
astrograf/
├── astrograf.py           # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── CidMundo.txt          # Banco de dados de cidades (não incluído)
└── .gitignore
```

## Rotas da API

### GET `/`
Retorna a página principal com formulário interativo.

### GET `/api/cidades?q=<query>`
Busca cidades no banco de dados.

**Parâmetros:**
- `q` (string): Termo de busca (mínimo 2 caracteres)

**Resposta:**
```json
[
  {
    "city": "Brasília",
    "state": "DF",
    "country": "Brasil",
    "lat": -15.7975,
    "lon": -47.8919,
    "tz": -3.0
  }
]
```

### POST `/api/gerar-grafico`
Gera o mapa astral em formato SVG.

**Body:**
```json
{
  "nome": "Meu Mapa",
  "dia": 15,
  "mes": 6,
  "ano": 1990,
  "hora": 14,
  "minuto": 30,
  "segundo": 0,
  "latitude": -15.7975,
  "longitude": -47.8919,
  "timezone": -3.0,
  "cidade": "Brasília",
  "pais": "Brasil"
}
```

**Resposta:**
- Arquivo SVG no formato `image/svg+xml`

## Mapeamento de Timezones

A aplicação mapeia offsets UTC para identificadores IANA válidos. Exemplo:
- `-3.0` → `America/Sao_Paulo`
- `0.0` → `UTC`
- `9.0` → `Asia/Tokyo`

Veja a variável `TZ_MAP` em `astrograf.py` para a lista completa.

## Dependências

```
Flask==2.3.0
kerykeion==4.20.0
swisseph==2.10.3.2
```

Instale com:
```bash
pip install -r requirements.txt
```

## Notas Importantes

- **Arquivo CidMundo.txt**: Essencial para a busca de cidades. Sem este arquivo, a funcionalidade de busca não funcionará.
- **Precisão Astrológica**: Os cálculos utilizam a biblioteca Swisseph, garantindo precisão em efeméridas.
- **Formato SVG**: Os mapas são gerados em SVG, permitindo escalabilidade sem perda de qualidade.
- **CORS**: Para desenvolvimento local, a cópia de imagem pode ter limitações de CORS em alguns navegadores.

## Troubleshooting

### Erro: "SVG não foi gerado"
- Verifique se a biblioteca Kerykeion está instalada corretamente
- Certifique-se de que tem permissão de escrita no diretório temporário do sistema

### Busca de cidades não funciona
- Verifique se `CidMundo.txt` está no diretório raiz
- Confirme que o arquivo tem o formato correto

### Erro de timezone
- Verifique se o offset UTC está correto
- Consulte `TZ_MAP` em `astrograf.py` para offsets suportados

## Desenvolvimento

Para modo de desenvolvimento com debug:
```bash
python astrograf.py
```

A aplicação será executada em `http://localhost:5000` com reload automático.

## Licença

Este projeto é fornecido para uso gratuito e franqueado.

## Autor

Desenvolvido por Adonis Saliba (Outubro 2025)

## Créditos

- [Kerykeion](https://github.com/g-battaglia/Kerykeion): Biblioteca para cálculos astrológicos
- [Swisseph](https://www.astro.com/swisseph/): Efeméridas astronômicas
- [Flask](https://flask.palletsprojects.com/): Framework web

## Contribuições

Contribuições são bem-vindas! Por favor, faça um fork do projeto e envie um pull request.

## Contato

Para dúvidas ou sugestões, abra uma issue no repositório.