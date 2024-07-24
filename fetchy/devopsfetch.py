#!/usr/bin/env python3
import argparse
import psutil
import docker
import subprocess
import pwd
from prettytable import PrettyTable
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import textwrap

def get_active_ports(port_number=None):
    connections = psutil.net_connections()
    ports = []
    for conn in connections:
        if conn.status == 'LISTEN':
            try:
                process = psutil.Process(conn.pid)
                port_info = {
                    "Port": conn.laddr.port,
                    "Process": process.name(),
                    "PID": conn.pid,
                    "Status": conn.status
                }
                if not port_number or port_number == str(conn.laddr.port):
                    ports.append(port_info)
            except psutil.NoSuchProcess:
                pass
    return ports

def get_docker_info(container_name=None):
    try:
        client = docker.from_env()
        containers = client.containers.list()
        docker_info = []
        for container in containers:
            container_info = {
                "Container ID": container.short_id,
                "Name": container.name,
                "Image": container.image.tags[0] if container.image.tags else "None",
                "Status": container.status
            }
            if not container_name or container_name == container.name:
                docker_info.append(container_info)
        return docker_info
    except docker.errors.DockerException as e:
        print(f"Error connecting to Docker: {str(e)}")
        return []

def get_nginx_info(domain=None):
    nginx_conf_path = '/etc/nginx/nginx.conf'
    if not os.path.exists(nginx_conf_path):
        print("Nginx configuration file not found. Is Nginx installed?")
        return []
    
    nginx_info = []
    try:
        with open(nginx_conf_path, 'r') as file:
            server_block = False
            server_name = None
            listen = None
            root = None
            
            for line in file:
                if re.match(r'\s*server\s*{', line):
                    server_block = True
                    server_name = None
                    listen = None
                    root = None

                if server_block:
                    if re.match(r'\s*}', line):
                        server_block = False
                        if server_name and listen:
                            server_info = {
                                "Server Name": server_name,
                                "Listen": listen,
                                "Root": root if root else "Not specified"
                            }
                            if not domain or domain in server_name:
                                nginx_info.append(server_info)
                        server_name = None
                        listen = None
                        root = None
                    
                    match = re.match(r'\s*server_name\s+(.*);', line)
                    if match:
                        server_name = match.group(1)
                    
                    match = re.match(r'\s*listen\s+(.*);', line)
                    if match:
                        listen = match.group(1)
                    
                    match = re.match(r'\s*root\s+(.*);', line)
                    if match:
                        root = match.group(1)
    except Exception as e:
        print(f"Error reading Nginx configuration: {str(e)}")
        return []

    if not nginx_info:
        return [{"Message": "No Nginx server information found."}]
    return nginx_info

def get_user_info(username=None):
    users = []
    for user in pwd.getpwall():
        last_login = subprocess.getoutput(f"last -n 1 {user.pw_name} | head -n 1 | awk '{{print $4, $5, $6, $7}}'")
        user_info = {
            "Username": user.pw_name,
            "UID": user.pw_uid,
            "Home": user.pw_dir,
            "Last Login": last_login if last_login else "Never"
        }
        if not username or username == user.pw_name:
            users.append(user_info)
    return users

def get_activities_in_time_range(time_range):
    start_time_str, end_time_str = time_range.split(',')
    start_time = datetime.strptime(start_time_str.strip(), "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time_str.strip(), "%Y-%m-%d %H:%M:%S")

    log_file = '/var/log/syslog'  # Adjust to the relevant log file for your system
    activities = []

    try:
        with open(log_file, 'r') as file:
            for line in file:
                try:
                    timestamp_str = ' '.join(line.split()[:3])
                    timestamp = datetime.strptime(timestamp_str, '%b %d %H:%M:%S')
                    timestamp = timestamp.replace(year=start_time.year)
                    
                    if start_time <= timestamp <= end_time:
                        activities.append({
                            "Timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            "Activity": line.strip()
                        })
                except ValueError:
                    continue  # Skip lines that don't match the expected format
    except FileNotFoundError:
        print(f"Log file '{log_file}' not found.")
        return []

    if not activities:
        return [{"Message": "No activities found within the specified time range."}]
    return activities

def print_table(data, filter_value=None):
    if not data:
        print("No data available.")
        return

    table = PrettyTable()
    table.field_names = data[0].keys()

    # Determine the max width for each column based on the data
    max_lengths = {key: 0 for key in data[0]}  # Initialize with zero width
    for key in max_lengths:
        if key in {'Activity', 'Message'}:  # Special handling for long text fields
            max_lengths[key] = max(
                len(line) for row in data for line in textwrap.wrap(row.get(key, ''), width=80)
            ) if data else 0
        else:
            max_lengths[key] = max(len(str(row.get(key, ''))) for row in data) if data else 0

    # Add rows to the table with wrapped text for long fields
    for row in data:
        if not filter_value or filter_value in str(row.values()):
            # Wrap the text fields to fit within the column width
            for key in row:
                if key in {'Activity', 'Message'}:
                    row[key] = '\n'.join(textwrap.wrap(row.get(key, ''), width=80))
            table.add_row(row.values())

    # Manually adjust column widths based on the max lengths
    for field in table.field_names:
        if max_lengths[field] > 0:  # Only set width if it's greater than zero
            table.max_width[field] = max_lengths[field]

    print(table)

def continuous_monitoring():
    logging.basicConfig(
        handlers=[RotatingFileHandler('/var/log/devopsfetch.log', maxBytes=10000000, backupCount=5)],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    while True:
        ports = get_active_ports()
        docker_info = get_docker_info()
        nginx_info = get_nginx_info()
        user_info = get_user_info()

        logging.info("Active Ports: %s", ports)
        logging.info("Docker Info: %s", docker_info)
        logging.info("Nginx Info: %s", nginx_info)
        logging.info("User Info: %s", user_info)

        time.sleep(300)  # Sleep for 5 minutes before next check

def main():
    parser = argparse.ArgumentParser(description="DevOpsFetch - Server Information Retrieval and Monitoring Tool")
    parser.add_argument("-p", "--port", nargs='?', const='all', help="Display active ports or info about a specific port")
    parser.add_argument("-d", "--docker", nargs='?', const='all', help="Display Docker info or details about a specific container")
    parser.add_argument("-n", "--nginx", nargs='?', const='all', help="Display Nginx domains or config for a specific domain")
    parser.add_argument("-u", "--users", nargs='?', const='all', help="Display user info or details about a specific user")
    parser.add_argument("-t", "--time", help="Display activities within a specific time range (format: 'YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS')")
    parser.add_argument("--monitor", action="store_true", help="Run in continuous monitoring mode")

    args = parser.parse_args()

    if args.monitor:
        continuous_monitoring()
    elif args.port is not None:
        print_table(get_active_ports(None if args.port == 'all' else args.port))
    elif args.docker is not None:
        print_table(get_docker_info(None if args.docker == 'all' else args.docker))
    elif args.nginx is not None:
        print_table(get_nginx_info(None if args.nginx == 'all' else args.nginx))
    elif args.users is not None:
        print_table(get_user_info(None if args.users == 'all' else args.users))
    elif args.time:
        print_table(get_activities_in_time_range(args.time))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

