"""LOB offset and length must be true ints before any packet I/O (#449)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pycubrid.constants import CUBRIDDataType
from pycubrid.exceptions import InterfaceError
from pycubrid.lob import Lob
from pycubrid.protocol import LOBReadPacket, LOBWritePacket


@pytest.fixture
def mock_connection() -> MagicMock:
    connection = MagicMock()
    connection._ensure_connected = MagicMock()

    def send_and_receive(packet: object) -> object:
        if isinstance(packet, LOBWritePacket):
            packet.bytes_written = len(packet.data)
        if isinstance(packet, LOBReadPacket):
            packet.lob_data = b""
            packet.bytes_read = 0
        return packet

    connection._send_and_receive = MagicMock(side_effect=send_and_receive)
    return connection


@pytest.mark.parametrize("value", [True, False, 1.5, 0.0, "1", "0"])
def test_read_rejects_non_int_length(mock_connection: MagicMock, value: object) -> None:
    lob = Lob(mock_connection, CUBRIDDataType.BLOB, b"lob-handle")
    with pytest.raises(InterfaceError, match="length must be an int"):
        lob.read(value)
    mock_connection._ensure_connected.assert_not_called()
    mock_connection._send_and_receive.assert_not_called()


@pytest.mark.parametrize("value", [True, False, 1.5, 0.0, "1"])
def test_read_rejects_non_int_offset(mock_connection: MagicMock, value: object) -> None:
    lob = Lob(mock_connection, CUBRIDDataType.BLOB, b"lob-handle")
    with pytest.raises(InterfaceError, match="offset must be an int"):
        lob.read(1, offset=value)
    mock_connection._ensure_connected.assert_not_called()
    mock_connection._send_and_receive.assert_not_called()


@pytest.mark.parametrize("value", [True, False, 1.5, 0.0, "1"])
def test_write_rejects_non_int_offset(mock_connection: MagicMock, value: object) -> None:
    lob = Lob(mock_connection, CUBRIDDataType.BLOB, b"lob-handle")
    with pytest.raises(InterfaceError, match="offset must be an int"):
        lob.write(b"x", offset=value)
    mock_connection._ensure_connected.assert_not_called()
    mock_connection._send_and_receive.assert_not_called()


def test_read_zero_still_returns_empty_without_send(mock_connection: MagicMock) -> None:
    lob = Lob(mock_connection, CUBRIDDataType.BLOB, b"lob-handle")
    assert lob.read(0) == b""
    mock_connection._send_and_receive.assert_not_called()
