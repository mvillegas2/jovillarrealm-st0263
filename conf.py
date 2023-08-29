import os, json

def self_conf() -> dict[str,str]:
    file = os.path.join(os.getcwd(), "configure.json")
    with open(file) as jsconf:
        conf: dict = json.load(jsconf)
    return conf
