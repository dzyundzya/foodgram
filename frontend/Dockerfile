FROM node:16.20
WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build
RUN npm install --global http-server

CMD ["npx", "-y", "http-server", "-p", "8090", "/app/build"]