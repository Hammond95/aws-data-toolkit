import os
import sys
import pytest
from pathlib import Path

cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from toolkit.aws.s3.path import S3Path


@pytest.mark.parametrize(
    "s3_path,prot,bucket,key,key_last",
    [
        ("s3://bucket", "s3", "bucket", "", ""),
        ("s3://bucket/", "s3", "bucket", "", ""),
        ("s3://bucket/key1/key2/", "s3", "bucket", "key1/key2/", "key2/"),
        (
            "s3://bucket/key1/key2/foobar",
            "s3",
            "bucket",
            "key1/key2/foobar",
            "foobar",
        ),
        ("s3a://bucket/key1/key2/", "s3a", "bucket", "key1/key2/", "key2/"),
    ],
)
def test_s3path_elements(s3_path, prot, bucket, key, key_last):
    s3p = S3Path(s3_path)

    assert s3p.prot == prot
    assert s3p.bucket == bucket
    assert s3p.key == key
    assert s3p.key_last_part == key_last

@pytest.mark.parametrize(
    "s3_path, exception",
    [
        ("bucket/key1/key2/", "Please provide a valid s3 url!"),
        ("bucket/", "Please provide a valid s3 url!"),
        ("bucket", "Please provide a valid s3 url!"),
    ],
)
def test_s3path_exceptions(s3_path, exception):
    with pytest.raises(ValueError) as exc:
        S3Path(s3_path)
    assert str(exc.value) == exception

@pytest.mark.parametrize(
    "s3_path,fullpath",
    [
        ("s3://bucket", "s3://bucket/"),
        ("s3://bucket/", "s3://bucket/"),
        ("s3://bucket/key1/key2/", "s3://bucket/key1/key2/"),
        ("s3://bucket/key1/key2/foobar", "s3://bucket/key1/key2/foobar"),
        ("s3a://bucket/key1/key2/", "s3a://bucket/key1/key2/"),
    ],
)
def test_s3path_fullpath(s3_path, fullpath):
    s3p = S3Path(s3_path)
    assert s3p.fullpath == fullpath


@pytest.mark.parametrize(
    "s3_path,result",
    [
        ("s3://bucket", False),
        ("s3://bucket/", False),
        ("s3://bucket/key1/key2/", False),
        ("s3://bucket/key1/key2/foobar", True),
        ("s3a://bucket/key1/key2/", False),
    ],
)
def test_s3path_isfile(s3_path, result):
    s3p = S3Path(s3_path)
    assert s3p.is_file() is result


@pytest.mark.parametrize(
    "s3_path,result",
    [
        ("s3://bucket", False),
        ("s3://bucket/", False),
        ("s3://bucket/key1/key2/", True),
        ("s3://bucket/key1/key2/foobar", False),
        ("s3a://bucket/key1/key2/", True),
    ],
)
def test_s3path_isfolder(s3_path, result):
    s3p = S3Path(s3_path)
    assert s3p.is_folder() is result


@pytest.mark.parametrize(
    "s3_path,result",
    [
        ("s3://bucket", True),
        ("s3://bucket/", True),
        ("s3://bucket/key1/key2/", False),
        ("s3://bucket/key1/key2/foobar", False),
        ("s3a://bucket/key1/key2/", False)
    ],
)
def test_s3path_isbucketonly(s3_path, result):
    s3p = S3Path(s3_path)
    assert s3p.is_bucket_only() is result


@pytest.mark.parametrize(
    "s3_path,s3_path_sub,local_path,result_subfolder,result_new_local_path",
    [
        (
            "s3://bucket/foo/bar/",
            "s3://bucket/foo/bar/baz/mimsy.txt",
            "/tmp/",
            "baz/",
            "/tmp/baz/",
        ),
        (
            "s3://bucket/foo/bar/",
            "s3://bucket/foo/bar/slithy_toves.txt",
            "/tmp/",
            "",
            "/tmp/",
        ),
    ],
)
def test_s3path_download_folder_logic(
    s3_path, s3_path_sub, local_path, result_subfolder, result_new_local_path
):
    lp = Path(local_path)
    s3p = S3Path(s3_path)
    nu_s3p = S3Path(s3_path_sub)
    subfolder = repr(nu_s3p).replace(repr(s3p), "").replace(nu_s3p.key_last_part, "")
    new_local_path = str(lp) + "/" + subfolder

    assert subfolder == result_subfolder
    assert new_local_path == result_new_local_path
