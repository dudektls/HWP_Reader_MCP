# HWP Reader MCP

HWP 5.x 문서에서 본문과 표 셀의 텍스트를 추출하는 읽기 전용 MCP 서버입니다.
한컴오피스를 실행하지 않고 HWP의 OLE 내부 구조를 분석하며, 추출한 텍스트를 MCP 클라이언트가 요약이나 검색에 사용할 수 있도록 반환합니다.

## 주요 기능

- Base64로 전달된 HWP 5.x 파일 처리
- `FileHeader`를 이용한 파일 형식, 압축 여부, 암호화 여부 확인
- `BodyText/Section` 스트림의 Deflate 압축 해제
- `PARA_TEXT` 레코드에서 일반 문단과 표 셀 텍스트 추출
- HWP 제어문자 제거 및 UTF-16LE 문자열 변환
- 최대 20MB 입력 제한

## 처리 구조

```text
MCP 클라이언트
  1. HWP 파일을 Base64 문자열로 전달
  2. read_hwp Tool 호출

server.py
  3. Base64 문자열을 HWP 바이너리로 복원
  4. hwp_reader.py의 추출 함수 호출

hwp_reader.py
  5. OLE 구조와 BodyText 분석
  6. 문단과 표 셀 텍스트 추출

MCP 클라이언트
  7. 추출된 일반 텍스트 수신
```

## 프로젝트 구조

```text
HWP_Reader_MCP/
├─ server.py          # MCP Server 생성 및 Tool 등록
├─ hwp_reader.py      # HWP 5.x 본문 추출 로직
├─ requirements.txt   # Python 의존성
├─ .gitignore
└─ README.md
```

## 요구 사항

- Python 3.10 이상
- 테스트 환경: Python 3.13, MCP SDK 2.2.0
- 암호화되지 않은 HWP 5.x 파일

한컴오피스 설치는 필요하지 않습니다.

## 처음 설치하기

저장소를 복제한 뒤 프로젝트 전용 Python 가상환경을 만들고 필요한 패키지를 설치합니다.

```powershell
git clone https://github.com/dudektls/HWP_Reader_MCP.git
cd HWP_Reader_MCP

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

설치 후에는 아래의 **Codex STDIO 연결** 설정까지 완료해야 Tool을 사용할 수 있습니다. 저장소를 복제하는 것만으로는 MCP 서버가 Codex에 자동 등록되지 않습니다.

## 기존 설치 업데이트하기

이미 저장소를 복제하고 Codex 연결까지 마쳤다면 프로젝트 폴더에서 다음 명령을 실행합니다.

```powershell
git pull origin main
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

`git pull`은 최신 코드를 내려받는 작업입니다. `requirements.txt`가 변경되었을 가능성이 있으므로 의존성 설치 명령도 다시 실행하는 것이 안전합니다.

업데이트를 적용하려면 실행 중인 MCP 서버를 다시 시작합니다.

1. Codex 설정에서 `HWP_Reader` 스위치를 껐다가 다시 켭니다.
2. 새 대화에서 `check_server` Tool을 호출합니다.
3. 정상 실행 메시지가 나오면 최신 코드가 반영된 상태입니다.

가상환경이나 프로젝트 위치를 변경하지 않았다면 Codex 연결 정보를 다시 등록할 필요는 없습니다.

## MCP Inspector 실행

Inspector 개발 실행에는 `uv`가 필요합니다.

```powershell
.\.venv\Scripts\python.exe -m pip install uv
$env:Path = "$(Resolve-Path .\.venv\Scripts);$env:Path"
.\.venv\Scripts\mcp.exe dev .\server.py
```

브라우저에서 서버 연결 후 `Tools` 탭의 `check_server`와 `read_hwp`를 확인할 수 있습니다.

## Codex STDIO 연결

Codex에서 STDIO MCP 서버를 추가하고 다음 값을 입력합니다.

| 항목 | 값 |
|---|---|
| 이름 | `HWP_Reader` |
| 유형 | `STDIO` |
| 실행 명령 | `<프로젝트 절대 경로>\.venv\Scripts\mcp.exe` |
| 작업 디렉터리 | `<프로젝트 절대 경로>` |

인자는 다음 순서로 각각 추가합니다.

```text
run
<프로젝트 절대 경로>\server.py
--transport
stdio
```

환경 변수와 환경 변수 패스스루 항목은 비워 두어도 됩니다. Windows 경로에 공백이 포함되어 있어도 각 입력 칸에는 따옴표 없이 절대 경로를 입력합니다.

설정을 저장하고 `HWP_Reader` 스위치를 켠 뒤 다음과 같이 요청하여 연결을 확인합니다.

```text
HWP_Reader의 check_server 도구를 호출하고 결과를 알려줘.
```

정상적으로 연결되면 다음 메시지가 반환됩니다.

```text
HWP Reader MCP 서버가 정상적으로 실행되었습니다.
```

## 설치 후 확인 목록

- 저장소를 clone 또는 pull했는지 확인
- `.venv` 가상환경을 생성했는지 확인
- `requirements.txt`의 패키지를 설치했는지 확인
- Codex에 실행 명령, 인자, 작업 디렉터리를 등록했는지 확인
- MCP 서버 스위치를 켰는지 확인
- `check_server` Tool 호출이 성공하는지 확인

## 제공 Tool

### `check_server`

MCP 서버가 실행 중이며 Tool 호출이 가능한지 확인합니다. 입력은 없습니다.

```text
HWP Reader MCP 서버가 정상적으로 실행되었습니다.
```

### `read_hwp`

Base64로 인코딩된 HWP 데이터를 입력받아 본문과 표 셀의 텍스트를 반환합니다.

| 인자 | 형식 | 설명 |
|---|---|---|
| `file_data_base64` | `string` | Base64로 인코딩된 HWP 원본 데이터 |

처리 과정은 다음과 같습니다.

1. Base64 입력 형식 확인
2. HWP 바이너리 데이터 복원
3. HWP 5.x 시그니처와 암호화 여부 확인
4. `BodyText` 압축 해제
5. `PARA_TEXT` 레코드 디코딩
6. 추출된 텍스트 반환

## 활용 예시

Google Drive와 함께 사용할 경우 MCP 클라이언트가 다음 순서로 Tool을 호출할 수 있습니다.

```text
Google Drive Tool로 HWP 원본 조회
HWP 원본을 Base64로 read_hwp에 전달
HWP Reader MCP가 본문 텍스트 반환
LLM이 안건, 결정 사항, 후속 조치 요약
```

자연어 요청 예시는 다음과 같습니다.

```text
Drive의 회의록 폴더에서 직전 회의의 HWP 파일을 찾아
핵심 안건, 결정 사항, 할 일을 요약해줘. 조회만 해.
```

## 지원 범위와 제한 사항

지원 범위:

- HWP 5.x OLE 문서
- 일반 문단 텍스트
- 표 셀에 포함된 문단 텍스트
- 압축된 `BodyText` 스트림

현재 지원하지 않는 항목:

- HWPX
- DOCX와 PDF
- HWP 3.x 등 구형 형식
- 암호화된 HWP
- 이미지 속 문자
- 글꼴, 표 테두리, 셀 크기 등의 시각적 서식 복원
- 복잡한 병합 셀과 중첩 표의 정확한 구조 재현

이 서버는 문서의 시각적 레이아웃을 복원하기보다 LLM이 읽고 요약할 수 있는 텍스트 추출에 초점을 맞춥니다.

## 보안 및 데이터 처리

- 입력 파일을 디스크에 저장하지 않고 메모리에서 처리합니다.
- 파일 크기를 20MB로 제한합니다.
- 파일을 수정하거나 새 HWP 파일을 생성하지 않습니다.
- 민감한 문서는 신뢰할 수 있는 로컬 MCP 클라이언트 환경에서 처리하세요.
