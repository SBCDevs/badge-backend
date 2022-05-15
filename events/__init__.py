from fastapi import APIRouter
from os import listdir
import imp

router = APIRouter()
package_dir = "events/"

__module_list = listdir(package_dir)
__module_list.remove("__init__.py")
for module in __module_list:
    if module.split(".")[-1] == "py":
        imp.load_source("module", package_dir + module).setup(router)
