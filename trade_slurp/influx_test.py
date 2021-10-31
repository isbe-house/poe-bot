import poe_lib

x = poe_lib.Influx()

x.write('test', 'my_test', {'temperature': 500})