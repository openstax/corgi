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
            <v-btn color="primary" class="mb-3" dark v-on="on">Create a new PDF job</v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="headline">Create a new PDF</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12" sm="6" md="6">
                    <v-text-field
                      v-model="collectionId"
                      label="Collection ID"
                      hint="e.g. test-20191021-1"
                      required
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-container>
              <small>*indicates required field</small>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
              <v-btn color="blue darken-1" text @click="clickCollection(collectionId)">Do it!</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>

      <v-data-table
        :headers="headers"
        :items="events"
        :disable-pagination="true"
        :hide-default-footer="true"
        class="elevation-1"
      ></v-data-table>

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
        { text: 'Start Date and Time', value: 'created_at' },
        { text: 'Download URL', value: 'pdf_url' },
        { text: 'Status', value: 'status_name' },
        { text: 'Updated at', value: 'updated_at' }
      ],
      dialog: false,
      collectionId: '',
      polling: null
    }
  },
  computed: {
    events () {
      return this.$store.state.events
    }
  },
  methods: {
    pollData () {
      this.polling = setInterval(() => {
        this.$store.dispatch('getEvents')
        console.log('get EVENTS now...')
      }, 30000)
    },
    clickCollection (collectionId) {
      this.dialog = false
      if (collectionId.length >= 0) {
        console.log('POSTing ' + collectionId + ' now!')
        this.submitCollection(this.collectionId)
      }
    },
    async submitCollection (collectionId) {
      try {
        const data = {
          collection_id: collectionId,
          status_id: 1,
          pdf_url: null
        }
        await this.$axios.$post('/api/events/', data)
      } catch (error) {
        console.log(error)
      }
    }
  },
  beforeDestroy () {
    clearInterval(this.polling)
  },
  created () {
    this.pollData()
  }
}

</script>
