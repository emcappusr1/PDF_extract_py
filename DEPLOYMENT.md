# Deployment Guide

This guide explains how to deploy the MCQ PDF Extractor API to a remote Linux server (e.g., AWS EC2, DigitalOcean Droplet, etc.) using Docker and secure it with SSL.

## prerequisites

- A Linux server (Ubuntu/Debian recommended)
- SSH access to the server (using PuTTY or terminal)
- Domain name pointed to your server's IP address (for SSL)

## 1. Connect to the Server

If you are using **PuTTY** on Windows:
1. Open PuTTY.
2. Enter your server's IP address in the "Host Name (or IP address)" field.
3. Ensure Port is 22 and Connection type is SSH.
4. Click "Open".
5. Log in with your username (usually `ubuntu` or `root`) and password/key.

## 2. Install Docker

Run the following commands on your server to install Docker:

```bash
# Update package index
sudo apt-get update

# Install prerequisite packages
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add the Docker repository
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package index again
sudo apt-get update

# Install Docker CE
sudo apt-get install -y docker-ce

# Verify Docker is running
sudo systemctl status docker
```

(Optional) Add your user to the docker group so you don't have to use `sudo` for every docker command:
```bash
sudo usermod -aG docker ${USER}
# Log out and log back in for changes to take effect
```

## 3. Deploy the Application

### Option A: Using Git (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t mcq-extractor .
   ```

3. **Run the container**:
   ```bash
   docker run -d -p 8001:8001 --restart unless-stopped --name mcq-api mcq-extractor
   ```
   - `-d`: Run in detached mode (background)
   - `-p 8001:8001`: Map port 8001 of the host to port 8001 of the container
   - `--restart unless-stopped`: Automatically restart the container if it crashes or the server reboots

### Option B: Transfer Files Directly (SCP)
If you don't use Git, you can upload files using WinSCP or `scp`. Upload all files **except** `venv`, `__pycache__`, etc.

## 4. Verify Deployment

Check if the application is running:
```bash
docker ps
```

View application logs:
```bash
docker logs -f mcq-api
```

You should see the message: `Uvicorn running on http://0.0.0.0:8001`.

## 5. Set up SSL with Nginx (Production)

To serve the API securely over HTTPS, use Nginx as a reverse proxy.

### Install Nginx
```bash
sudo apt-get install -y nginx
```

### Configure Nginx
Create a new configuration file:
```bash
sudo nano /etc/nginx/sites-available/mcq-api
```

Paste the following configuration (replace `your-domain.com` with your actual domain):

```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:
```bash
sudo ln -s /etc/nginx/sites-available/mcq-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Enable SSL (HTTPS) with Certbot

1. **Install Certbot**:
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   ```

2. **Obtain and Install Certificate**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
   Follow the prompts. Certbot will automatically configure SSL for you.

3. **Verify Auto-Renewal**:
   ```bash
   sudo certbot renew --dry-run
   ```

## 6. Access the API

Your API should now be accessible at:
- **HTTPS**: `https://your-domain.com`
- **Docs**: `https://your-domain.com/docs`
