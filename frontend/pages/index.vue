<template>
  <v-layout
    column
    justify-center
    align-center
    class="mainscreen"
  >
    <v-flex
      xs12
      sm8
      md8
    >
      <div class="text-right">
        <v-dialog v-model="dialog" persistent max-width="600px">
          <template v-slot:activator="{ on }">
            <v-btn color="primary" class="mb-3" dark v-on="on">
              Create a new PDF job
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="headline">Create a new PDF</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12" sm="4" md="4">
                    <v-text-field
                      v-model="collectionId"
                      label="Collection ID"
                      hint="e.g. col12345"
                      required
                    />
                  </v-col>
                  <v-col cols="12" sm="4" md="4">
                    <v-text-field
                      v-model="version"
                      label="Version"
                      hint="19.2"
                      optional
                    />
                  </v-col>
                  <v-col cols="12" sm="4" md="4">
                    <v-select
                      v-model="contentServerId"
                      :items="content_servers"
                      label="Content Server"
                      required
                    />
                  </v-col>
                </v-row>
              </v-container>
              <small>*indicates required field</small>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn color="blue darken-1" text @click="dialog = false">
                Cancel
              </v-btn>
              <v-btn color="blue darken-1" text @click="clickCollection(collectionId, contentServerId, version)">
                Do it!
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
      <v-data-table
        :headers="headers"
        :items="events"
        :disable-pagination="true"
        :hide-default-footer="true"
        :sort-by="'updated_at'"
        :sort-desc="true"
        class="elevation-1"
      >
        <template v-slot:item.created_at="{ item }">
          <span>
            {{ $moment.utc(item.created_at).format('MMM DD YYYY HH:mm:ss z') }}
          </span>
        </template>
        <template v-slot:item.pdf_url="{ item }">
          <a
            :href="item.pdf_url"
            target="_blank"
          >
            {{ item.pdf_url }}
          </a>
        </template>
        <template v-slot:item.status_name="{ item }">
          <v-chip :color="getStatusColor(item.status_name)" dark>
            {{ item.status_name }}
            <v-progress-circular
              v-if="showStatus(item.status_name)"
              :width="3"
              size=12
              color="green"
              indeterminate
              class="ml-2"
            />
          </v-chip>
        </template>
        <template v-slot:item.updated_at="{ item }">
          <span>
            {{ $moment.utc(item.updated_at).format('MMM DD YYYY HH:mm:ss z') }}
          </span>
        </template>
      </v-data-table>
    </v-flex>
  </v-layout>
</template>

<script>

export default {
  data () {
    return {
      headers: [
        {
          text: 'Job ID',
          align: 'left',
          sortable: true,
          value: 'id'
        },
        { text: 'Collection ID', value: 'collection_id' },
        { text: 'Version', value: 'version' },
        { text: 'Start Date and Time', value: 'created_at' },
        { text: 'Download URL', value: 'pdf_url' },
        { text: 'Status', value: 'status_name' },
        { text: 'Content Server', value: 'content_server_name' },
        { text: 'Updated at', value: 'updated_at' }
      ],
      dialog: false,
      collectionId: '',
      polling: null,
      contentServerId: null
    }
  },
  computed: {
    events () {
      return this.$store.state.events
    },
    content_servers () {
      return this.$store.getters.content_servers_items
    }
  },
  methods: {
    created () {
      this.pollData()
    },
    beforeDestroy () {
      clearInterval(this.polling)
    },
    pollData () {
      this.polling = setInterval(() => {
        this.$store.dispatch('getEvents')
        console.log('get EVENTS now...')
      }, 30000)
    },
    showStatus (status) {
      return (status === 'assigned' || status === 'processing')
    },
    getStatusColor (status) {
      if (status === 'failed') {
        return 'red'
      } else if (status === 'assigned') {
        return 'lightgrey'
      } else if (status === 'processing') {
        return 'orange'
      } else if (status === 'completed') {
        return 'green'
      } else {
        return 'grey'
      }
    },
    clickCollection (collectionId, contentServerId, version) {
      this.dialog = false
      if (collectionId.length >= 0) {
        console.log('POSTing ' + collectionId + ' now!')
        this.submitCollection(this.collectionId, this.contentServerId, this.version)
      }
    },
    async submitCollection (collectionId, contentServerId, version) {
      try {
        const data = {
          collection_id: collectionId,
          status_id: 1,
          pdf_url: null,
          version: version || null,
          content_server_id: contentServerId
        }
        await this.$axios.$post('/api/events/', data)
      } catch (error) {
        console.log(error)
      }
    }
  }
}

</script>
