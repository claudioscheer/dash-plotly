## Brazil Journal Scraper

Script disponível [aqui](./src/integration/braziljournal.py).

Este é um scraper das notícias do site [Brazil Journal](https://braziljournal.com/). Ele busca as notícias disponíveis no site e armazenar num arquivo CSV, disponível em `data/braziljournal.csv`. Você pode informar uma lista de ações para o script. Segue o exemplo de como executar o script:

```bash
python src/integration/braziljournal.py CEAB3 WEGE3 PETR4
```

A ideia deste scraper é manter uma base de dados atualizada com as notícias do site. Podemos rodar o script no background (uma Lambda da AWS, um CronJob do Kubernetes, etc) a cada `x` tempo, por exemplo.

No dashboard, eu tento buscar os dados mais recentes do site com um timeout de 1 segundo. Caso o site não responda em 1 segundo, eu busco os dados do arquivo CSV. Desta forma, conseguimos mostrar notícias mesmo que o site do Brazil Journal esteja fora do ar e, ao mesmo tempo, temos a opção de mostrarmos os dados mais atualizados no dashboard.
