## 설치

### 1. pyenv 설치 (한 번만)

```bash
brew install pyenv

## 필요시 설치 (brew install pyenv 중간에 swig를 요구한다면 설치하는 게 안전)
brew install swig
```

`.zshrc` 맨 아래에 아래 추가:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

반영:

```bash
source ~/.zshrc
#확인
cat ~/.zshrc
```

---

### 2. Python 3.11 설치

```bash
pyenv install 3.11.8
```

설치 완료 후 프로젝트 디렉토리로 이동:

```bash
cd ~/Documents/project/llm-2025
pyenv local 3.11.8

#확인
python3 --version
```

---

### 3. 가상환경 생성 및 패키지 설치

```bash
## 기존 가상환경 확인
ls vectordb
## 있으면 제거
rm -rf vectordb

python3.11 -m venv vectordb
source vectordb/bin/activate
pip install -r requirements.txt
```

> requirements.txt는 FastAPI + Chroma + embedding 관련 패키지 포함

## 폴더 구조

```
llm-2025/
├── repo/                    # 💾 분석 대상 레포 (청크 추출 대상)
│   ├── file1.js
│   └── subfolder/
│       └── file2.py
│
├── data/                    # 📁 생성된 데이터 (embedding.json, FAISS index 등)
│   ├── embeddings.json
│   └── faiss_index.index
│
├── scripts/                 # ⚙️ 스크립트들
│   ├── chunk_and_embed.py  # 청크 & 임베딩 생성
│   └── build_faiss.py      # (다음 단계에서 만들 FAISS DB 저장용)
│
├── api/                     # 🚀 FastAPI 서버 (검색 API)
│   ├── main.py
│   └── ...
│
├── vscode-extension/       # 🧩 VSCode 플러그인 개발 폴더
│   └── ...
│
└── README.md                # 전체 설명

```

| 폴더                | 설명                                                          |
| ------------------- | ------------------------------------------------------------- |
| `repo/`             | 분석 대상 레포. 여기에 직접 클론해도 되고, 복사해서 넣어도 됨 |
| `data/`             | 생성된 임베딩, FAISS index, metadata 등 저장                  |
| `scripts/`          | 실행 가능한 Python 스크립트                                   |
| `api/`              | FastAPI 서버 구현                                             |
| `vscode-extension/` | VSCode 확장 개발용 코드                                       |
| `README.md`         | 실행 방법이나 설명 문서                                       |

## 실행

### embeddings.json 파일 생성

```
python scripts/chunk_and_embed.py
```

### FAISS 인덱스에 추가

```
python scripts/build_faiss.py
```

### 서버 실행

```
uvicorn api.main:app --reload
```

→ 기본 포트 http://127.0.0.1:8000
