from app.data_models.models import Job, JobMin


def test_get_jobs(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)
    response = testclient_with_session.get("/api/jobs")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    first = payload[0]
    assert Job(**first) == Job.from_orm(fake_data.FAKE_JOB)


def test_check_jobs_no_query(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    def mock_get_items_order_by(self, *args, **kwargs):
        assert "skip" in kwargs
        assert kwargs["skip"] == 0
        assert "limit" in kwargs
        assert kwargs["limit"] == 20
        return [fake_data.FAKE_JOB]
    mock_jobs_service.get_items_order_by = mock_get_items_order_by
    response = testclient_with_session.get("/api/jobs/check")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    first = payload[0]
    assert JobMin(**first) == JobMin.from_orm(fake_data.FAKE_JOB)


def test_check_jobs_with_status_id(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)
    response = testclient_with_session.get("/api/jobs/check?status_id=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    first = payload[0]
    assert JobMin(**first) == JobMin.from_orm(fake_data.FAKE_JOB)

    response = testclient_with_session.get("/api/jobs/check?status_id=3")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 0


def test_check_jobs_with_job_type(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)
    response = testclient_with_session.get("/api/jobs/check?job_type_id=3")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    first = payload[0]
    assert JobMin(**first) == JobMin.from_orm(fake_data.FAKE_JOB)

    response = testclient_with_session.get("/api/jobs/check?job_type_id=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 0


def test_get_job(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)
    response = testclient_with_session.get("/api/jobs/1")
    assert response.status_code == 200
    payload = response.json()
    assert Job(**payload) == Job.from_orm(fake_data.FAKE_JOB)


def test_create_job(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)
    response = testclient_with_session.post("/api/jobs/", json={
        "status_id": "1",
        "job_type_id": "3",
        "version": "test",
        "worker_version": "",
        "repository": {
            "name": "test",
            "owner": "test"
        },
        "book": "test"
    })
    assert response.status_code == 200
    payload = response.json()
    assert Job(**payload) == Job.from_orm(fake_data.FAKE_JOB)
