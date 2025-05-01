from flask import Flask, render_template
import psutil
import time

app = Flask(__name__)

# Récupération des informations système
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent

def get_process_count():
    return len(psutil.pids())

def get_uptime():
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            return temps['coretemp'][0].current  # Température du CPU pour systèmes Linux
    except Exception as e:
        return "N/A"  # En cas d'erreur

def get_network_info():
    net = psutil.net_if_addrs()
    ip = net.get('eth0', None)  # Assure-toi que 'eth0' est le bon nom d'interface sur ta machine
    ip_address = ip[0].address if ip else "N/A"
    net_stats = psutil.net_io_counters()
    return ip_address, net_stats.bytes_sent, net_stats.bytes_recv

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.device] = {
            'total': usage.total / (1024 ** 3),  # Conversion en Go
            'used': usage.used / (1024 ** 3),
            'free': usage.free / (1024 ** 3),
            'percent': usage.percent
        }
    return disk_info

def get_swap_memory():
    swap = psutil.swap_memory()
    return swap.used / (1024 ** 3), swap.free / (1024 ** 3), swap.percent  # En Go

def get_threads():
    return psutil.cpu_count(logical=False)

def get_logical_cpus():
    return psutil.cpu_count(logical=True)

@app.route('/')
def index():
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()
    process_count = get_process_count()
    uptime = get_uptime()
    cpu_temp = get_cpu_temp()
    ip_address, bytes_sent, bytes_recv = get_network_info()
    disk_info = get_disk_info()
    swap_used, swap_free, swap_percent = get_swap_memory()
    threads = get_threads()
    logical_cpus = get_logical_cpus()

    return render_template('index.html', cpu_usage=cpu_usage, memory_usage=memory_usage,
                           disk_usage=disk_usage, process_count=process_count, uptime=uptime,
                           cpu_temp=cpu_temp, ip_address=ip_address, disk_info=disk_info,
                           swap_used=swap_used, swap_free=swap_free, swap_percent=swap_percent,
                           threads=threads, logical_cpus=logical_cpus)

if __name__ == '__main__':
    app.run(debug=True)
