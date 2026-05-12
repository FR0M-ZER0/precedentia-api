import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.petition_model import Petition
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
                password="hashed_password_aqui"
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
                "file_name": "Ação Cobrança Lei 12855 Tema Repetitivo 974 SIRDR 3 STJ.pdf"
            },
            {
                "type": "Ação Popular",
                "tribunal": "TJES",
                "facts": "Defesa do patrimônio municipal contra ato estadual lesivo à autonomia e finanças do Município.",
                "requests": "Tutela provisória de urgência para suspender ato administrativo e declaração final de nulidade.",
                "file_name": "Ação Popular Competência Originária TJES IRDR 85.pdf"
            },
            {
                "type": "Habeas Corpus",
                "tribunal": "Tribunal de Justiça",
                "facts": "Conflito entre foro privilegiado estabelecido em constituição estadual e a soberania do Tribunal do Júri.",
                "requests": "Liminar para suspensão da ação penal e reconhecimento da competência exclusiva do Júri.",
                "file_name": "Competência Júri Foro Privilegiado CE SV 45 STF.pdf"
            },
            {
                "type": "Alimentos Complementares",
                "tribunal": "Vara de Família",
                "facts": "Pedido de complementação de verba alimentar direcionada aos avós devido à insuficiência dos genitores.",
                "requests": "Fixação de alimentos subsidiários e citação do polo passivo para audiência de conciliação.",
                "file_name": "Inicial Alimentos Complementares Litisconsórcio Avós Tema 1310 com suspensão.pdf"
            },
            {
                "type": "Repetição de Indébito",
                "tribunal": "Justiça Federal",
                "facts": "Questionamento sobre a legalidade de taxas de matrícula em instituições públicas de ensino superior.",
                "requests": "Declaração de nulidade da cobrança e repetição do indébito dos valores pagos indevidamente.",
                "file_name": "Inicial Cobrança Taxa Matrícula Universidade Pública Tema RG 40.pdf"
            }
        ]

        print("🌱 Iniciando o seed de petições...")

        for data in mock_data:

            file_path = f"app/documents/petitions/{data['file_name']}"
            existing = db.query(Petition).filter(Petition.file_path == file_path).first()
            
            if not existing:
                new_petition = Petition(
                    type=data["type"],
                    tribunal=data["tribunal"],
                    facts=data["facts"],
                    requests=data["requests"],
                    file_path=file_path,
                    user_id=user_id,
                    created_at=datetime.utcnow()
                )
                db.add(new_petition)
                print(f"✅ Inserida: {data['file_name']}")
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