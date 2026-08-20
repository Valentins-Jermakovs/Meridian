# ==============================
# Datu normalizācijas klase
# ==============================

class DataNormalizer:

    # Teksta normalizācija
    def normalize_text(
        self,
        value: str,
    ) -> str:
        return " ".join(
            value.strip().split()
        )

    # E-pasta normalizācija
    def normalize_email(
        self,
        email: str,
    ) -> str:
        return email.strip().lower()

    # Lietotājvārda normalizācija
    def normalize_username(
        self,
        username: str,
    ) -> str:
        return username.strip().lower()