import { derived, Writable, writable } from "svelte/store";
import { getJobs } from "./jobs";
import { SECONDS } from "./time";
import type { Job, RepositorySummary } from "./types";
import { fetchRepoSummaries } from "./utils";

type GConstructor<T = {}> = new (...args: any[]) => T;
type Updatable = GConstructor<{ update: () => Promise<void> }>;
type ErrorWithDate = { date: Date; error: string };

class APIStore<T> {
  private fetching = false;

  constructor(
    protected readonly baseStore: Writable<T>,
    private readonly fetchValue: () => Promise<T>,
    public readonly subscribe = baseStore.subscribe
  ) {}

  async update() {
    if (this.fetching) {
      return;
    }
    try {
      this.fetching = true;
      this.baseStore.set(await this.fetchValue());
    } catch (e) {
      errorStore.add(e.toString());
    } finally {
      this.fetching = false;
    }
  }
}

const RateLimited = <T extends Updatable>(Base: T, timeoutSeconds: number) =>
  class extends Base {
    private readonly timeout = timeoutSeconds * SECONDS;
    private nextUpdate = 0;

    public override update = async () => {
      const now = Date.now();
      if (now > this.nextUpdate) {
        await super.update();
        this.nextUpdate = now + this.timeout;
      }
    };

    public updateImmediate = super.update;

    public clearLimit() {
      this.nextUpdate = 0;
    }
  };

const Pollable = <T extends Updatable>(Base: T) =>
  class extends Base {
    private polling = undefined;

    startPolling(interval: number, force: boolean = false) {
      if (this.polling !== undefined) {
        if (force) {
          clearInterval(this.polling);
        } else {
          throw new Error("Polling already running");
        }
      }
      this.polling = setInterval(() => void this.update(), interval);
    }

    stopPolling() {
      if (this.polling === undefined) {
        throw new Error("Polling is not running");
      }
      clearInterval(this.polling);
      this.polling = undefined;
    }
  };

const baseErrorStore = (() => {
  const { subscribe, set } = writable([] as ErrorWithDate[]);
  const errors: ErrorWithDate[] = [];
  return {
    subscribe,
    add: (err: string) => {
      // Do not report the same error multiple times in a row
      if (errors[0]?.error !== err) {
        errors.unshift({ date: new Date(), error: err });
        set(errors);
      }
    },
    clear: () => {
      errors.splice(0);
      set(errors);
    },
  };
})();

export const errorStore = (() => {
  const { subscribe } = derived(baseErrorStore, (errors) =>
    errors.map((e) => `${e.date.toLocaleTimeString()} - ${e.error}`)
  );
  // NOTE: The order is important here because we want to override `subscribe`
  return {
    ...baseErrorStore,
    subscribe,
  };
})();

export const repoSummariesStore = new (RateLimited(
  APIStore<RepositorySummary[]>,
  3
))(writable([]), fetchRepoSummaries);
export const jobsStore = new (Pollable(RateLimited(APIStore<Job[]>, 3)))(
  writable([]),
  getJobs
);
