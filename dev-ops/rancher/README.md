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
- master-data-service.yml
- query-service.yml
- ingress.yml
- servicemonitor.yml (unknown CRD - monitoring not installed)

ingress testing:
- execute `kubectl get ingress -n city-navigator` to get the IP address(es)
- map the IP address(es) to the hostname `city-navigator.jch` in your /etc/hosts (or its Windows equivalent)
- try the following queries
  - http://city-navigator.jch/api/query/means-of-transport
  - http://city-navigator.jch/api/query/stations
  - http://city-navigator.jch/api/query/lines
  - http://city-navigator.jch/api/query/journey-plan?start=Traisengasse&destination=Nordwestbahnstrasse
