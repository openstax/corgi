import { derived, Writable, Readable, writable } from "svelte/store";
import { getJobs } from "./jobs";
import { SECONDS } from "./time";
import type { Job, JobType, RepositorySummary } from "./types";
import { fetchRepoSummaries, isJobComplete, parseDateTimeAsUTC } from "./utils";

type GConstructor<T = {}> = new (...args: any[]) => T;
type Updatable = GConstructor<{ update: () => Promise<void> }>;
type ErrorWithDate = { date: Date; error: string };

// class APIStore<T> {
//   private fetching = false;

//   constructor(
//     protected readonly baseStore: Writable<T>,
//     private readonly fetchValue: () => Promise<T>,
//     public readonly subscribe = baseStore.subscribe
//   ) {}

//   async update() {
//     if (this.fetching) {
//       return;
//     }
//     try {
//       this.fetching = true;
//       this.baseStore.set(await this.fetchValue());
//     } catch (e) {
//       errorStore.add(e.toString());
//     } finally {
//       this.fetching = false;
//     }
//   }
// }

type Updater<T> = (value: T) => Promise<T>;

interface AsyncWritable<T> extends Readable<T> {
  /**
   * Set value and inform subscribers.
   * @param value to set
   */
  set(this: void, value: T): void;

  /**
   * Update value using callback and inform subscribers.
   * @param updater callback
   */
  update(this: void, updater: Updater<T>): void;
}

const asyncWritable = (value) => {
  const { set, subscribe } = writable(value);
  function intersetpt(newValue) {
    value = newValue;
    set(newValue);
  }
  function update(fn) {
    fn(value).then((newValue) => intersetpt(newValue));
  }
  return {
    set: intersetpt,
    subscribe,
    update,
  };
};

class APIStore<T> {
  private fetching = false;

  constructor(
    protected readonly baseStore: AsyncWritable<T>,
    private readonly fetchValue: (value: T) => Promise<T>,
    public readonly subscribe = baseStore.subscribe
  ) {}

  async update() {
    if (this.fetching) {
      return;
    }
    try {
      this.fetching = true;
      this.baseStore.update(this.fetchValue);
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
))(asyncWritable([]), fetchRepoSummaries);

export const jobsStore = new (Pollable(RateLimited(APIStore<Job[]>, 3)))(
  asyncWritable([]),
  async (jobs) => {
    // if there are no jobs get all jobs
    if (jobs.length === 0) {
      return await getJobs();
    }

    // if there are jobs get the oldest job that was created in the last 24 hours
    const searchRangeStartTimestamp = Date.now() - 86400000; // yesterday

    let oldestJobInSearchRangeIndex = 0;

    for (let i = jobs.length - 1; i > 0; i--) {
      const j = jobs[i];
      console.log(parseDateTimeAsUTC(j.updated_at));
      if (parseDateTimeAsUTC(j.updated_at) < searchRangeStartTimestamp) {
        oldestJobInSearchRangeIndex = i;
        break;
      }
    }

    // search for the oldest running job in the search range
    let oldestRunningJobIndex = -1;

    for (let i = oldestJobInSearchRangeIndex; i < jobs.length; i++) {
      const j = jobs[i];
      if (!isJobComplete(j)) {
        oldestRunningJobIndex = i;
        break;
      }
    }

    let lastJob;

    console.log(oldestRunningJobIndex);
    if (oldestRunningJobIndex === -1) {
      lastJob = jobs[jobs.length - 1];
    } else {
      lastJob = jobs[oldestRunningJobIndex];
    }

    const rangeStart = parseDateTimeAsUTC(lastJob.created_at) / 1000;
    return jobs
      .slice(0, oldestRunningJobIndex)
      .concat(await getJobs(rangeStart));
  }
);
