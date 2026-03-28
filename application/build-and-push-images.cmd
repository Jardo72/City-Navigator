@cls
@echo ""
@echo "**************************************************"
@echo " Starting the build"
@echo "**************************************************"
@time /T

@echo "Going to build data-importer"
docker build -f data-importer/Dockerfile -t jardo72/city-navigator-data-importer:latest data-importer
docker push jardo72/city-navigator-data-importer:latest

@echo "Going to build master-data-service"
docker build -f master-data-service/Dockerfile -t jardo72/city-navigator-master-data-service:latest .
docker push jardo72/city-navigator-master-data-service:latest

@echo "Going to build query-service"
docker build -f query-service/Dockerfile -t jardo72/city-navigator-query-service:latest .
docker push jardo72/city-navigator-query-service:latest

@echo "Going to build HTTP service discovery"
docker build -f http-service-discovery/Dockerfile -t jardo72/city-navigator-http-service-discovery:latest .
docker push jardo72/city-navigator-http-service-discovery:latest

@echo "Going to build PostgreSQL"
docker build -f postgres/Dockerfile -t jardo72/city-navigator-postgres:latest postgres
docker push jardo72/city-navigator-postgres:latest

@echo ""
@echo "**************************************************"
@echo " Build completed"
@echo "**************************************************"
@time /T
