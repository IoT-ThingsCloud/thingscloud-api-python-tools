import click
from tools.create_devices import create_devices
from tools.export_devices_attributes_history import export_devices_attributes_history
from tools.export_devices import export_devices
from tools.export_devices_certificates import export_devices_certificates 
from lib.store import GlobalStore

@click.group()
@click.option('--log', is_flag=True, required=False, default=False, help='开启日志')
def main(log):
    store = GlobalStore()
    store.set_variable('log_enabled', log)
    pass

main.add_command(create_devices)
main.add_command(export_devices)
main.add_command(export_devices_attributes_history)
main.add_command(export_devices_certificates) 

if __name__ == "__main__":
    main()