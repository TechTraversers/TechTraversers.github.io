FROM node:22-alpine
WORKDIR /app
COPY package.json server.mjs ./
COPY scripts/build-public.mjs ./scripts/build-public.mjs
COPY sitemap.xml robots.txt style.css script.js contact.js index.html ./
COPY aboutus ./aboutus
COPY contact ./contact
COPY ourservices ./ourservices
COPY ourvalues ./ourvalues
COPY wood-bank-software ./wood-bank-software
COPY work ./work
COPY assets ./assets
RUN node scripts/build-public.mjs
USER node
ENV NODE_ENV=production
CMD ["node", "server.mjs"]
