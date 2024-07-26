# DevOpsFetch

**DevOpsFetch** is a tool designed with Python exclusively for DevOps professionals to collect and display essential system information. This tool supports retrieving details about active ports, Docker containers, Nginx configurations, user logins, and system activities within a specified time range. Additionally, it offers continuous monitoring and logging capabilities via a systemd service.

## Objective

To develop a tool that provides:
- Active ports and services
- Docker images and container statuses
- Nginx configurations
- User logins and details
- System activities within a time range

## Requirements

### Information Retrieval

1. **Ports:**
   - `-p` or `--port`: Display all active ports and services.
   - `-p <port_number>`: Provide detailed information about a specific port.

2. **Docker:**
   - `-d` or `--docker`: List all Docker images and containers.
   - `-d <container_name>`: Provide detailed information about a specific container.

3. **Nginx:**
   - `-n` or `--nginx`: Display all Nginx domains and their ports.
   - `-n <domain>`: Provide detailed configuration information for a specific domain.

4. **Users:**
   - `-u` or `--users`: List all users and their last login times.
   - `-u <username>`: Provide detailed information about a specific user.

5. **Time Range:**
   - `-t` or `--time`: Display activities within a specified time range in the format `YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS`.

### Output Formatting

- Outputs are formatted in well-structured tables for clarity, with descriptive column names and text wrapping to ensure readability.

## Installation

To install and set up DevOpsFetch, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone  https://github.com/fortis-07/DevOps_Fetch
   cd fetchy
   ```
2. **Install Dependencies**
  ```bash sudo apt-get update
sudo apt-get install -y python3 python3-pip
pip3 install -r requirements.txt
```
3. **Install the Script**
   
```bash
 sudo ./install.sh
```

```bash   sudo cp devopsfetch.py /usr/local/bin/devopsfetch
sudo chmod +x /usr/local/bin/devopsfetch
```
4. ***Set Up Systemd Service**
```bash sudo cp devopsfetch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable devopsfetch.service
sudo systemctl start devopsfetch.service
```
## Usage

DevOpsFetch can be used with various command-line flags:

### Port Information
- Display all active ports:
```bash
sudo devopsfetch -p
```
- Display information for a specific port:
```bash
sudo devopsfetch -p 80
```
### Docker Information
- List all Docker images and containers:
```bash
sudo devopsfetch -d
```
- Display information for a specific container:
  
```bash
sudo devopsfetch -d my_container_name
```
### Nginx Information
- Display all Nginx domains and their ports:

```bash
devopsfetch -n
```

#- Display configuration for a specific domain
```bash
devopsfetch -n example.com
```
### User Information
- List all users and their last login times:

```bash
sudo devopsfetch -u
```
### Time Range Activities
- Display system activities within a specified time range:
```bash
sudo devopsfetch -t "YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS"
```
### Help
- Display usage instructions:

```bash
sudo devopsfetch -h
```
### Logging Mechanism

DevOpsFetch uses systemd for logging. Logs are stored in the system journal and a dedicated log file.

To view the systemd service logs:

```bash
sudo journalctl -u devopsfetch.service
```

To view the dedicated log file:
```bash
sudo cat /var/log/devopsfetch.log
```
Logging
Logs for continuous monitoring are stored in /var/log/devopsfetch.log. To view the logs, you can use:

```bash
sudo cat /var/log/devopsfetch.log
```


