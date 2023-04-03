FROM nginx:1.23.3-alpine

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]
