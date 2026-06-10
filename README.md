# Multi-Language Microservices with Nginx Reverse Proxy

A production-ready architecture demonstrating **Nginx** configured as an **API Gateway, Reverse Proxy, and Load Balancer**. It routes incoming client requests to three backend applications written in different programming languages: **Node.js (Express)**, **Python (Flask)**, and **Java (Native HttpServer)**. The entire stack is fully containerized and orchestrated using **Docker Compose**.

---

## 🏗️ Architecture Overview

The following diagram illustrates the routing mechanism, upstream configurations, load-balancing policies, and container network layout:

```mermaid
graph TD
    Client([🌐 Client / Browser]) -->|HTTP Port 80| Nginx[🔒 Nginx API Gateway]

    subgraph Docker Bridge Network: backend-network
        Nginx -->|/api/node/* <br> least_conn| NodeUpstream[Node.js Upstream]
        Nginx -->|/api/python/* <br> rate limit: 10r/s| PythonBackend[🐍 backend-python:5000]
        Nginx -->|/api/java/*| JavaBackend[☕ backend-java:8080]

        subgraph Node.js Cluster (Load Balanced)
            NodeUpstream -->|Weight: 3| Node1[Node Instance 1 <br> backend-node-1:3000]
            NodeUpstream -->|Weight: 2| Node2[Node Instance 2 <br> backend-node-2:3001]
        end
    end

    classDef gateway fill:#2196F3,stroke:#1E88E5,stroke-width:2px,color:#fff;
    classDef service fill:#4CAF50,stroke:#43A047,stroke-width:2px,color:#fff;
    classDef client fill:#FFC107,stroke:#FFB300,stroke-width:2px,color:#000;
    class Nginx gateway;
    class Node1,Node2,PythonBackend,JavaBackend service;
    class Client client;
```

---

## ✨ Features Implemented

1. **Unified Routing / API Gateway**: Client interactions are directed to a single entry point (Port `80`). Nginx forwards requests to the correct backend depending on the request subpath.
2. **Node.js Load Balancing**: Configured with the `least_conn` routing algorithm, sending requests to the server with the fewest active connections while using server weights (`weight=3` for Instance 1, `weight=2` for Instance 2).
3. **Rate Limiting**: Python endpoints are protected using Nginx request rate limiting (`10r/s` with a burst buffer capacity of `20` requests).
4. **WebSocket Compatibility**: Includes dynamic handling of the `Connection` and `Upgrade` headers via an Nginx `map` block, preventing Rest API connection issues while staying WebSocket-ready.
5. **Optimized Docker Builds**: The Java backend leverages a **multi-stage build** using JDK 17 for compilation and a lightweight JRE 17 Alpine image for runtime execution, minimizing the final image size and reducing security vulnerabilities.
6. **Robust Forwarded Headers**: Preserves client contexts by forwarding standard headers:
   * `Host`
   * `X-Real-IP`
   * `X-Forwarded-For`
   * `X-Forwarded-Proto`
7. **Normalized Path Trailing Slashes**: Automatically redirects requests without trailing slashes (e.g. `/api/node`) to their trailing slash equivalent (e.g. `/api/node/`) to ensure proper route matching.
8. **Standardized Docker Logging**: Configured access and error logs to stream to `/var/log/nginx/access.log` and `/var/log/nginx/error.log`, redirecting output directly to standard stdout/stderr for retrieval via `docker logs`.

---

## 📂 Project Structure

```text
3.ReverseProxy-2/
├── backend1-node/          # Node.js backend service (Express)
│   ├── app.js              # Application server logic
│   ├── Dockerfile          # Builds Node 22 Alpine image
│   └── package.json        # Dependencies & start script
├── backend2-python/        # Python backend service (Flask)
│   ├── app.py              # Application server logic
│   ├── Dockerfile          # Builds Python 3.11 Slim image
│   └── requirements.txt    # Flask dependency
├── backend3-java/          # Java backend service (Native HttpServer)
│   ├── Main.java           # Native HTTP server logic
│   └── Dockerfile          # Multi-stage JDK 17 / JRE 17 Alpine build
├── nginx/                  # Nginx API Gateway files
│   ├── nginx.conf          # Gateway configuration & proxy settings
│   └── Dockerfile          # Builds Nginx Alpine container
├── docker-compose.yml      # Orchestration config for all services
└── README.md               # Documentation (This file)
```

---

## 🚀 Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running on your machine)
* Docker Compose CLI

### Run the Stack
1. Clone or navigate to the project root directory:
   ```bash
   cd 3.ReverseProxy-2
   ```
2. Build and launch all services in detached mode:
   ```bash
   docker compose up --build -d
   ```
3. Verify that all 5 containers are running:
   ```bash
   docker compose ps
   ```

---

## 🗺️ API Reference & Gateway Routing

| Entrypoint Gateway Path | Destination Server / Port | Language/Tech | HTTP Method | Example Response |
| :--- | :--- | :--- | :--- | :--- |
| **`GET /`** | Nginx Gateway (Direct) | Nginx Config | `GET` | `"Welcome to API Gateway"` |
| **`GET /health`** | Nginx Gateway (Direct) | Nginx Config | `GET` | `"healthy"` |
| **`GET /api/node/`** | `node_backend` cluster:3000/3001 | Node.js / Express | `GET` | Service info metadata & hostname |
| **`GET /api/node/users`** | `node_backend` cluster:3000/3001 | Node.js / Express | `GET` | A list of user objects |
| **`POST /api/node/users`** | `node_backend` cluster:3000/3001 | Node.js / Express | `POST` | Confirmation of created user payload |
| **`GET /api/python/`** | `backend-python`:5000 | Python / Flask | `GET` | Flask service metadata & timestamp |
| **`GET /api/python/products`** | `backend-python`:5000 | Python / Flask | `GET` | A list of products |
| **`POST /api/python/products`**| `backend-python`:5000 | Python / Flask | `POST` | Confirmation of product creation |
| **`GET /api/java/`** | `backend-java`:8080 | Java / Native Server | `GET` | Java service metadata |
| **`GET /api/java/orders`** | `backend-java`:8080 | Java / Native Server | `GET` | A list of active orders |

---

## 🧪 Testing with cURL

Once the stack is running, you can test the configurations using the following command examples:

### 1. Test Gateway Index & Health Checks
```bash
curl http://localhost/
# Output: Welcome to API Gateway

curl http://localhost/health
# Output: healthy
```

### 2. Test Trailing Slash Auto-Redirection
Request the Node endpoint without a trailing slash. Nginx will return a `301 Moved Permanently` redirecting to the correct location:
```bash
curl -I http://localhost/api/node
# Look for: Location: http://localhost/api/node/
```

### 3. Test Load Balancing (Node.js)
Call the Node index path repeatedly. Because of the `least_conn` upstream block and distinct hostnames, you will see the host alternate between `node-backend-1` and `node-backend-2`:
```bash
curl http://localhost/api/node/
```

### 4. Test Python Rate Limiting
Python requests are rate-limited. If you spam the endpoint rapidly, you will receive `503 Service Temporarily Unavailable`:
```bash
# Example test script to hit python server multiple times
for i in {1..30}; do curl -I http://localhost/api/python/products; done
```

### 5. Inspect Container Stream Logs
Retrieve consolidated standard logs directly from Nginx:
```bash
docker compose logs reverse-proxy
```

---

## ⚙️ Configuration Highlight: Dynamic WebSocket Upgrades
Standard reverse proxy setups hardcode `Connection 'upgrade'` and `Upgrade $http_upgrade`, which can terminate connections on standard REST servers. To avoid this, we map variables dynamically:
```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
```
Inside the server proxy location blocks, we proxy using:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;
```
If a request is standard HTTP, it sends `Connection: close`. If it's a WebSocket handshake, it sends `Connection: upgrade`.
