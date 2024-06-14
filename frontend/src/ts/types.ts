export interface Job {
  id: string;
  status_id: string;
  job_type_id: string;
  version: string;
  git_ref: string;
  worker_version: string;
  created_at: string;
  updated_at: string;
  status: Status;
  repository: Repository;
  job_type: JobType;
  user: User;
  books: Book[];
  artifact_urls: ArtifactUrl[];
  error_message: string;
}

export interface Status {
  name: string;
  id: string;
}

export interface Repository {
  name: string;
  owner: string;
}

export interface JobType {
  name: string;
  display_name: string;
  id: string;
}

export interface User {
  name: string;
  avatar_url: string;
  id: string;
}

export interface Book {
  slug: string;
  commit_id: string;
  edition: number;
  uuid: string;
  style: string;
}

export interface ArtifactUrl {
  slug: string;
  url: string;
}

export interface RepositorySummary extends Repository {
  books: string[];
}

export interface ApprovedBook {
  uuid: string;
  code_version: string;
  commit_sha: string;
}

export interface ApprovedBookWithDate extends ApprovedBook {
  created_at: string;
  committed_at: string;
  repository_name: string;
  slug: string;
  consumer: string;
}

export enum FeatureName {
  makeRepoPublicOnApproval,
}

export interface Config {
  readonly stackName: string | undefined;
  isFeatureEnabled: (featureName: FeatureName) => boolean;
}
