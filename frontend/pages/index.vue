<template>
  <v-row justify="center">
    <v-col
      cols="12"
      md="10"
      class="mainscreen"
    >
      <v-row justify="space-between">
        <div class="d-md-flex">
          <v-btn
            class="ma-1"
            @click="toPage(Math.max(0, current_page - 1))"
          >
            Previous Page
          </v-btn>
          <v-btn
            class="ma-1"
            @click="toPage(current_page + 1)"
          >
            Next Page
          </v-btn>
          <v-text-field
            v-model="goto_page"
            class="ma-1"
            style="max-width: 100px"
            label="Page"
            outlined
            dense
            hide-details
          />
          <v-text-field
            v-model="goto_page_limit"
            class="ma-1"
            style="max-width: 100px"
            label="Jobs"
            outlined
            dense
            hide-details
          />
          <v-btn
            class="ma-1"
            @click="doPageGo()"
          >
            Go
          </v-btn>
        </div>
        <v-dialog v-model="dialog" persistent max-width="800px">
          <template #activator="{ on }">
            <v-btn
              color="primary"
              class="mb-3 create-job-button"
              dark
              large
              tile
              v-on="on"
            >
              <span>Create a new job</span>
              <v-icon class="ml-2">
                mdi-file-document-box-plus-outline
              </v-icon>
            </v-btn>
          </template>
          <v-card class="job-modal">
            <v-card-title class="headline grey lighten-2" primary-title>
              <v-icon class="mr-1" large>
                mdi-file-document-box-plus-outline
              </v-icon>
              <span>Create a new job</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-form ref="form" v-model="valid" lazy-validation>
                  <v-row>
                    <v-radio-group v-model="jobType" row mandatory :default="jobTypes.PDF" @change="resetFormValidation">
                      <v-radio label="PDF" :value="jobTypes.PDF" class="pdf-radio-button" />
                      <v-radio label="Web Preview" :value="jobTypes.DIST_PREVIEW" class="preview-radio-button" />
                      <v-radio label="PDF (git)" :value="jobTypes.GIT_PDF" class="git-pdf-radio-button" />
                      <v-radio label="Web Preview (git)" :value="jobTypes.GIT_DIST_PREVIEW" class="git-preview-radio-button" />
                    </v-radio-group>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="3" md="3">
                      <v-text-field
                        v-model="collectionId"
                        :rules="activeJobIsUsingArchive ? collectionRules : gitCollectionRules"
                        label="Collection ID"
                        class="collection-id-error-text collection-id-incorrect-error-text collection-id-field"
                        :hint="activeJobIsUsingArchive ? 'e.g. col12345' : 'e.g. repo-name/slug-name'"
                        required
                      />
                    </v-col>
                    <v-col cols="12" sm="3" md="3">
                      <v-text-field
                        v-model="version"
                        label="Version"
                        class="version-field"
                        :hint="activeJobIsUsingArchive ? 'e.g. 19.2' : 'e.g. master or a git tag'"
                        optional
                      />
                    </v-col>
                    <v-col cols="12" sm="3" md="3">
                      <v-combobox
                        v-model="style"
                        :rules="styleRules"
                        :items="styleItems"
                        hint="e.g. microbiology"
                        label="Style"
                        class="style-error-text style-field"
                        required
                      />
                    </v-col>
                    <v-col cols="12" sm="3" md="3">
                      <v-select
                        v-model="contentServerId"
                        :items="content_servers"
                        :rules="activeJobIsUsingArchive ? serverRules : []"
                        :disabled="!activeJobIsUsingArchive"
                        label="Content Server"
                        class="server-error-text server-field"
                        required
                      />
                    </v-col>
                  </v-row>
                </v-form>
              </v-container>
              <small>
                Hint: You can also edit the style field yourself
              </small>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn class="job-cancel-button" color="blue darken-1" text @click="closeDialog()">
                Cancel
              </v-btn>
              <v-btn class="create-button-start-job" color="blue darken-1" text @click="clickCollection(collectionId, maybeContentServerId, version, style, jobType)">
                Create
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-row>
      <v-row>
        <v-data-table
          v-if="browserReady"
          :headers="headers"
          :items="jobs"
          :disable-pagination="true"
          :hide-default-footer="true"
          class="elevation-1 jobs-table"
          show-expand
          single-expand="singleExpand"
          style="width:100%;"
          @click:row="(item, slot) => slot.expand(!slot.isExpanded)"
        >
          <template #expanded-item="{ headers, item }">
            <td :colspan="headers.length">
              <v-row>
                <v-col style="padding:2rem;">
                  <v-row style="margin:0;">
                    <h3 class="ma-2 text-uppercase">
                      Job Details
                    </h3>
                  </v-row>
                  <v-row
                    class="job-controls"
                  >
                    <v-col>
                      <v-divider />
                      <v-subheader>Utility</v-subheader>
                      <v-btn
                        class="job-repeat-button ma-2"
                        color="yellow darken-2"
                        outlined
                        @click="submitCollection(item.collection_id, item.content_server_id, item.version, item.style, item.job_type_id)"
                      >
                        Repeat
                      </v-btn>
                      <v-tooltip top>
                        <template #activator="{ on, attrs }">
                          <v-btn class="job-abort-button ma-2" color="red darken-1" outlined v-bind="attrs" v-on="on">
                            Abort
                          </v-btn>
                        </template>
                        <span>Not yet implemented!</span>
                      </v-tooltip>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col class="job-error-message">
                      <v-divider />
                      <v-subheader>Errors</v-subheader>
                      <kbd v-if="item.error_message" class="d-block my-2" style="white-space:pre;">{{ item.error_message }}</kbd>
                      <p v-else>
                        No errors to display.
                      </p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </td>
          </template>
          <template #item.created_at="{ item }">
            <span>
              {{ $moment.utc(item.created_at).local().format('lll') }}
            </span>
          </template>
          <template #item.pdf_url="{ item }">
            <ul
              style="list-style:none; padding:0;"
            >
              <li
                v-for="entry in getUrlEntries(item.pdf_url)"
                :key="entry.text"
              >
                <a
                  :href="entry.href"
                  target="_blank"
                >
                  {{ entry.text }}
                </a>
              </li>
            </ul>
          </template>
          <template #item.status_name="{ item }">
            <v-chip :color="getStatusColor(item.status_name)" dark>
              <span :class="{ 'font-weight-bold' : showStatus(item.status_name)}">
                {{ item.status_name }}
              </span>
              <v-progress-circular
                v-if="showStatus(item.status_name)"
                :width="3"
                size="12"
                color="white"
                indeterminate
                class="ml-2"
              />
            </v-chip>
          </template>
          <template #item.updated_at="{ item }">
            <span>
              {{ $moment.utc(item.updated_at).local().format('lll') }}
            </span>
          </template>
        </v-data-table>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>

export default {
  data () {
    return {
      dialog: false,
      collectionId: '',
      version: '',
      style: '',
      jobType: this.jobTypes.PDF,
      polling: null,
      contentServerId: null,
      browserReady: false,
      current_page: 0,
      goto_page: '0',
      page_limit: 50,
      goto_page_limit: '50',
      valid: false,
      lastJobStartTime: Date.now()
    }
  },
  computed: {
    jobs () {
      return this.$store.state.jobs
    },
    content_servers () {
      return this.$store.getters.content_servers_items
    },
    maybeContentServerId () {
      return this.activeJobIsUsingArchive ? this.contentServerId : null
    },
    activeJobIsUsingArchive () {
      return [1, 2].includes(this.jobType)
    }
  },
  // Init non-reactive data
  beforeCreate () {
    this.jobStartRateLimitDurationMillis = 1000
    this.styleItems = [
      'accounting',
      'additive-manufacturing',
      'american-government',
      'anatomy',
      'ap-biology',
      'ap-history',
      'ap-physics',
      'astronomy',
      'biology',
      'business-ethics',
      'calculus',
      'chemistry',
      'college-success',
      'dev-math',
      'economics',
      'entrepreneurship',
      'history',
      'hs-physics',
      'intro-business',
      'microbiology',
      'college-physics',
      'pl-u-physics',
      'precalculus',
      'precalculus-coreq',
      'principles-management',
      'psychology',
      'sociology',
      'statistics',
      'u-physics'
    ]
    this.styleItems.sort()
    this.collectionRules = [
      v => !!v || 'Collection ID is required',
      v => /^col\d*$/.test(v) || 'A valid collection ID is required, e.g. col12345'
    ]
    this.styleRules = [v => !!v || 'Style is required']
    this.serverRules = [v => !!v || 'Please select a server']
    this.gitCollectionRules = [
      v => !!v || 'Repo and slug are required',
      v => /[a-zA-Z0-9-_]+\/[a-zA-Z0-9-_]+/.test(v) || 'A valid repo and slug name is required, e.g. repo-name/slug-name'
    ]
    this.headers = [
      {
        text: 'Job ID',
        align: 'left',
        sortable: true,
        value: 'id'
      },
      { text: 'Job Type', value: 'job_type_display_name' },
      { text: 'Collection ID', value: 'collection_id' },
      { text: 'Version', value: 'version' },
      { text: 'Style', value: 'style' },
      { text: 'Start Date and Time', value: 'created_at' },
      { text: 'Download URL', value: 'pdf_url' },
      { text: 'Status', value: 'status_name' },
      { text: 'Content Server', value: 'content_server_name' },
      { text: 'Worker Version', value: 'worker_version' },
      { text: 'Updated at', value: 'updated_at' }
    ]
    // This value corresponds to the seeded id in the backend
    this.jobTypes = { PDF: 1, DIST_PREVIEW: 2, GIT_PDF: 3, GIT_DIST_PREVIEW: 4 }
    this.getUrlEntries = (input) => {
      if (input == null) {
        return []
      }
      try {
        return JSON.parse(input)
      } catch (err) {
        return [{ text: 'View', href: input.trim() }]
      }
    }
  },
  created () {
    this.getJobsImmediate()
    this.pollData()
  },
  mounted () {
    this.browserReady = true
  },
  beforeDestroy () {
    clearInterval(this.polling)
  },
  methods: {
    getJobsImmediate () {
      this.$store.dispatch('getJobsForPage', { page: this.current_page, limit: this.page_limit })
      console.log('get JOBS now...')
    },
    pollData () {
      this.polling = setInterval(() => {
        this.getJobsImmediate()
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
    resetFormValidation () {
      this.$refs.form.resetValidation()
    },
    closeDialog () {
      this.dialog = false
      this.$refs.form.resetValidation()
      this.$refs.form.reset()
    },
    doPageGo () {
      this.current_page = Math.max(0, parseInt(this.goto_page) || 0)
      this.page_limit = Math.max(0, parseInt(this.goto_page_limit) || 0)
      this.toPage(this.current_page)
    },
    toPage (number) {
      this.current_page = number
      this.goto_page = `${this.current_page}`
      this.goto_page_limit = `${this.page_limit}`
      this.getJobsImmediate()
    },
    clickCollection (collectionId, contentServerId, version, style, jobType) {
      if (this.$refs.form.validate()) {
        console.log('POSTing ' + collectionId + ' now!')
        this.submitCollection(collectionId, contentServerId, version, style, jobType)
        this.closeDialog()
      }
    },
    async submitCollection (collectionId, contentServerId, version, astyle, jobType) {
      // This fails to queue the job silently so the rate limit duration shouldn't
      // be a noticable time period for reasonable usage, else confusion will ensue
      if (this.lastJobStartTime + this.jobStartRateLimitDurationMillis > Date.now()) {
        return
      }
      this.lastJobStartTime = Date.now()
      try {
        const data = {
          collection_id: collectionId,
          status_id: 1,
          pdf_url: null,
          version: version || null,
          style: astyle,
          job_type_id: jobType,
          content_server_id: contentServerId
        }
        await this.$axios.$post('/api/jobs/', data)
        setTimeout(() => { this.getJobsImmediate() }, 1000)
      } catch (error) {
        console.log(error)
      }
    }
  }
}

</script>
