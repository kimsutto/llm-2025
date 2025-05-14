import { SearchRequest, SearchResponse } from "./types";

export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async search(
    question: string,
    selectedText?: string,
    currentFile?: SearchRequest["currentFile"]
  ): Promise<SearchResponse> {
    // Mock 응답 데이터
    const mockResults = [
      {
        title: "검색 결과 1",
        content: "이것은 첫 번째 검색 결과입니다.",
        score: 0.95,
        context: selectedText
          ? "선택된 코드 기반 검색"
          : currentFile
          ? "전체 파일 기반 검색"
          : "일반 검색",
      },
      {
        title: "검색 결과 2",
        content: "이것은 두 번째 검색 결과입니다.",
        score: 0.85,
        context: selectedText
          ? "선택된 코드 기반 검색"
          : currentFile
          ? "전체 파일 기반 검색"
          : "일반 검색",
      },
      {
        title: "검색 결과 3",
        content: "이것은 세 번째 검색 결과입니다.",
        score: 0.75,
        context: selectedText
          ? "선택된 코드 기반 검색"
          : currentFile
          ? "전체 파일 기반 검색"
          : "일반 검색",
      },
    ];

    // 실제 API 호출 대신 mock 데이터 반환
    return {
      question,
      status: "ok",
      results: mockResults,
    };

    // 실제 API 호출 코드는 주석 처리
    /*
    try {
      const response = await fetch(`${this.baseUrl}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          selectedText,
          currentFile
        } as SearchRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data as SearchResponse;
    } catch (error) {
      console.error("API call failed:", error);
      return {
        question,
        status: "error",
        results: [],
      };
    }
    */
  }
}
