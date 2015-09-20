from __future__ import absolute_import, print_function, division
from netlib.exceptions import HttpException
from netlib.http import CONTENT_MISSING, Headers
from netlib.http.http1.assemble import (
    assemble_request, assemble_request_head, assemble_response,
    assemble_response_head, _assemble_request_line, _assemble_request_headers,
    _assemble_response_headers,
    assemble_body)
from netlib.tutils import treq, raises, tresp


def test_assemble_request():
    c = assemble_request(treq()) == (
        b"GET /path HTTP/1.1\r\n"
        b"header: qvalue\r\n"
        b"Host: address:22\r\n"
        b"Content-Length: 7\r\n"
        b"\r\n"
        b"content"
    )

    with raises(HttpException):
        assemble_request(treq(body=CONTENT_MISSING))


def test_assemble_request_head():
    c = assemble_request_head(treq())
    assert b"GET" in c
    assert b"qvalue" in c
    assert b"content" not in c


def test_assemble_response():
    c = assemble_response(tresp()) == (
        b"HTTP/1.1 200 OK\r\n"
        b"header-response: svalue\r\n"
        b"Content-Length: 7\r\n"
        b"\r\n"
        b"message"
    )

    with raises(HttpException):
        assemble_response(tresp(body=CONTENT_MISSING))


def test_assemble_response_head():
    c = assemble_response_head(tresp())
    assert b"200" in c
    assert b"svalue" in c
    assert b"message" not in c


def test_assemble_body():
    c = list(assemble_body(Headers(), [b"body"]))
    assert c == [b"body"]

    c = list(assemble_body(Headers(transfer_encoding="chunked"), [b"123456789a", b""]))
    assert c == [b"a\r\n123456789a\r\n", b"0\r\n\r\n"]

    c = list(assemble_body(Headers(transfer_encoding="chunked"), [b"123456789a"]))
    assert c == [b"a\r\n123456789a\r\n", b"0\r\n\r\n"]


def test_assemble_request_line():
    assert _assemble_request_line(treq()) == b"GET /path HTTP/1.1"

    authority_request = treq(method=b"CONNECT", form_in="authority")
    assert _assemble_request_line(authority_request) == b"CONNECT address:22 HTTP/1.1"

    absolute_request = treq(form_in="absolute")
    assert _assemble_request_line(absolute_request) == b"GET http://address:22/path HTTP/1.1"

    with raises(RuntimeError):
        _assemble_request_line(treq(), "invalid_form")


def test_assemble_request_headers():
    # https://github.com/mitmproxy/mitmproxy/issues/186
    r = treq(body=b"")
    r.headers[b"Transfer-Encoding"] = b"chunked"
    c = _assemble_request_headers(r)
    assert b"Transfer-Encoding" in c

    assert b"Host" in _assemble_request_headers(treq(headers=Headers()))


def test_assemble_response_headers():
    # https://github.com/mitmproxy/mitmproxy/issues/186
    r = tresp(body=b"")
    r.headers["Transfer-Encoding"] = b"chunked"
    c = _assemble_response_headers(r)
    assert b"Transfer-Encoding" in c