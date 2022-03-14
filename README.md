# Postgresql proxy checker
Python code to allow a proxy, for example HAProxy to check health of a Postgresql server


## Requirements for the checker

 - Determine if we can connect or not 
 - Determine if the server is included in replication
 - Determine if the server is in recovery mode
 - If success, return a valid http response ( 200 OK ), or if it fails, return a 503
 - Allow server to be disabled

## How to setup 

## Config file 
```
[test2]
hostname=test
port=5432
user=monitoring
password=testpasswd
```

### Create database user 
### Setup systemd
### Setup HaProxy