FROM node:16 as builder

EXPOSE 4000

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

#nginx gateway
FROM nginx

WORKDIR /app

COPY --from=builder /app/dist /usr/share/nginx/html/

CMD ["nginx", "-g", "daemon off;"]