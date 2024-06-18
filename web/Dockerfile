# Use Node.js image as base
FROM node:alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Build project
RUN npm run build

# Expose port
EXPOSE 8082

# Start server
CMD ["npm", "start"]
