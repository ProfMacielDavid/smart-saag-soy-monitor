# One‑pager (FAPERON) – Produtos e Diferenciais Adicionais

**Projeto:** SMART SAAG – Monitoramento de Soja (Centelha II)  
**Período:** 2025  
**Status do protótipo:** MVP funcional com rotinas de ingestão Sentinel‑2, cálculo de índices de vegetação e séries temporais por talhão.

## O que não estava no plano original e foi entregue
1. **Protótipo de software aberto (GitHub)** com pipeline modular para download, pré‑processamento e análise de imagens Sentinel‑2 via Sentinel Hub, incluindo NDVI/EVI/NDRE e geração de séries temporais por talhão.
2. **API/CLI inicial** para execução padronizada de tarefas, facilitando reprodutibilidade e futuras integrações.
3. **Modelo de detecção de anomalias** (baseline) baseado em z‑score temporal por talhão para identificar quebras de tendência.
4. **Padrão de dados** para exportação (GeoPackage/CSV/Parquet) visando integração rápida com dashboards (Metabase/Power BI).

## Impactos e diferenciais
- Acelera o monitoramento em escala municipal/estadual.
- Facilita a adoção por cooperativas e órgãos públicos (reprodutível, baixo custo).
- Base pronta para futura proteção de PI (métodos e combinações de features).

## Próximos passos
- Dash interativo com comparação de talhões no tempo.
- Expansão para detecção de nuvem/sombra via modelo leve.
- Avaliação de métricas agronômicas (fenologia, datas‑chave).

**Repositório GitHub:** _(inserir link após publicação)_
