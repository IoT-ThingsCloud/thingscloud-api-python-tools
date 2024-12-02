import click
from tools.export_devices_attributes_history import export_devices_attributes_history
from lib.store import GlobalStore

@click.group()
@click.option('--log', is_flag=True, required=False, default=False, help='开启日志')
def main(log):
    store = GlobalStore()
    store.set_variable('log_enabled', log)
    pass

main.add_command(export_devices_attributes_history)

if __name__ == "__main__":
    main()