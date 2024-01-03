## Como rodar o projeto

- Copiar o arquivo `.env.example` para `.env` e informar os valores pedidos;
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

## Dados históricos das ações

No site [https://backtester.com.br](https://backtester.com.br) são disponibilizados dados históricos das ações. Eles forcecem gratuitamente os dados dos últimos dois anos para as três ações que precisamos: CEAB3, WEGE3 e PETR4. Eu usei estes dados como base para o processo de atualização do valor das ações ao longo do tempo. Os arquivos CSV estão disponíveis [aqui](./data/stocks).

Para manter os valores atualizados, podemos fazer um processo similar ao que fizemos com as notícias. Podemos rodar um script no background que busque os dados das ações para o dia `d-1` e atualize o nosso banco de dados, neste caso o arquivo CSV de cada uma das ações. Portanto, para manter os valores atualizado eu utilizei a brapi. A documentação da chamada que eu realizo pra buscar os valores históricos das ações pode ser encontrada [aqui](https://brapi.dev/docs/acoes).

### brapi

Script disponível [aqui](./src/integrations/brapi.py).

Este script está programado para buscar os valores históricos das ações para o dia `d-1` e atualizar o arquivo CSV correspondente. Podemos usar o brapi para buscar informações além de `d-1`, mas precisamos de uma licença paga para períodos maiores que 3 meses. Portanto, vou assumir que iremos até a brapi uma vez por dia pra buscar os valores do dia `d-1` e manter nosso dataset atualizado.

Segue o exemplo de como executar o script:

```bash
python src/integrations/brapi.py CEAB3 WEGE3 PETR4
```

## Melhorias

- [ ] Buscar os dados históricos das ações a partir da data mais recente que temos no nosso banco de dados;
- [ ] Criar um banco de dados MySQL para armazenar os dados históricos das ações e as notícias, garantindo a utilização de transações e a integridade dos dados;
