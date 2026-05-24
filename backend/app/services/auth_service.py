"""Authentication service handling user registration, login, and profile management."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password, create_access_token

logger = logging.getLogger("fraudshield.services.auth")


class AuthService:
    """Service layer for authentication and user management operations."""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user account.

        Args:
            db: Database session
            user_data: Validated user registration data

        Returns:
            Created User object

        Raises:
            ValueError: If email or username already exists
        """
        # Check for existing email
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise ValueError("An account with this email already exists")

        # Check for existing username
        existing_username = db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_username:
            raise ValueError("This username is already taken")

        # Create user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            phone=user_data.phone,
            role="user",
            is_active=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password.

        Args:
            db: Database session
            email: User's email address
            password: User's plain text password

        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return None

        if not user.is_active:
            logger.warning(f"Login attempt for deactivated account: {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {email}")
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        logger.info(f"Successful login: {email}")
        return user

    @staticmethod
    def generate_token(user: User) -> dict:
        """Generate a JWT token for an authenticated user.

        Args:
            user: Authenticated User object

        Returns:
            Dictionary with access_token, token_type, and user data
        """
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def update_profile(db: Session, user: User, update_data: UserUpdate) -> User:
        """Update a user's profile information.

        Args:
            db: Database session
            user: Current user object
            update_data: Fields to update

        Returns:
            Updated User object
        """
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if value is not None:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        logger.info(f"Profile updated for user: {user.email}")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users(
        db: Session, skip: int = 0, limit: int = 50
    ) -> tuple:
        """Get all users with pagination (admin only).

        Returns:
            Tuple of (users list, total count)
        """
        total = db.query(User).count()
        users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return users, total

    @staticmethod
    def toggle_user_status(db: Session, user_id: str, is_active: bool) -> Optional[User]:
        """Activate or deactivate a user account (admin only)."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.is_active = is_active
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        status = "activated" if is_active else "deactivated"
        logger.info(f"User {user.email} {status}")
        return user

    @staticmethod
    def create_admin_user(db: Session) -> Optional[User]:
        """Create the default admin user if it doesn't exist.

        Returns:
            The admin User object, or None if already exists
        """
        existing = db.query(User).filter(User.email == "admin@veridian.io").first()
        if existing:
            return existing

        admin = User(
            email="admin@veridian.io",
            username="admin",
            full_name="System Administrator",
            hashed_password=hash_password("Admin@123456"),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        logger.info("Default admin user created: admin@veridian.io / Admin@123456")
        return admin
