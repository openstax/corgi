import flattenObject from '@/store/utils.js'

export const state = () => ({
  events: [],
  content_servers: []
})

export const mutations = {
  REFRESH_EVENTS: (state, value) => {
    state.events = value
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
        'text': item.hostname,
        'value': item.id
      })
    })
    return data
  }
}

export const actions = {
  async nuxtServerInit ({ dispatch }, { req }) {
    await dispatch('getEvents')
    await dispatch('getContentServers')
  },
  async getEvents ({ commit }) {
    const response = await this.$axios.$get('/api/events/')
    const data = []
    response.forEach(function (item) {
      data.push(flattenObject(item))
    })
    // if (data.hasOwnProperty('collection_id')) {
    commit('REFRESH_EVENTS', data)
    // }
  },
  async getContentServers ({ commit }) {
    const response = await this.$axios.$get('/api/content-servers')
    commit('REFRESH_CONTENT_SERVERS', response)
  }
}
