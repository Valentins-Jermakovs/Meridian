# ==============================
# Data Normalization
# ==============================

class DataNormalizer:
    """
    Provides utilities for normalizing user-provided text data.

    The normalizer removes unnecessary whitespace and applies
    consistent formatting to email addresses and usernames.
    """

    # ==============================
    # Normalize Text
    # ==============================

    def normalize_text(
        self,
        value: str,
    ) -> str:
        """
        Normalizes general text by removing leading and trailing
        whitespace and replacing consecutive whitespace characters
        with a single space.

        Args:
            value (str): Text value to normalize.

        Returns:
            str: Normalized text.
        """

        return " ".join(
            value.strip().split()
        )

    # ==============================
    # Normalize Email
    # ==============================

    def normalize_email(
        self,
        email: str,
    ) -> str:
        """
        Normalizes an email address by removing surrounding
        whitespace and converting it to lowercase.

        Args:
            email (str): Email address to normalize.

        Returns:
            str: Normalized email address.
        """

        return email.strip().lower()

    # ==============================
    # Normalize Username
    # ==============================

    def normalize_username(
        self,
        username: str,
    ) -> str:
        """
        Normalizes a username by removing surrounding whitespace
        and converting it to lowercase.

        Args:
            username (str): Username to normalize.

        Returns:
            str: Normalized username.
        """

        return username.strip().lower()