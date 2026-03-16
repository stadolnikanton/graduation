import pytest


@pytest.mark.anyio
async def test_upload_and_list_files(auth_client):
    file_content = b"Hello, MinIO!"
    upload_res = await auth_client.post(
        "/files/upload", files={"file": ("test_file.txt", file_content, "text/plain")}
    )
    assert upload_res.status_code == 200

    list_res = await auth_client.get("/files/")
    assert list_res.status_code == 200

    data = list_res.json()

    owned_files = data.get("files", {}).get("owned", [])

    my_file = next(
        (f for f in owned_files if f["original_filename"] == "test_file.txt"), None
    )
    assert my_file is not None, f"Файл не найден в {owned_files}"
    assert my_file["original_filename"] == "test_file.txt"


@pytest.mark.anyio
async def test_delete_file_logic(auth_client):
    await auth_client.post(
        "/files/upload", files={"file": ("to_delete.txt", b"bye", "text/plain")}
    )

    res = await auth_client.get("/files/")
    owned_files = res.json().get("files", {}).get("owned", [])

    target = next(
        (f for f in owned_files if f["original_filename"] == "to_delete.txt"), None
    )
    assert target is not None, "Файл не найден"
    file_id = target["id"]

    del_res = await auth_client.delete(f"/files/{file_id}")
    assert del_res.status_code == 200

    final_res = await auth_client.get("/files/")
    final_owned = final_res.json().get("files", {}).get("owned", [])
    assert all(f["id"] != file_id for f in final_owned)
