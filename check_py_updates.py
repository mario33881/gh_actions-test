import json
import typing
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message

winpython_url = "https://api.github.com/repos/winpython/winpython/releases/latest"


class Version:
    """
    Represents and parses a version string.
    """
    def __init__(self, t_version_string):
        self.major = None
        self.minor = None
        self.bug_fix = None
        self.post_rel_fix = None

        self.parse(t_version_string)

    def parse(self, t_version_string):
        """
        Parses the version from <t_version_string>.
        """
        version_list = t_version_string.split(".")
        if len(version_list) != 4:
            raise Exception("<t_version_string> must be in this format: x.y.w.z")
        
        self.major = version_list[0]
        self.minor = version_list[1]
        self.bug_fix = version_list[2]
        self.post_rel_fix = version_list[3]


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
    with open("python_version.txt", "r") as f:
        py_version = f.read().strip()

    # print("Currently using python version: ", py_version)

    current_version = Version(py_version)
    
    # get data from the API
    r = request(winpython_url)
    json_data = r.json()
    
    # try to find the best match to this current version
    confidence_level = 0
    best_match = None

    for asset in json_data["assets"]:
        asset_name = asset["name"]

        if asset_name.startswith("Winpython64-") and asset_name.endswith("dot.exe"):

            asset_version = asset_name.replace("Winpython64-").replace("dot.exe", "")
            if confidence_level == 0:
                confidence_level = 1
                best_match = asset_version

            new_version = Version(asset_version)

            if new_version.major == current_version.major:
                if confidence_level == 1:
                    confidence_level = 2
                    best_match = asset_version
                
                if new_version.minor == current_version.minor:
                    if confidence_level == 2:
                        confidence_level = 3
                        best_match = asset_version

                    if new_version.bug_fix == current_version.bug_fix:
                        if confidence_level == 3:
                            confidence_level = 4
                            best_match = asset_version
                        
                        if new_version.post_rel_fix == current_version.post_rel_fix:
                            if confidence_level == 4:
                                confidence_level = 5
                                best_match = asset_version
                                break

    print("{};{}".format(confidence_level, best_match), end="")
