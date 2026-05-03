"""Kills processes based on ther listening port"""

import signal

import psutil


def get_pids_for_ports(ports):
    """Retrieve PIDs for processes listening on specified ports."""
    ports = {int(p) for p in ports}
    pids = set()

    for conn in psutil.net_connections(kind="tcp"):
        if conn.status == psutil.CONN_LISTEN and conn.laddr.port in ports and conn.pid is not None:
            pids.add(conn.pid)

    return pids

def kill_process(pid):
    """Attempt to kill a process by PID."""
    try:
        psutil.Process(pid).send_signal(signal.SIGTERM)
        print(f"✅ Process {pid} terminated.")
    except psutil.NoSuchProcess:
        print(f"⚠️ Process {pid} no longer exists.")
    except psutil.AccessDenied:
        print(f"❌ Access denied when trying to terminate process {pid}.")

def clean_ports(ports):
    """Clean processes associated with specified ports."""

    # Remove 'localhost:' part
    ports = [port.split(':')[1] for port in ports]

    print(f"Cleaning ports: {ports}\n")

    pids = get_pids_for_ports(ports)
    if not pids:
        print("No processes found for the specified ports.\n")
        return

    for pid in pids:
        kill_process(pid)
    print()
