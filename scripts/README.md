### extract_chunk.js
* vue class component 형식 파일 청크
* output: vue_chunks_ast.json

[ ] 함수 단위 청크하는 보조 파서 추가 

[ ] filePath 수정 

### annotate_chunk.py
* 성능 강화를 위해 llm으로 파일단위 청크에 메타데이터 기반 주석 생성해줌
* output: vue_chunks_annotated.json

[ ] max_input_length 수정 

[ ] 다양한 모델로 테스트 ? 

### embed_chunk.py
* 청크 파일을 임베딩해서 벡터모델에 저장 
* output: index.faiss, metadata 

### search_test.py
* 임베딩 모델 검색 테스트 

### 😩
[ ] 전체 index script 만들기 