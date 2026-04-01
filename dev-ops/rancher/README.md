TODO:
- secret for Redis credentials (not as YAML - it should not go to Git)
- secret for Postgres credentials (not as YAML - it should not go to Git)

deployment order:
- namespace (created via Rancher UI)
- logging-configurations.yml
- secrets
- grafana-dashboard.yml (error when creating "grafana-dashboards.yml": namespaces "cattle-monitoring-system" not found)
- redis.yml
- postgres.yml
- data-importer.yml
- master-data-service.yml (Mandatory environment variable 'PROMETHEUS_DISCOVERY_BASE_URL' is not defined)
- query-service.yml
