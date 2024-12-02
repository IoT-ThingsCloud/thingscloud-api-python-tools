from lib.store import GlobalStore

def log_info(message):
    store = GlobalStore()
    if store.get_variable('log_enabled'):
        print(f"[INFO] {message}")
        