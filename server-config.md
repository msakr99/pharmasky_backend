# Server Configuration

## Production Server Details

### Server Information
- **IP Address**: 129.212.140.152
- **Protocol**: HTTP
- **Full URL**: http://129.212.140.152/

### SSH Access
- **SSH Key Type**: ed25519
- **SSH Public Key**: 
  ```
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICiYHpODLkXsNKxolkjyIN6xWhWULWKnvL8cyNaNr+Jp pharmasky-github-deploy
  ```
- **Key Name**: pharmasky-github-deploy

## Usage Instructions

### SSH Connection
To connect to the server via SSH:
```bash
ssh -i ~/.ssh/pharmasky-github-deploy root@129.212.140.152
```

### Setting up SSH Key on Server
If the key is not yet added to the server, you need to add it manually:

1. **Connect to server with password (if available):**
   ```bash
   ssh root@129.212.140.152
   ```

2. **Or through server console/panel, then add the public key:**
   ```bash
   mkdir -p ~/.ssh
   echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICiYHpODLkXsNKxolkjyIN6xWhWULWKnvL8cyNaNr+Jp pharmasky-github-deploy" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

### Deployment Process
1. Make your code changes locally
2. Push changes to the repository
3. SSH into the server
4. Pull the latest changes
5. Restart services if needed

## Security Notes
- This SSH key is for GitHub deployment purposes
- Keep this key secure and never share it publicly
- Make sure to use proper file permissions (600) for the private key

## Server Access
- Web URL: http://129.212.140.152/
- For HTTPS setup, consider configuring SSL/TLS certificates

---
**Last Updated**: September 28, 2025
**Environment**: Production Server
