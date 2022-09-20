export type Job = {
    id: number;
    job_type: JobType;
    repo: string;
    book: string;
    version: string;
    style: string;
    created_at: number;
    elapsed: number;
    status: Status;
    pdf_url: string;
    worker_version: string;
};

export type Status = {
    name: string;
};

export type JobType = {
    name: string;
    display_name: string;
    id: string;
};