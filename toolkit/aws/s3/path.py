import copy
from urllib.parse import urlparse


class S3Path(object):

    def __init__(self, url):
        self._parsed = urlparse(url, allow_fragments=False)

        if (self._parsed.scheme == '') or (self._parsed.netloc == ''):
            raise ValueError("Please provide a valid s3 url!")

    @property
    def prot(self):
        return self._parsed.scheme

    @property
    def bucket(self):
        return self._parsed.netloc

    @property
    def key(self):
        if self._parsed.query:
            return self._parsed.path.lstrip('/') + '?' + self._parsed.query
        else:
            return self._parsed.path.lstrip('/')

    @property
    def fullpath(self):
        if self.is_bucket_only():
            return self._parsed.geturl().rstrip("/") + "/"
        return self._parsed.geturl()

    @property
    def key_last_part(self):
        if self.is_folder():
            return "/".join(self.key.split("/")[-2:])
        return self.key.rpartition('/')[-1]

    @classmethod
    def from_s3path(cls, obj: "S3Path"):
        if isinstance(obj, S3Path):
            return copy.deepcopy(obj)
        else:
            return None

    def __repr__(self) -> str:
        return self.fullpath

    def __str__(self) -> str:
        return self.fullpath

    def __eq__(self, other) -> bool:
        return isinstance(other, S3Path) and (repr(self) == repr(other))

    def is_bucket_only(self) -> bool:
        if self.bucket and (self.key == ""):
            return True
        return False

    def is_file(self) -> bool:
        if not self.is_bucket_only():
            return (not self._parsed.path.endswith("/")) and self.key != ""
        return False

    def is_folder(self) -> bool:
        if not self.is_bucket_only():
            return self._parsed.path.endswith("/")
        return False

