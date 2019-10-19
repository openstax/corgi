import Vuex from 'vuex'
import mutations from '@/store/mutations.js'
// import _ from 'lodash'

const createStore = () => {
  return new Vuex.Store({
    state: {
      events: []
    },
    getters: {
      // no getters yet
    },
    mutations,
    actions: {
      async nuxtServerInit ({ dispatch }, { req }) {
        await dispatch('getEvents')
      },
      async getEvents ({ commit }) {
        const data = await this.$axios.$get('/api/events/')
        // if (data.hasOwnProperty('collection_id')) {
        commit('REFRESH_EVENTS', data)
        // }
      }
    }
  })
}

export default createStore
