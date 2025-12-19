# Cloudflare Tunnel Setup Guide

Expose your local backend API to the internet securely using Cloudflare Tunnel.

## Step 1: Install Cloudflared

### Windows
Download from: https://github.com/cloudflare/cloudflared/releases
Or use the included `cloudflared.exe` in the backend folder.

### Linux/Mac
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

## Step 2: Login to Cloudflare
```bash
cloudflared tunnel login
```
This opens a browser window. Select your domain.

## Step 3: Create a Tunnel
```bash
cloudflared tunnel create tradescanpro
```
Note the tunnel ID shown in the output.

## Step 4: Create Configuration File

Create `cloudflared_config.yml`:
```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: /path/to/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.tradescanpro.com
    service: http://localhost:8000
  - service: http_status:404
```

Replace:
- `YOUR_TUNNEL_ID_HERE` with your tunnel ID
- `/path/to/.cloudflared/` with actual path (shown after tunnel creation)
- `api.tradescanpro.com` with your actual domain

## Step 5: Configure DNS

Run this command or manually add DNS record in Cloudflare dashboard:
```bash
cloudflared tunnel route dns tradescanpro api.tradescanpro.com
```

## Step 6: Run the Tunnel

### Windows
```bash
cloudflared tunnel --config cloudflared_config.yml run tradescanpro
```

### Linux (as a service)
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## Step 7: Update Frontend Configuration

Update `frontend/.env.production`:
```
REACT_APP_API_URL=https://api.tradescanpro.com
```

## Verify Setup

Visit: `https://api.tradescanpro.com/api/stocks/`

You should see the API response.

## Troubleshooting

**Tunnel not connecting**: Check if Django server is running on port 8000
**502 Bad Gateway**: Backend server not responding, restart Django
**DNS not resolving**: Wait 5-10 minutes for DNS propagation
