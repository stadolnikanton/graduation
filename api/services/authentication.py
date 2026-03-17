
    async def refresh(self, request, response):
        refresh_token = request.cookies.get("refresh_token")

        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=422, detail="Not a refresh token")

        user_id = int(payload.get("sub"))

        result = await self.session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return None

    async def get_current_user(self, current_user):
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": (
                current_user.created_at.isoformat() if current_user.created_at else None
            ),
        }
