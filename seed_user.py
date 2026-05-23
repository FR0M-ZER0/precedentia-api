from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user_model import User
from app.models.search_model import Search  # noqa: F401
from app.models.petition_model import Petition  # noqa: F401


def seed():
    db: Session = SessionLocal()

    try:
        mock_users = [
            {
                "email": "desenvolvedor@fatec.sp.gov.br",
                "password": "hashed_password_1",
            },
            {
                "email": "admin@juriscan.com",
                "password": "hashed_password_2",
            },
            {
                "email": "usuario.teste@email.com",
                "password": "hashed_password_3",
            },
        ]

        print("🌱 Iniciando o seed da tabela 'users'...")

        for data in mock_users:
            existing_user = db.query(User).filter(User.email == data["email"]).first()

            if not existing_user:
                new_user = User(
                    email=data["email"],
                    password=data["password"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(new_user)
                print(f"✅ Usuário inserido: {data['email']}")
            else:
                print(f"⏭️ Pulando (já existe): {data['email']}")

        db.commit()
        print("\n✨ Processo de seed finalizado com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao realizar o seed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
