import sys
import requests

winpython_url = "https://api.github.com/repos/winpython/winpython/releases/latest"

if __name__ == "__main__":

    with open("python_version.txt") as f:
        py_version = f.read()

    with open("winpython_version.txt") as f:
        wp_version = f.read()

    print("Currently using WinPython version: ", wp_version)    
    print("Which uses python version: ", py_version)
    
    r = requests.get(winpython_url)
    json = r.json()
          
    found = False
    for asset in json["assets"]:
        if asset["name"] == "Winpython32-" + py_version + "dot.exe":
            print("The latest WinPython version contains the current python version",
                  py_version,
                  ": there's nothing to do manually")
            found = True
        
    if json["tag_name"] == wp_version:
        print("Currently using the latest WinPython version: exiting with code 0")
    else:
        if not found:
            print("The new WinPython version does NOT have the current python version: exiting with code 2")
            sys.exit(2)
        else:
            print("The new Winpython version has the current python version: exiting with code 1")
            sys.exit(1)
