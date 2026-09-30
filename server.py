import base64
import binascii

from mcp.server import MCPServer

from hwp_reader import extract_hwp_text_bytes


mcp = MCPServer("HWP Reader")

MAX_HWP_SIZE = 20 * 1024 * 1024


@mcp.tool()
def check_server() -> str:
    """HWP Reader MCP 서버의 실행 상태를 확인합니다."""
    return "HWP Reader MCP 서버가 정상적으로 실행되었습니다."


@mcp.tool()
def read_hwp(file_data_base64: str) -> str:
    """
    Base64로 전달된 HWP 5.x 파일에서 본문과 표 셀의 텍스트를 추출합니다.
    """

    encoded_data = "".join(file_data_base64.split())

    try:
        hwp_bytes = base64.b64decode(encoded_data, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("올바른 Base64 형식의 HWP 데이터가 아닙니다.") from error

    if not hwp_bytes:
        raise ValueError("전달된 HWP 데이터가 비어 있습니다.")

    if len(hwp_bytes) > MAX_HWP_SIZE:
        raise ValueError("20MB를 초과하는 HWP 파일은 처리할 수 없습니다.")

    extracted_text = extract_hwp_text_bytes(hwp_bytes)

    if not extracted_text.strip():
        raise ValueError("HWP 파일에서 읽을 수 있는 본문을 찾지 못했습니다.")

    return extracted_text