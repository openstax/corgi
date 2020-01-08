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
        <v-dialog v-model="dialog" persistent max-width="800px">
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" color="primary" class="mb-3" dark>
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
                  <v-col cols="12" sm="3" md="3">
                    <v-text-field
                      v-model="collectionId"
                      label="Collection ID"
                      hint="e.g. col12345"
                      required
                    />
                  </v-col>
                  <v-col cols="12" sm="3" md="3">
                    <v-text-field
                      v-model="version"
                      label="Version"
                      hint="e.g. 19.2"
                      optional
                    />
                  </v-col>
                  <v-col cols="12" sm="3" md="3">
                    <v-text-field
                      v-model="style"
                      label="Style"
                      hint="e.g. microbiology"
                      optional
                    />
                  </v-col>
                  <v-col cols="12" sm="3" md="3">
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
              <v-btn @click="dialog = false" color="blue darken-1" text>
                Cancel
              </v-btn>
              <v-btn @click="clickCollection(collectionId, contentServerId, version, style)" color="blue darken-1" text>
                Do it!
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
      <v-data-table
        :headers="headers"
        :items="jobs"
        :disable-pagination="true"
        :hide-default-footer="true"
        :sort-by="'updated_at'"
        :sort-desc="true"
        class="elevation-1"
      >
        <template v-slot:item.created_at="{ item }">
          <span>
            {{ $moment.utc(item.created_at).local().format('lll') }}
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
              size="12"
              color="green"
              indeterminate
              class="ml-2"
            />
          </v-chip>
        </template>
        <template v-slot:item.updated_at="{ item }">
          <span>
            {{ $moment.utc(item.updated_at).local().format('lll') }}
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
        { text: 'Style', value: 'style' },
        { text: 'Start Date and Time', value: 'created_at' },
        { text: 'Download URL', value: 'pdf_url' },
        { text: 'Status', value: 'status_name' },
        { text: 'Content Server', value: 'content_server_name' },
        { text: 'Updated at', value: 'updated_at' }
      ],
      dialog: false,
      collectionId: '',
      version: '',
      style: '',
      polling: null,
      contentServerId: null
    }
  },
  computed: {
    jobs () {
      return this.$store.state.jobs
    },
    content_servers () {
      return this.$store.getters.content_servers_items
    }
  },
  created () {
    this.pollData()
  },
  beforeDestroy () {
    clearInterval(this.polling)
  },
  methods: {
    pollData () {
      this.polling = setInterval(() => {
        this.$store.dispatch('getJobs')
        console.log('get JOBS now...')
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
    clickCollection (collectionId, contentServerId, version, style) {
      this.dialog = false
      if (collectionId.length >= 0) {
        console.log('POSTing ' + collectionId + ' now!')
        this.submitCollection(collectionId, contentServerId, version, style)
      }
    },
    async submitCollection (collectionId, contentServerId, version, astyle) {
      try {
        const data = {
          collection_id: collectionId,
          status_id: 1,
          pdf_url: null,
          version: version || null,
          style: astyle,
          content_server_id: contentServerId
        }
        await this.$axios.$post('/api/jobs/', data)
      } catch (error) {
        console.log(error)
      }
    }
  }
}

</script>
