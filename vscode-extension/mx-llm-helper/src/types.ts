export interface SearchResponse {
  question: string;
  status: "ok" | "error";
  results: any[]; // 실제 결과 타입에 맞게 수정 필요
}

export interface SearchRequest {
  question: string;
  selectedText?: string; // 선택된 텍스트
  currentFile?: {
    // 현재 파일 정보
    content: string;
    path: string;
    language: string;
  };
}
