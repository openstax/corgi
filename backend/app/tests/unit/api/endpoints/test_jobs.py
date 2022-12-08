import pytest

from app.data_models.models import Job, JobMin


@pytest.mark.unit
@pytest.mark.nondestructive
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


@pytest.mark.unit
@pytest.mark.nondestructive
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


@pytest.mark.unit
@pytest.mark.nondestructive
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


@pytest.mark.unit
@pytest.mark.nondestructive
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


@pytest.mark.unit
@pytest.mark.nondestructive
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


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_job_404(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    def mock_get(*_):
        return None
    mock_jobs_service.get = mock_get

    response = testclient_with_session.get("/api/jobs/2")
    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.nondestructive
def test_create_job(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    response = testclient_with_session.post(
        "/api/jobs/", data=Job.from_orm(fake_data.FAKE_JOB).json())
    assert response.status_code == 200
    payload = response.json()
    assert Job(**payload) == Job.from_orm(fake_data.FAKE_JOB)


@pytest.mark.unit
@pytest.mark.nondestructive
def test_update_job(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    response = testclient_with_session.put("/api/jobs/1", json={"status_id": 3})
    assert response.status_code == 200
    payload = response.json()
    updated_job = Job.from_orm(fake_data.FAKE_JOB)
    updated_job.status_id = "3"
    assert Job(**payload) == updated_job


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize("original_status_id", [4, 5, 6])
def test_update_job_ignore_status_id(
        original_status_id,
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    # GIVEN: a job with a status id in range [4, 6]
    def mock_get(*_args, **_kwargs):
        job = fake_data.FAKE_JOB
        job.status_id = original_status_id
        return job
    mock_jobs_service.get = mock_get

    # WHEN: the status_id is updated
    response = testclient_with_session.put("/api/jobs/1", json={"status_id": 3})
    assert response.status_code == 200
    payload = response.json()
    updated_job = Job.from_orm(fake_data.FAKE_JOB)

    # THEN: status_id should stay the same
    updated_job.status_id = str(original_status_id)
    assert Job(**payload) == updated_job


@pytest.mark.unit
@pytest.mark.nondestructive
def test_update_job_404(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    def mock_get(*_args, **_kwargs):
        return None
    mock_jobs_service.get = mock_get
    response = testclient_with_session.put("/api/jobs/1", json={"status_id": 3})
    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_job_error(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    response = testclient_with_session.get("/api/jobs/error/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload == ""


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_job_error_404(
        monkeypatch,
        testclient_with_session,
        mock_jobs_service,
        fake_data):
    monkeypatch.setattr(
        "app.api.endpoints.jobs.jobs_service",
        mock_jobs_service)

    def mock_get(*_args, **_kwargs):
        return None
    mock_jobs_service.get = mock_get

    response = testclient_with_session.get("/api/jobs/error/1")
    assert response.status_code == 404
