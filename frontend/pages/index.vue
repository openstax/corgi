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
                    <v-select
                      :items="['Book1', 'Book2', 'Book3']"
                      label="Bookname*"
                      required
                    ></v-select>
                  </v-col>
                </v-row>
              </v-container>
              <small>*indicates required field</small>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
              <v-btn color="blue darken-1" text @click="dialog = false">Do it!</v-btn>
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
