def _register_and_login(client, email: str) -> None:
    client.post("/auth/register", json={"name": "User", "identifier": email, "password": "password123"})
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def _promote_to_admin_and_relogin(client, db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


VALID_BODY = {"title": "Bài test", "body": "Nội dung", "category": "general"}


def _publish(db_session, post_id: int) -> None:
    from app.domains.forum.models import ForumPost

    db_session.query(ForumPost).filter(ForumPost.id == post_id).update({"status": "published"})
    db_session.commit()


def test_list_posts_is_public_and_only_returns_published(client, db_session):
    _register_and_login(client, "forum-author@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    assert client.get("/forum/posts").json() == []

    _publish(db_session, post["id"])

    published = client.get("/forum/posts").json()
    assert [p["id"] for p in published] == [post["id"]]


def test_list_posts_filters_by_category(client, db_session):
    _register_and_login(client, "forum-cat@example.com")
    general = client.post("/forum/posts", json=VALID_BODY).json()
    styling = client.post("/forum/posts", json={**VALID_BODY, "category": "styling-help"}).json()
    _publish(db_session, general["id"])
    _publish(db_session, styling["id"])

    response = client.get("/forum/posts?category=styling-help")
    assert [p["id"] for p in response.json()] == [styling["id"]]


def test_list_posts_ignores_an_invalid_category_filter(client, db_session):
    _register_and_login(client, "forum-cat2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    response = client.get("/forum/posts?category=not-a-real-category")
    assert [p["id"] for p in response.json()] == [post["id"]]


def test_create_post_requires_authentication(client):
    response = client.post("/forum/posts", json=VALID_BODY)
    assert response.status_code == 401


def test_create_post_rejects_invalid_body(client):
    _register_and_login(client, "forum-invalid@example.com")
    response = client.post("/forum/posts", json={**VALID_BODY, "category": "not-a-category"})
    assert response.status_code == 422


def test_get_post_returns_404_for_a_pending_post_to_a_stranger(client):
    _register_and_login(client, "forum-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-stranger@example.com")
    assert client.get(f"/forum/posts/{post['id']}").status_code == 404


def test_get_post_is_visible_to_its_owner_while_pending(client):
    _register_and_login(client, "forum-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    assert client.get(f"/forum/posts/{post['id']}").status_code == 200


def test_get_post_is_visible_to_an_admin_while_pending(client, db_session):
    _register_and_login(client, "forum-owner3@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-admin-viewer@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-admin-viewer@example.com")
    assert client.get(f"/forum/posts/{post['id']}").status_code == 200


def test_get_post_returns_404_for_a_nonexistent_id(client):
    assert client.get("/forum/posts/999999").status_code == 404


def test_list_my_posts_requires_authentication(client):
    assert client.get("/forum/posts/mine").status_code == 401


def test_list_my_posts_returns_only_the_caller_own_posts_any_status(client):
    _register_and_login(client, "forum-mine@example.com")
    mine = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-other@example.com")
    client.post("/forum/posts", json=VALID_BODY)

    _register_and_login(client, "forum-mine@example.com")
    response = client.get("/forum/posts/mine")
    assert [p["id"] for p in response.json()] == [mine["id"]]


def test_update_post_requires_authentication(client):
    assert client.put("/forum/posts/1", json=VALID_BODY).status_code == 401


def test_update_post_requires_ownership(client):
    _register_and_login(client, "forum-owner4@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-not-owner@example.com")
    response = client.put(f"/forum/posts/{post['id']}", json=VALID_BODY)
    assert response.status_code == 403


def test_update_post_resets_status_to_pending_even_from_published(client, db_session):
    _register_and_login(client, "forum-owner5@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    updated = client.put(f"/forum/posts/{post['id']}", json={**VALID_BODY, "title": "Đã sửa"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "pending"
    assert updated.json()["title"] == "Đã sửa"


def test_update_post_returns_404_when_missing(client):
    _register_and_login(client, "forum-owner6@example.com")
    assert client.put("/forum/posts/999999", json=VALID_BODY).status_code == 404


def test_delete_post_requires_authentication(client):
    assert client.delete("/forum/posts/1").status_code == 401


def test_delete_post_allowed_for_owner(client):
    _register_and_login(client, "forum-owner7@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 204


def test_delete_post_allowed_for_admin(client, db_session):
    _register_and_login(client, "forum-owner8@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-admin-deleter@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-admin-deleter@example.com")
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 204


def test_delete_post_forbidden_for_non_owner_non_admin(client):
    _register_and_login(client, "forum-owner9@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-stranger2@example.com")
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 403


def test_delete_post_returns_404_when_missing(client):
    _register_and_login(client, "forum-owner10@example.com")
    assert client.delete("/forum/posts/999999").status_code == 404


def test_delete_post_returns_404_when_already_deleted(client):
    _register_and_login(client, "forum-owner11@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    client.delete(f"/forum/posts/{post['id']}")
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 404


def test_get_post_still_visible_after_the_owner_deletes_it_with_deletion_info(client):
    _register_and_login(client, "forum-owner12@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    client.delete(f"/forum/posts/{post['id']}")

    response = client.get(f"/forum/posts/{post['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["deletedAt"] is not None
    assert body["deletedByAdmin"] is False


def test_get_post_reports_deleted_by_admin_when_an_admin_deletes_it(client, db_session):
    _register_and_login(client, "forum-owner13@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    _register_and_login(client, "forum-admin-deleter2@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-admin-deleter2@example.com")
    client.delete(f"/forum/posts/{post['id']}")

    response = client.get(f"/forum/posts/{post['id']}")
    assert response.json()["deletedByAdmin"] is True


def test_list_posts_excludes_a_deleted_post(client, db_session):
    _register_and_login(client, "forum-owner14@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    client.delete(f"/forum/posts/{post['id']}")

    assert client.get("/forum/posts").json() == []


def test_post_response_includes_can_delete_for_the_owner(client):
    _register_and_login(client, "forum-owner15@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    assert post["canDelete"] is True


def test_update_post_status_requires_authentication(client):
    assert client.patch("/forum/posts/1", json={"status": "published"}).status_code == 401


def test_update_post_status_requires_admin(client):
    _register_and_login(client, "forum-status-user@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "published"})
    assert response.status_code == 403


def test_update_post_status_allows_pending_to_published(client, db_session):
    _register_and_login(client, "forum-status1@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status1@example.com")

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "published"})
    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_update_post_status_allows_pending_to_rejected(client, db_session):
    _register_and_login(client, "forum-status2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status2@example.com")

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "rejected"})
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_update_post_status_allows_published_to_hidden(client, db_session):
    _register_and_login(client, "forum-status3@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status3@example.com")
    client.patch(f"/forum/posts/{post['id']}", json={"status": "published"})

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "hidden"})
    assert response.status_code == 200
    assert response.json()["status"] == "hidden"


def test_update_post_status_rejects_an_invalid_transition(client, db_session):
    _register_and_login(client, "forum-status4@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status4@example.com")

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "hidden"})
    assert response.status_code == 409
    assert response.json()["detail"] == "INVALID_STATUS_TRANSITION"


def test_update_post_status_rejects_transition_from_a_terminal_status(client, db_session):
    _register_and_login(client, "forum-status5@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status5@example.com")
    client.patch(f"/forum/posts/{post['id']}", json={"status": "rejected"})

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "published"})
    assert response.status_code == 409


def test_update_post_status_rejects_an_invalid_status_value(client, db_session):
    _register_and_login(client, "forum-status6@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-status6@example.com")

    response = client.patch(f"/forum/posts/{post['id']}", json={"status": "not-a-status"})
    assert response.status_code == 422


def test_update_post_status_returns_404_when_missing(client, db_session):
    _register_and_login(client, "forum-status7@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-status7@example.com")
    assert client.patch("/forum/posts/999999", json={"status": "published"}).status_code == 404


def test_create_report_requires_authentication(client):
    assert client.post("/forum/posts/1/report", json={"reason": "Spam"}).status_code == 401


def test_create_report_succeeds_for_a_visible_post(client, db_session):
    _register_and_login(client, "forum-report-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-report-owner@example.com")
    client.patch(f"/forum/posts/{post['id']}", json={"status": "published"})

    _register_and_login(client, "forum-reporter@example.com")
    response = client.post(f"/forum/posts/{post['id']}/report", json={"reason": "Spam"})
    assert response.status_code == 201
    assert response.json()["postId"] == post["id"]
    assert response.json()["status"] == "open"


def test_create_report_returns_404_for_a_non_visible_post(client):
    _register_and_login(client, "forum-report-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-reporter2@example.com")
    response = client.post(f"/forum/posts/{post['id']}/report", json={"reason": "Spam"})
    assert response.status_code == 404


def test_create_report_rejects_a_blank_reason(client):
    _register_and_login(client, "forum-report-owner3@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    response = client.post(f"/forum/posts/{post['id']}/report", json={"reason": "   "})
    assert response.status_code == 422


def test_moderation_pending_requires_admin(client):
    assert client.get("/forum/moderation/pending").status_code == 401


def test_moderation_pending_lists_pending_posts(client, db_session):
    _register_and_login(client, "forum-mod-pending@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-mod-pending@example.com")

    response = client.get("/forum/moderation/pending")
    assert response.status_code == 200
    assert any(p["id"] == post["id"] for p in response.json())


def test_moderation_reports_requires_admin(client):
    assert client.get("/forum/moderation/reports").status_code == 401


def test_moderation_reports_lists_open_reports_with_post_info(client, db_session):
    _register_and_login(client, "forum-mod-reports@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    client.post(f"/forum/posts/{post['id']}/report", json={"reason": "Spam"})
    _promote_to_admin_and_relogin(client, db_session, "forum-mod-reports@example.com")

    response = client.get("/forum/moderation/reports")
    assert response.status_code == 200
    report = next(r for r in response.json() if r["postId"] == post["id"])
    assert report["postTitle"] == VALID_BODY["title"]
    assert report["postStatus"] == "pending"


def test_resolve_report_requires_admin(client):
    assert client.patch("/forum/reports/1").status_code == 401


def test_resolve_report_marks_it_resolved(client, db_session):
    _register_and_login(client, "forum-resolve@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    report = client.post(f"/forum/posts/{post['id']}/report", json={"reason": "Spam"}).json()
    _promote_to_admin_and_relogin(client, db_session, "forum-resolve@example.com")

    response = client.patch(f"/forum/reports/{report['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_resolve_report_returns_404_when_missing(client, db_session):
    _register_and_login(client, "forum-resolve2@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-resolve2@example.com")
    assert client.patch("/forum/reports/999999").status_code == 404


def test_upload_url_requires_authentication(client):
    assert client.post("/forum/upload-url").status_code == 401


def test_upload_url_returns_a_writable_sas_url_and_final_image_url(client):
    _register_and_login(client, "forum-upload@example.com")
    response = client.post("/forum/upload-url")
    assert response.status_code == 200
    body = response.json()
    assert "X-Amz-Signature=" in body["uploadUrl"]
    assert body["blobPath"] in body["imageUrl"]


def test_upload_url_accepts_webp_and_uses_a_webp_blob_extension(client):
    _register_and_login(client, "forum-upload-webp@example.com")
    response = client.post("/forum/upload-url", params={"content_type": "image/webp"})
    assert response.status_code == 200
    assert response.json()["blobPath"].endswith(".webp")


def test_upload_url_accepts_avif_and_uses_an_avif_blob_extension(client):
    _register_and_login(client, "forum-upload-avif@example.com")
    response = client.post("/forum/upload-url", params={"content_type": "image/avif"})
    assert response.status_code == 200
    assert response.json()["blobPath"].endswith(".avif")


def test_upload_url_rejects_unsupported_content_type(client):
    _register_and_login(client, "forum-upload-bad-type@example.com")
    response = client.post("/forum/upload-url", params={"content_type": "application/pdf"})
    assert response.status_code == 400


def test_create_post_accepts_an_optional_image_url(client):
    _register_and_login(client, "forum-image@example.com")
    response = client.post("/forum/posts", json={**VALID_BODY, "imageUrl": "https://example.com/a.jpg"})
    assert response.status_code == 201
    assert response.json()["imageUrl"] == "https://example.com/a.jpg"


def test_post_response_includes_author_name_and_zeroed_counts(client):
    _register_and_login(client, "forum-shape@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    assert post["authorName"] == "User"
    assert post["imageUrl"] is None
    assert post["likeCount"] == 0
    assert post["likedByMe"] is False
    assert post["commentCount"] == 0


def test_like_post_requires_authentication(client):
    assert client.post("/forum/posts/1/like").status_code == 401


def test_like_post_toggles_and_reflects_in_the_post_response(client, db_session):
    _register_and_login(client, "forum-like-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    response = client.post(f"/forum/posts/{post['id']}/like")
    assert response.status_code == 200
    assert response.json() == {"liked": True, "likeCount": 1}

    fetched = client.get(f"/forum/posts/{post['id']}").json()
    assert fetched["likeCount"] == 1
    assert fetched["likedByMe"] is True

    response2 = client.post(f"/forum/posts/{post['id']}/like")
    assert response2.json() == {"liked": False, "likeCount": 0}


def test_like_post_returns_404_for_a_non_visible_post(client):
    _register_and_login(client, "forum-like-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-like-stranger@example.com")
    assert client.post(f"/forum/posts/{post['id']}/like").status_code == 404


def test_like_post_returns_404_for_a_nonexistent_post(client):
    _register_and_login(client, "forum-like-owner3@example.com")
    assert client.post("/forum/posts/999999/like").status_code == 404


def test_create_comment_requires_authentication(client):
    assert client.post("/forum/posts/1/comments", json={"body": "Hay quá"}).status_code == 401


def test_create_comment_rejects_a_blank_body(client, db_session):
    _register_and_login(client, "forum-comment-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    response = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "   "})
    assert response.status_code == 422


def test_create_comment_succeeds_for_a_visible_post(client, db_session):
    _register_and_login(client, "forum-comment-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    _register_and_login(client, "forum-commenter@example.com")
    response = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Đẹp quá!"})
    assert response.status_code == 201
    body = response.json()
    assert body["body"] == "Đẹp quá!"
    assert body["authorName"] == "User"
    assert body["canDelete"] is True


def test_create_comment_returns_404_for_a_non_visible_post(client):
    _register_and_login(client, "forum-comment-owner3@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-commenter2@example.com")
    response = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Đẹp quá!"})
    assert response.status_code == 404


def test_list_comments_is_public_for_a_published_post(client, db_session):
    _register_and_login(client, "forum-comment-owner4@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Bình luận công khai"})

    _register_and_login(client, "forum-comment-viewer@example.com")
    response = client.get(f"/forum/posts/{post['id']}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["canDelete"] is False


def test_list_comments_returns_404_for_a_non_visible_post(client):
    _register_and_login(client, "forum-comment-owner5@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-commenter3@example.com")
    assert client.get(f"/forum/posts/{post['id']}/comments").status_code == 404


def test_post_response_comment_count_reflects_comments(client, db_session):
    _register_and_login(client, "forum-comment-owner6@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Một"})
    client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Hai"})

    fetched = client.get(f"/forum/posts/{post['id']}").json()
    assert fetched["commentCount"] == 2


def test_delete_comment_requires_authentication(client):
    assert client.delete("/forum/comments/1").status_code == 401


def test_delete_comment_allowed_for_the_author(client, db_session):
    _register_and_login(client, "forum-comment-owner7@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    comment = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Xoá tôi"}).json()

    assert client.delete(f"/forum/comments/{comment['id']}").status_code == 204


def test_delete_comment_allowed_for_an_admin(client, db_session):
    _register_and_login(client, "forum-comment-owner8@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    _register_and_login(client, "forum-commenter4@example.com")
    comment = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Của người khác"}).json()

    _register_and_login(client, "forum-comment-admin@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-comment-admin@example.com")
    assert client.delete(f"/forum/comments/{comment['id']}").status_code == 204


def test_delete_comment_forbidden_for_a_stranger(client, db_session):
    _register_and_login(client, "forum-comment-owner9@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])
    comment = client.post(f"/forum/posts/{post['id']}/comments", json={"body": "Của tôi"}).json()

    _register_and_login(client, "forum-comment-stranger@example.com")
    assert client.delete(f"/forum/comments/{comment['id']}").status_code == 403


def test_delete_comment_returns_404_when_missing(client):
    _register_and_login(client, "forum-comment-owner10@example.com")
    assert client.delete("/forum/comments/999999").status_code == 404


def test_bookmark_post_requires_authentication(client):
    assert client.post("/forum/posts/1/bookmark").status_code == 401


def test_bookmark_post_toggles_and_reflects_in_the_post_response(client, db_session):
    _register_and_login(client, "forum-bookmark-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    response = client.post(f"/forum/posts/{post['id']}/bookmark")
    assert response.status_code == 200
    assert response.json() == {"bookmarked": True}

    fetched = client.get(f"/forum/posts/{post['id']}").json()
    assert fetched["bookmarkedByMe"] is True

    response2 = client.post(f"/forum/posts/{post['id']}/bookmark")
    assert response2.json() == {"bookmarked": False}


def test_bookmark_post_returns_404_for_a_non_visible_post(client):
    _register_and_login(client, "forum-bookmark-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-bookmark-stranger@example.com")
    assert client.post(f"/forum/posts/{post['id']}/bookmark").status_code == 404


def test_bookmark_post_returns_404_for_a_nonexistent_post(client):
    _register_and_login(client, "forum-bookmark-owner3@example.com")
    assert client.post("/forum/posts/999999/bookmark").status_code == 404


def test_list_saved_posts_requires_authentication(client):
    assert client.get("/forum/posts/saved").status_code == 401


def test_list_saved_posts_returns_the_caller_bookmarked_posts(client, db_session):
    _register_and_login(client, "forum-saved-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    _register_and_login(client, "forum-saved-other@example.com")
    other_post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, other_post["id"])
    client.post(f"/forum/posts/{other_post['id']}/bookmark")

    response = client.get("/forum/posts/saved")
    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == [other_post["id"]]
    assert response.json()[0]["bookmarkedByMe"] is True
