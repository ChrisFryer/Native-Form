import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
timeout = 300
max_requests = 1000
max_requests_jitter = 50
accesslog = "/var/log/native-form/gunicorn-access.log"
errorlog = "/var/log/native-form/gunicorn-error.log"
loglevel = "info"
preload_app = True
