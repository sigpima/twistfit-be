def _seed_ten_questions(client, db_session):
    from app.domains.auth.models import User

    client.post("/auth/register", json={"name": "Admin", "identifier": "quiz-attempt-admin@example.com", "password": "password123"})
    db_session.query(User).filter(User.email == "quiz-attempt-admin@example.com").update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"identifier": "quiz-attempt-admin@example.com", "password": "password123"})

    hue_options = [
        {"label": "Warm", "axisValue": "warm"},
        {"label": "Cool", "axisValue": "cool"},
        {"label": "Neutral", "axisValue": "neutral"},
    ]
    value_options = [
        {"label": "Dark", "axisValue": "dark"},
        {"label": "Light", "axisValue": "light"},
        {"label": "Medium", "axisValue": "medium"},
    ]
    chroma_options = [
        {"label": "Bright", "axisValue": "bright"},
        {"label": "Muted", "axisValue": "muted"},
        {"label": "Neutral", "axisValue": "neutral"},
    ]

    hue_questions = [
        client.post("/quiz-questions", json={"questionText": f"Hue {i}?", "axis": "hue", "options": hue_options}).json()
        for i in range(5)
    ]
    value_questions = [
        client.post("/quiz-questions", json={"questionText": f"Value {i}?", "axis": "value", "options": value_options}).json()
        for i in range(3)
    ]
    chroma_questions = [
        client.post("/quiz-questions", json={"questionText": f"Chroma {i}?", "axis": "chroma", "options": chroma_options}).json()
        for i in range(2)
    ]

    client.post("/auth/logout")
    return hue_questions, value_questions, chroma_questions


def _option_id_for(question, axis_value):
    return next(option["id"] for option in question["options"] if option["axisValue"] == axis_value)


def _light_spring_answers(hue_questions, value_questions, chroma_questions):
    # Mirrors Task 1's test_value_dominant_sub_season vote pattern exactly:
    # hue unanimous warm, value unanimous light, chroma split bright/neutral
    # (a tie -> "neutral" axis result, share 0) -> parentSeason=spring, subSeason=light-spring.
    answers = [{"questionId": q["id"], "optionId": _option_id_for(q, "warm")} for q in hue_questions]
    answers += [{"questionId": q["id"], "optionId": _option_id_for(q, "light")} for q in value_questions]
    answers += [
        {"questionId": chroma_questions[0]["id"], "optionId": _option_id_for(chroma_questions[0], "bright")},
        {"questionId": chroma_questions[1]["id"], "optionId": _option_id_for(chroma_questions[1], "neutral")},
    ]
    return answers


def test_create_attempt_allows_anonymous_submission(client, db_session):
    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    response = client.post("/quiz-attempts", json={"answers": answers})
    assert response.status_code == 201
    body = response.json()
    assert body["parentSeason"] == "spring"
    assert body["subSeason"] == "light-spring"
    assert body["userId"] is None


def test_create_attempt_attributes_to_the_logged_in_user(client, db_session):
    from app.domains.auth.models import User

    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    client.post("/auth/register", json={"name": "Test", "identifier": "quiz-attempt-router@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-attempt-router@example.com", "password": "password123"})
    user = db_session.query(User).filter(User.email == "quiz-attempt-router@example.com").one()

    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    response = client.post("/quiz-attempts", json={"answers": answers})
    assert response.status_code == 201
    assert response.json()["userId"] == user.id


def test_create_attempt_treats_an_invalid_access_token_as_anonymous(client, db_session):
    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    client.cookies.set("access_token", "not-a-valid-jwt")
    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    response = client.post("/quiz-attempts", json={"answers": answers})
    assert response.status_code == 201
    assert response.json()["userId"] is None


def test_create_attempt_rejects_fewer_than_ten_answers(client, db_session):
    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    response = client.post("/quiz-attempts", json={"answers": answers[:2]})
    assert response.status_code == 422


def test_create_attempt_rejects_an_option_id_that_does_not_match_its_question(client, db_session):
    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    answers[0]["optionId"] = _option_id_for(value_questions[0], "light")  # belongs to a value question, not this hue one
    response = client.post("/quiz-attempts", json={"answers": answers})
    assert response.status_code == 422


def test_get_me_requires_authentication(client):
    response = client.get("/quiz-attempts/me")
    assert response.status_code == 401


def test_get_me_returns_null_when_no_attempt_exists(client):
    client.post("/auth/register", json={"name": "Test", "identifier": "quiz-me-1@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-me-1@example.com", "password": "password123"})

    response = client.get("/quiz-attempts/me")

    assert response.status_code == 200
    assert response.json() is None


def test_get_me_returns_the_latest_attempt(client, db_session):
    hue_questions, value_questions, chroma_questions = _seed_ten_questions(client, db_session)
    client.post("/auth/register", json={"name": "Test", "identifier": "quiz-me-2@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-me-2@example.com", "password": "password123"})

    answers = _light_spring_answers(hue_questions, value_questions, chroma_questions)
    client.post("/quiz-attempts", json={"answers": answers})

    response = client.get("/quiz-attempts/me")

    assert response.status_code == 200
    assert response.json()["subSeason"] == "light-spring"
