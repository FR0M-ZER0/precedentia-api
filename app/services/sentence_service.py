import re
import io
from pypdf import PdfReader

START_MARKERS = [
    r"peti[çc][aã]o\s+inicial",
    r"excelent[íi]ssimo\s+senhor",
    r"exmo\.?\s*sr\.?\s*dr\.?",
    r"mm\.?\s*juiz",
    r"douto\s+juiz",
]

END_MARKERS = [
    r"termos\s+em\s+que\s+pede\s+deferimento",
    r"nestes\s+termos\s*,?\s*pede\s+deferimento",
    r"pede\s+e\s+espera\s+deferimento",
    r"requer\s+deferimento",
    r"data\s+e\s+assinatura",
]

NEXT_PIECE_MARKERS = [
    r"contest[aã][çc][aã]o",
    r"reconven[çc][aã]o",
    r"senten[çc]a",
    r"decis[aã]o\s+interlocut",
    r"audi[êe]ncia",
    r"certid[aã]o\s+de\s+cita[çc][aã]o",
]

BATCH_SIZE = 50
MAX_PAGES_TO_SCAN = 300


class SentenceService:
    @staticmethod
    def _matches_any(text: str, patterns: list[str]) -> bool:
        t = text.lower()
        return any(re.search(p, t) for p in patterns)

    @staticmethod
    def _clean_page_text(raw: str) -> str:
        return re.sub(r"\s+", " ", raw.replace("\n", " ").replace("\r", " ")).strip()

    @staticmethod
    def extract_initial_petition(file_bytes: bytes) -> dict:
        """
        Extrai somente a petição inicial de um processo judicial completo.
        Lê as páginas em lotes e interrompe assim que detectar o fim da
        petição, evitando carregar o processo inteiro em memória.

        Returns:
            {
                "text": str,
                "start_page": int,
                "end_page": int,
                "pages_read": int,
                "found": bool,
            }
        """
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        limit = min(total_pages, MAX_PAGES_TO_SCAN)

        petition_started = False
        petition_lines: list[str] = []
        start_page = -1
        end_page = -1

        for batch_start in range(0, limit, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, limit)

            for page_idx in range(batch_start, batch_end):
                raw = reader.pages[page_idx].extract_text() or ""
                clean = SentenceService._clean_page_text(raw)

                if not petition_started:
                    if SentenceService._matches_any(clean, START_MARKERS):
                        petition_started = True
                        start_page = page_idx + 1
                        petition_lines.append(clean)
                        print(
                            f"[SentenceService] Petição inicial encontrada na "
                            f"página {start_page}."
                        )
                else:
                    if SentenceService._matches_any(
                        clean, NEXT_PIECE_MARKERS
                    ) and not SentenceService._matches_any(clean, END_MARKERS):
                        end_page = page_idx
                        print(
                            f"[SentenceService] Interrompido por nova peça na "
                            f"página {page_idx + 1}. Petição extraída até a "
                            f"página {end_page}."
                        )
                        break

                    petition_lines.append(clean)

                    if SentenceService._matches_any(clean, END_MARKERS):
                        end_page = page_idx + 1
                        print(
                            f"[SentenceService] Fim da petição detectado na "
                            f"página {end_page}."
                        )
                        break

            if end_page != -1:
                break

        found = petition_started

        if petition_started and end_page == -1:
            end_page = min(start_page + len(petition_lines), limit)
            print(
                f"[SentenceService] Fim da petição não detectado por marcador."
                f" Usando página {end_page} como estimativa."
            )

        return {
            "text": " ".join(petition_lines).strip(),
            "start_page": start_page,
            "end_page": end_page,
            "pages_read": end_page if end_page != -1 else limit,
            "found": found,
        }

    @staticmethod
    async def extract_petition_text(file_bytes: bytes) -> dict:
        """
        Wrapper async para uso nos endpoints. Valida se a petição foi
        encontrada e retorna o texto junto com metadados de localização
        no processo.

        Returns:
            {
                "text": str,
                "count": int,
                "meta": {
                    "start_page": int,
                    "end_page": int,
                    "pages_read": int,
                }
            }
        """
        result = SentenceService.extract_initial_petition(file_bytes)

        print(f"[SentenceService] Texto extraído:\n{result['text']}\n")

        if not result["found"] or not result["text"]:
            raise ValueError(
                f"Petição inicial não encontrada nas primeiras "
                f"{MAX_PAGES_TO_SCAN} páginas do processo."
            )

        return {
            "text": result["text"],
            "count": result["end_page"] - result["start_page"] + 1,
            "meta": {
                "start_page": result["start_page"],
                "end_page": result["end_page"],
                "pages_read": result["pages_read"],
            },
        }
