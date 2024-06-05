# -*- coding: utf-8 -*-
import bs
import os
import json
import time

cmd_logs = []
env = bs.getEnvironment()['userScriptsDirectory']
path = os.path.join(env, 'data')
stats = os.path.join(path, 'stats.json')
pStats = os.path.join(path, 'pStats.json')
bank = os.path.join(path, 'banks.json')
customers = os.path.join(path, 'effectCustomers.json')
cmdlogfile = os.path.join(path, 'cmdlog.txt')
roles = os.path.join(path, 'roles.json')

# print(ver_roles())
class storage:
    customers = {}
    roles = {}


# creamos una lista con todos los archivos
myfiles = [stats, pStats, bank, roles, customers]

# creamos este diccionario vacio para poder guardar los archivos
empty = {}

# creamos el directorio
if not os.path.exists(path):
    os.mkdir(path)

def get_admin_list():
    f = open(roles, 'r')
    admins = json.load(f)
    allAdmins = []
    for k, v in admins.items():
        if k in ["admins", "owners"]:
            allAdmins.extend(v)
    return allAdmins



def log(name, msg, id, path):
    global cmd_logs
    if id not in get_admin_list():
        # solo guarda el registro de los que si son admins
        return
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = u"{}: {} | id: {} | date: {}\n".format(name, msg, id, current_time)
    cmd_logs.append(log_entry)
    if len(cmd_logs) == 3:
        try:
            with open(path, 'a+') as f:
                f.writelines(cmd_logs)
            #print("log creado correctamente!") #debug
        except Exception as e:
            bs.printException(e)


# test
#log(name="hola", msg="/end", id="89813", path=cmdlogfile)


def create(files):
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write(json.dumps(empty, indent=4))
                f.close()


create(myfiles)
