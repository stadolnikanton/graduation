import pytest


@pytest.mark.anyio
async def test_share_limit_logic(db_connect):
    user = {
        "name": "sharer",
        "email": "s@m.com",
        "password": "Password123",
        "password_confirm": "Password123",
    }
    await db_connect.post("/auth/register", json=user)
    await db_connect.post(
        "/auth/login", json={"email": "s@m.com", "password": "Password123"}
    )

    await db_connect.post(
        "/files/upload", files={"file": ("shared.txt", b"data", "text/plain")}
    )

    res = await db_connect.get("/files/")
    owned_files = res.json().get("files", {}).get("owned", [])

    target_file = next(
        (f for f in owned_files if f["original_filename"] == "shared.txt"), None
    )
    assert target_file is not None, "Файл не найден"
    file_id = target_file["id"]

    share_res = await db_connect.post(
        f"/share/{file_id}", data={"expires_hours": 1, "max_downloads": 1}
    )
    assert share_res.status_code == 200
    token = share_res.json()["share_url"].split("/")[-1]

    await db_connect.get(f"/share/{token}")

    second_res = await db_connect.get(f"/share/{token}")
    assert second_res.status_code == 410
