from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.search_model import Search
from app.models.user_model import User


def seed():
    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            print("⚠️ Usuário ID 1 não encontrado. Criando usuário de teste...")
            user = User(
                id=1,
                email="desenvolvedor@fatec.sp.gov.br",
                password="hashed_password_aqui",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        user_id = user.id

        mock_data = [
            {
                "type": "Ação Cobrança - Lei 12855",
                "tribunal": "Justiça Federal",
                "facts": "Servidor público federal pleiteando indenização de fronteira nos termos da Lei nº 12.855/2013.",
                "requests": "Reconhecimento do direito à percepção de R$ 91,00 por jornada e condenação ao pagamento de retroativos.",
                "file_name": "Ação Cobrança Lei 12855 Tema Repetitivo 974 SIRDR 3 STJ.pdf",
                "precedents": "Tema Repetitivo 974 STJ - Fixa a legalidade da verba de fronteira e o direito à percepção de R$ 91,00 por jornada trabalhada para servidores federais civis.",
            },
            {
                "type": "Ação Popular",
                "tribunal": "TJES",
                "facts": "Defesa do patrimônio municipal contra ato estadual lesivo à autonomia e finanças do Município.",
                "requests": "Tutela provisória de urgência para suspender ato administrativo e declaração final de nulidade.",
                "file_name": "Ação Popular Competência Originária TJES IRDR 85.pdf",
                "precedents": "IRDR 85 TJES - Analisa a competência federativa originária das Cortes Estaduais em conflitos interinstitucionais que afetam finanças municipais.",
            },
            {
                "type": "Habeas Corpus",
                "tribunal": "Tribunal de Justiça",
                "facts": "Conflito entre foro privilegiado estabelecido em constituição estadual e a soberania do Tribunal do Júri.",
                "requests": "Liminar para suspensão da ação penal e reconhecimento da competência exclusiva do Júri.",
                "file_name": "Competência Júri Foro Privilegiado CE SV 45 STF.pdf",
                "precedents": "Súmula Vinculante 45 STF - A competência constitucional do Tribunal do Júri para crimes dolosos contra a vida prevalece sobre o foro por prerrogativa de função instituído exclusivamente por constituição estadual.",
            },
            {
                "type": "Alimentos Complementares",
                "tribunal": "Vara de Família",
                "facts": "Pedido de complementação de verba alimentar direcionada aos avós devido à insuficiência dos genitores.",
                "requests": "Fixação de alimentos subsidiários e citação do polo passivo para audiência de conciliação.",
                "file_name": "Inicial Alimentos Complementares Litisconsórcio Avós Tema 1310 com suspensão.pdf",
                "precedents": "Tema 1310 STJ - Define os parâmetros para fixação da responsabilidade alimentar subsidiária e complementar dos avós (litisconsórcio facultativo).",
            },
            {
                "type": "Repetição de Indébito",
                "tribunal": "Justiça Federal",
                "facts": "Questionamento sobre a legalidade de taxas de matrícula em instituições públicas de ensino superior.",
                "requests": "Declaração de nulidade da cobrança e repetição do indébito dos valores pagos indevidamente.",
                "file_name": "Inicial Cobrança Taxa Matrícula Universidade Pública Tema RG 40.pdf",
                "precedents": "Tema RG 40 STF - Consagra o princípio da gratuidade do ensino público em estabelecimentos oficiais, vedando a cobrança de taxas de matrícula em universidades públicas.",
            },
        ]

        print("🌱 Iniciando o seed da tabela 'search' (campo precedents como texto)...")

        for data in mock_data:
            petition_path = f"app/documents/petitions/{data['file_name']}"

            existing = (
                db.query(Search).filter(Search.petition_path == petition_path).first()
            )

            if not existing:
                new_search = Search(
                    type=data["type"],
                    tribunal=data["tribunal"],
                    facts=data["facts"],
                    requests=data["requests"],
                    precedents=data["precedents"],
                    petition_path=petition_path,
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(new_search)
                print(f"✅ Inserida busca para: {data['file_name']}")
            else:
                print(f"⏭️ Pulando (já existe): {data['file_name']}")

        db.commit()
        print("\n✨ Processo de seed finalizado com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao realizar o seed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
