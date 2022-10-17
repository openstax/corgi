export type Job = {
    id: number;
    status_id: string;
    job_type_id: string;
    version: string;
    worker_version: string;
    created_at: number;
    updated_at: number;
    status: Status;
    repository: Repository;
    job_type: JobType;
    user: User;
    books: Book[];
    pdf_url: string;
    error_message: string;
};

export type Status = {
    name: string;
    id: string;
};

export type Repository = {
    name: string;
    owner: string;
    id: string;
};

export type JobType = {
    name: string;
    display_name: string;
    id: string;
};

export type User = {
    name: string;
    avatar_url: string;
    id: string
};

export type Book = {
    slug: string;
    commit_id: string;
    edition: number;
    uuid: string;
    style: string;
};

export type ArtifactUrl = {
    slug: string;
    url: string;
};