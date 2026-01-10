FROM node:18-alpine

WORKDIR /app

COPY package.json .
COPY package-lock.json .
# If package-lock doesn't exist yet, it's fine, we can just copy package.json. 
# But usually created by create-vite.

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
