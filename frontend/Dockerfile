FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

FROM node:20-alpine

WORKDIR /app

RUN yarn global add serve

COPY --from=builder /app/dist .

ENV PORT 10000

CMD ["serve", "-s", ".", "-l", "10000"]
