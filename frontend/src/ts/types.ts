export interface Job {
    id: number
    status_id: string
    job_type_id: string
    version: string
    worker_version: string
    created_at: string
    updated_at: string
    status: Status
    repository: Repository
    job_type: JobType
    user: User
    books: Book[]
    pdf_url: string
    error_message: string
}

export interface Status {
    name: string
    id: string
}

export interface Repository {
    name: string
    owner: string
}

export interface JobType {
    name: string
    display_name: string
    id: string
}

export interface User {
    name: string
    avatar_url: string
    id: string
}

export interface Book {
    slug: string
    commit_id: string
    edition: number
    uuid: string
    style: string
}

export interface ArtifactUrl {
    slug: string
    url: string
}

export interface RepositorySummary extends Repository {
    books: string[]
}