from typing import List, Tuple, Optional
from database.database_manager import DatabaseManager
from database.models import Token, TrackedToken


class TokenManager:
    """Manages token tracking and threshold operations"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize token manager

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def get_all_tokens(self) -> List[Token]:
        """Get all available tokens"""
        return self.db_manager.get_all_tokens()

    def get_available_tokens(self) -> List[Token]:
        """Get tokens that are not currently tracked"""
        return self.db_manager.get_available_tokens()

    def get_tracked_tokens(self) -> List[Tuple[Token, TrackedToken]]:
        """Get all tracked tokens with their thresholds"""
        return self.db_manager.get_tracked_tokens()

    def add_token_to_tracked(self, token_id: int, threshold_value: float,
                            threshold_mode: str = 'percentage') -> bool:
        """
        Add token to tracked list

        Args:
            token_id: Token ID
            threshold_value: Threshold value
            threshold_mode: 'percentage' or 'dollar'

        Returns:
            True if successful
        """
        try:
            # Validate threshold
            if threshold_value < 0:
                print("Threshold must be positive")
                return False

            # Validate mode
            if threshold_mode not in ['percentage', 'dollar']:
                print("Invalid threshold mode")
                return False

            # Add to tracked
            self.db_manager.add_tracked_token(token_id, threshold_value, threshold_mode)
            return True

        except Exception as e:
            print(f"Error adding token to tracked: {str(e)}")
            return False

    def remove_token_from_tracked(self, token_id: int) -> bool:
        """
        Remove token from tracked list

        Args:
            token_id: Token ID

        Returns:
            True if successful
        """
        try:
            self.db_manager.remove_tracked_token(token_id)
            return True
        except Exception as e:
            print(f"Error removing token from tracked: {str(e)}")
            return False

    def update_token_threshold(self, token_id: int, threshold_value: float,
                               threshold_mode: str) -> bool:
        """
        Update threshold for tracked token

        Args:
            token_id: Token ID
            threshold_value: New threshold value
            threshold_mode: 'percentage' or 'dollar'

        Returns:
            True if successful
        """
        try:
            # Validate
            if threshold_value < 0:
                print("Threshold must be positive")
                return False

            if threshold_mode not in ['percentage', 'dollar']:
                print("Invalid threshold mode")
                return False

            # Update
            self.db_manager.update_token_threshold(token_id, threshold_value, threshold_mode)
            return True

        except Exception as e:
            print(f"Error updating threshold: {str(e)}")
            return False

    def get_token_by_symbol(self, symbol: str) -> Optional[Token]:
        """Get token by symbol"""
        return self.db_manager.get_token_by_symbol(symbol)

    def get_token_by_id(self, token_id: int) -> Optional[Token]:
        """Get token by ID"""
        return self.db_manager.get_token_by_id(token_id)

    def is_token_tracked(self, token_id: int) -> bool:
        """Check if token is tracked"""
        tracked = self.get_tracked_tokens()
        return any(token.id == token_id for token, _ in tracked)
