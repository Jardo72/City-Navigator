@cls
@echo ""
@echo "**************************************************"
@echo " Starting the build"
@echo "**************************************************"
@time /T

@pushd data-importer
@echo "Going to build data-importer"
docker build -t jardo72/city-navigator-data-importer:latest .
docker push jardo72/city-navigator-data-importer:latest
@popd

@pushd master-data-service
@echo "Going to build master-data-service"
docker build -t jardo72/city-navigator-master-data-service:latest .
docker push jardo72/city-navigator-master-data-service:latest
@popd

@pushd query-service
@echo "Going to build query-service"
docker build -t jardo72/city-navigator-query-service:latest .
docker push jardo72/city-navigator-query-service:latest
@popd

@pushd http-service-discovery
@echo "Going to build HTTP service discovery"
docker build -t jardo72/city-navigator-http-service-discovery:latest .
docker push jardo72/city-navigator-http-service-discovery:latest
@popd

@pushd postgres
@echo "Going to build PostgreSQL"
docker build -t jardo72/city-navigator-postgres:latest .
docker push jardo72/city-navigator-postgres:latest
@popd

@echo ""
@echo "**************************************************"
@echo " Build completed"
@echo "**************************************************"
@time /T
