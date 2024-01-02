## Como rodar o projeto

- Copiar o arquivo `.env.example` e informar os valores pedidos;
- Instalar as dependências do projeto:
```bash
pip install -r requirements.txt
```
- Rodar o projeto para desenvolvimento local:
```bash
python src/dashboard.py
```

## Brazil Journal Scraper

Script disponível [aqui](./src/integrations/braziljournal.py).

Este é um scraper das notícias do site [Brazil Journal](https://braziljournal.com/). Ele busca as notícias disponíveis no site e armazena num arquivo CSV, disponível em `data/braziljournal.csv`. Você pode informar uma lista de ações para o script. Segue o exemplo de como executar o script:

```bash
python src/integrations/braziljournal.py CEAB3 WEGE3 PETR4
```

A ideia deste scraper é manter uma base de dados atualizada com as notícias do site. Podemos rodar o script no background (um Lambda da AWS, um CronJob do Kubernetes, etc) a cada `x` tempo, por exemplo.

Quando o usuário seleciona uma ação no dashboard, eu tento buscar os dados mais recentes diretamente no site do Brazil Journal com um timeout de 1 segundo. Caso o site não responda em 1 segundo, eu busco os dados do arquivo CSV. Desta forma, conseguimos mostrar notícias mesmo que o site do Brazil Journal esteja fora do ar e, ao mesmo tempo, temos a opção de mostrarmos os dados mais atualizados no dashboard.

## brapi

A documentação da chamada que eu realizo pra buscar os valores históricos das ações pode ser encontrada [aqui](https://brapi.dev/docs/acoes).

Como a documentação diz que podemos esperar "dados com ao menos 30 minutos de atraso", eu adicionei um cache de 15 minutos pra não ir na API buscar os dados todas as vezes que algum reload acontece.

**Para os dados históricos de uma ação podemos fazer o processo similar ao que fizemos para as notícias. Podemos armazenar estes dados em um banco de dados ou arquivo CSV e buscar desta base de dados quando os dados históricos forem solicitados.**
