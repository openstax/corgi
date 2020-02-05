import flattenObject from '@/store/utils.js'

export const state = () => ({
  jobs: [],
  content_servers: []
})

export const mutations = {
  REFRESH_JOBS: (state, value) => {
    state.jobs = value
  },
  REFRESH_CONTENT_SERVERS: (state, value) => {
    state.content_servers = value
  }
}

export const getters = {
  content_servers (state) {
    return state.content_servers
  },
  content_servers_items (state) {
    const data = []
    state.content_servers.forEach(function (item) {
      data.push({
        'text': item.name,
        'value': item.id
      })
    })
    return data
  }
}

export const actions = {
  async nuxtServerInit ({ dispatch }, { req }) {
    await dispatch('getJobsForPage', { page: 0, limit: 50 })
    await dispatch('getContentServers')
  },
  async getJobsForPage ({ commit }, { page, limit }) {
    const response = await this.$axios.$get(`/api/jobs/pages/${page}?limit=${limit}`)
    const data = []
    response.forEach(function (item) {
      data.push(flattenObject(item))
    })
    // if (data.hasOwnProperty('collection_id')) {
    commit('REFRESH_JOBS', data)
    // }
  },
  async getContentServers ({ commit }) {
    const response = await this.$axios.$get('/api/content-servers')
    commit('REFRESH_CONTENT_SERVERS', response)
  }
}
