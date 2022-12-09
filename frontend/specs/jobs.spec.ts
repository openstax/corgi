import { expect, describe, it, jest, beforeEach } from '@jest/globals';
import { submitNewJob, abortJob } from '../src/ts/jobs'
import { repoToString } from '../src/ts/utils'
import { jobsStore } from '../src/ts/stores'

let mockFetch
beforeEach(() => {
    mockFetch = jest.fn().mockImplementation(() =>
    Promise.resolve({ status: 200 })
  )
  window.fetch = mockFetch as any
})
describe('submitNewJob', () => {
  [
    ['3', 'tiny-book', 'book-slug1', ''],
    ['4', 'tiny-book', 'book-slug1', 'main'],
    ['3', 'owner/repo', 'book', 'main'],
  ].forEach(args => {
    it(`calls fetch with the correct information -> ${args}`, () => {
      const [jobTypeId, repo, book, version] = args
      submitNewJob(jobTypeId, repo, book, version).then(() => {
        const url: string = (mockFetch.mock.lastCall as any[])[0] as string
        const options = (mockFetch.mock.lastCall as any[])[1]
        const body = JSON.parse(options.body)
        expect(options.method).toBe('POST')
        expect(options.headers['Content-Type']).toBe('application/json')
        expect(url).toBe('/api/jobs/')
        expect(body.status_id).toBe(1)
        expect(body.job_type_id).toBe(jobTypeId)
        expect(repoToString(body.repository)).toBe(repo)
        expect(body.book).toBe(!!book ? book : null)
        expect(body.version).toBe(!!version ? version : null)
      })
    })
  })
})
describe('abortJob', () => {
  it('calls fetch with the correct information', () => {
    const jobId = 1
    const mockUpdate = jest.fn()
    jobsStore.update = mockUpdate as any
    window.setTimeout = jest.fn().mockImplementation((fn: any, _) => {
      fn()
    }) as any
    abortJob(jobId).then(() => {
      const url: string = (mockFetch.mock.lastCall as any[])[0] as string
      const options = (mockFetch.mock.lastCall as any[])[1]
      const body = JSON.parse(options.body)
      expect(url).toBe(`/api/jobs/${jobId}`)
      expect(options.method).toBe('PUT')
      expect(body.status_id).toBe('6')
      expect(mockUpdate.mock.calls.length).toBe(1)
    })
  })
})
