import json
import multiprocessing
import os

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
error_log_file = os.getenv("ERROR_LOG_FILE") or "-"
access_log_file = os.getenv("ACCESS_LOG_FILE") or None
syslog_conf = os.getenv("SYSLOG_ADDR") or None
use_bind = bind_env if bind_env else f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)

if syslog_conf and not (
    syslog_conf.startswith("unix://")
    or syslog_conf.startswith("udp://")
    or syslog_conf.startswith("tcp://")
):
    raise ValueError(f"Invalid syslog address: {syslog_conf}")

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = error_log_file
accesslog = access_log_file
syslog = syslog_conf is not None
syslog_addr = syslog_conf
timeout = 120

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
