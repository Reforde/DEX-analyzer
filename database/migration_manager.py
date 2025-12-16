from typing import Optional
from config import Config
from database.database_manager import DatabaseManager


class MigrationManager:
    """Handles database migrations and initial data seeding"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize migration manager

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def run_migrations(self) -> None:
        """Run all necessary migrations"""
        print("Running database migrations...")

        # Check if tokens table is empty
        tokens = self.db_manager.get_all_tokens()
        if len(tokens) == 0:
            print("Seeding initial token data...")
            self.seed_tokens()
            print(f"Successfully seeded {len(Config.TOKENS_CONFIG)} tokens")
        else:
            print(f"Database already contains {len(tokens)} tokens, skipping seed")

        # Set default preferences if not exist
        self._set_default_preferences()

        print("Migrations completed successfully!")

    def seed_tokens(self) -> None:
        """Seed database with 40 most popular tokens"""
        for token_config in Config.TOKENS_CONFIG:
            symbol = token_config["symbol"]
            name = token_config["name"]
            decimals = token_config["decimals"]

            # Insert token (addresses not needed for CoinGecko API)
            self.db_manager.insert_token(
                symbol=symbol,
                name=name,
                decimals=decimals,
                eth_address=None,
                bsc_address=None,
                polygon_address=None
            )

            print(f"  Added token: {symbol} ({name})")

    def _set_default_preferences(self) -> None:
        """Set default user preferences if they don't exist"""
        # Theme preference
        if self.db_manager.get_preference("theme") is None:
            self.db_manager.set_preference("theme", Config.DEFAULT_THEME)
            print(f"  Set default theme: {Config.DEFAULT_THEME}")

        # Auto-refresh preference
        if self.db_manager.get_preference("auto_refresh") is None:
            self.db_manager.set_preference("auto_refresh", "false")
            print("  Set default auto_refresh: false")

    def reset_database(self, confirm: bool = False) -> None:
        """
        Reset database to initial state (WARNING: deletes all data)

        Args:
            confirm: Must be True to actually reset
        """
        if not confirm:
            print("Reset cancelled: confirm parameter must be True")
            return

        print("Resetting database...")
        self.db_manager.clear_all_data()
        print("Database reset complete!")


def initialize_database(db_name: Optional[str] = None) -> DatabaseManager:
    """
    Initialize database with migrations

    Args:
        db_name: Optional database name (defaults to Config.DATABASE_NAME)

    Returns:
        DatabaseManager instance
    """
    if db_name is None:
        db_name = Config.DATABASE_NAME

    # Create database manager
    db_manager = DatabaseManager(db_name)

    # Run migrations
    migration_manager = MigrationManager(db_manager)
    migration_manager.run_migrations()

    return db_manager
