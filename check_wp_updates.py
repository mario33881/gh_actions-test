import sys
import json
import typing
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message

winpython_url = "https://api.github.com/repos/winpython/winpython/releases/latest"


class Response(typing.NamedTuple):
    body: str
    headers: Message
    status: int
    error_count: int = 0

    def json(self) -> typing.Any:
        """
        Decode body's JSON.
        Returns:
            Pythonic representation of the JSON object
        """
        try:
            output = json.loads(self.body)
        except json.JSONDecodeError:
            output = ""
        return output


def request(
    url: str,
    data: dict = None,
    params: dict = None,
    headers: dict = None,
    method: str = "GET",
    data_as_json: bool = True,
    error_count: int = 0,
) -> Response:
    """
    Make a request without non-standard libraries
    """
    if not url.casefold().startswith("http"):
        raise urllib.error.URLError("Incorrect and possibly insecure protocol in url")
    method = method.upper()
    request_data = None
    headers = headers or {}
    data = data or {}
    params = params or {}
    headers = {"Accept": "application/json", **headers}

    if method == "GET":
        params = {**params, **data}
        data = None

    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True, safe="/")

    if data:
        if data_as_json:
            request_data = json.dumps(data).encode()
            headers["Content-Type"] = "application/json; charset=UTF-8"
        else:
            request_data = urllib.parse.urlencode(data).encode()

    httprequest = urllib.request.Request(
        url, data=request_data, headers=headers, method=method
    )

    try:
        with urllib.request.urlopen(httprequest) as httpresponse:
            response = Response(
                headers=httpresponse.headers,
                status=httpresponse.status,
                body=httpresponse.read().decode(
                    httpresponse.headers.get_content_charset("utf-8")
                ),
            )
    except urllib.error.HTTPError as e:
        response = Response(
            body=str(e.reason),
            headers=e.headers,
            status=e.code,
            error_count=error_count + 1,
        )

    return response


if __name__ == "__main__":

    # get python and winpython versions from their files
    with open("python_version.txt") as f:
        py_version = f.read().strip()

    with open("winpython_version.txt") as f:
        wp_version = f.read().strip()

    print("Currently using WinPython version: ", wp_version)    
    print("Which uses python version: ", py_version)
    
    # get data from the API
    r = request(winpython_url)
    json_data = r.json()
    
    # Check if an asset contains the same python version as the current winpython version
    found = False
    for asset in json_data["assets"]:
        if asset["name"] == "Winpython64-" + py_version + "dot.exe":
            print("The latest WinPython version contains the current python version",
                  py_version,
                  ": there's nothing to do manually")
            found = True
            break
    
    # exit with different exit codes to tell GH actions what to do next
    if json["tag_name"] == wp_version:
        # there are no winpython updates
        print("Currently using the latest WinPython version: exiting with code 0")
    else:
        # there are winpython updates
        if not found:
            # the python version is different
            print("The new WinPython version does NOT have the current python version: exiting with code 2")
            sys.exit(2)
        else:
            # the python version is the same
            print("The new Winpython version has the current python version: exiting with code 1")
            sys.exit(1)
